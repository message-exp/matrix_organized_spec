# 5. PDUs

- [5. PDUs](#5-pdus)
  - [5.1 Checks performed on receipt of a PDU](#51-checks-performed-on-receipt-of-a-pdu)
    - [5.1.1 Definitions](#511-definitions)
    - [5.1.2 Authorization rules](#512-authorization-rules)
      - [5.1.2.1 Auth events selection](#5121-auth-events-selection)
    - [5.1.3 Rejection](#513-rejection)
    - [5.1.4 Soft failure](#514-soft-failure)
    - [5.1.5 Retrieving event authorization information](#515-retrieving-event-authorization-information)

每個 PDU（持久數據單元）包含一個起始伺服器希望發送到目標伺服器的房間事件。

- **`prev_events` 字段**：
  - 標識事件的“父”事件
  - 將事件鏈接成有向無環圖（DAG）
  - 在房間內建立事件的部分排序
  - 發送伺服器應將這個字段填充為所有尚未有子事件的事件，以表明該事件在所有已知事件之後發生。

例子

考慮一個房間，其事件形成了下圖所示的 DAG。一個伺服器在這個房間中創建一個新事件時，應將新事件的 `prev_events` 字段填充為 `E4` 和 `E6`，因為這兩個事件都還沒有子事件：

```text
E1
^
|
E2 <--- E5
^       ^
|       |
E3      E6
^
|
E4
```

有關 PDU 的完整模式，請參見 [房間版本規範](https://spec.matrix.org/v1.11/rooms)。

## 5.1 Checks performed on receipt of a PDU

每當伺服器接收到來自遠程伺服器的事件時，接收伺服器必須確保該事件：

1. 是有效事件，否則丟棄。
   - 有效事件必須包含 `room_id`，並符合該 [房間版本](https://spec.matrix.org/v1.11/rooms) 的事件格式。
2. 通過簽名檢查，否則丟棄。
3. 通過哈希檢查，否則在進一步處理前被編輯。
4. 通過基於事件中授權事件的授權規則，否則拒絕。
5. 通過基於事件前狀態的授權規則，否則拒絕。
6. 通過基於房間當前狀態的授權規則，否則“軟失敗”。

這些檢查的詳細信息以及如何處理失敗在後續部分中進行了描述。

[簽名事件](#signing-events) 部分提供了有關事件中期望的哈希和簽名以及如何計算它們的更多信息。

### 5.1.1 Definitions

所需權限等級（Required Power Level）

每個事件類型都有一個相關聯的*所需權限等級*。
這個等級由當前的 [`m.room.power_levels`](https://spec.matrix.org/v1.11/client-server-api/#mroompower_levels) 事件給出。
事件類型要麼在 `events` 部分中明確列出，
要麼根據事件是否為狀態事件，分別由 `state_default` 或 `events_default` 給出。

邀請等級、踢出等級、封禁等級、編輯等級（Invite Level, Kick Level, Ban Level, Redact Level）

這些等級由當前 [`m.room.power_levels`](https://spec.matrix.org/v1.11/client-server-api/#mroompower_levels) 狀態中的 `invite`、`kick`、`ban` 和 `redact` 屬性給出。
如果未指定，邀請等級默認為0，踢出等級、封禁等級和編輯等級各自默認為50。

 目標用戶（Target User）

對於 [`m.room.member`](https://spec.matrix.org/v1.11/client-server-api/#mroommember) 狀態事件，
由於牽扯到用戶，
目標用戶由事件的 `state_key` 指定。

> **WARNING**
>
> 一些 [房間版本](https://spec.matrix.org/v1.11/rooms) 接受權限等級值表示為字符串而不是整數，這是為了向後兼容。家庭伺服器應採取合理的預防措施來防止用戶發送包含字符串值的新權限等級事件（例如，通過拒絕API請求），並且不得將默認權限等級填充為字符串值。

請參見 [房間版本規範](https://spec.matrix.org/v1.11/rooms) 以獲取更多信息。

### 5.1.2 Authorization rules

決定事件是否被授權的規則取決於一組狀態。
特定事件會根據不同的狀態集進行多次檢查，如上所述。
每個房間版本可能有不同的算法和規則。
詳細信息請參見[房間版本規範](https://spec.matrix.org/v1.11/rooms)。

#### 5.1.2.1 Auth events selection

PDU 的 `auth_events` 字段標識了一組授權發送者發送該事件的事件。
對於房間中的 `m.room.create` 事件，`auth_events` 為空；
對於其他事件，應包括以下房間狀態的subset：

- `m.room.create` 事件。
- 當前的 `m.room.power_levels` 事件（如果有）。
- 發送者當前的 `m.room.member` 事件（如果有）。
- 如果事件類型是 `m.room.member` ->
  - 目標用戶當前的 `m.room.member` 事件（如果有）。
  - 如果 `membership` = ( `join` or `invite` ) -> 當前的 `m.room.join_rules` 事件（如果有）。
  - 如果 `membership` = `invite` & `content` 包含 `third_party_invite` -> 
    - 當前的 `m.room.third_party_invite` 事件
    - `state_key` 匹配 `content.third_party_invite.signed.token`（如果有）。
  - 如果 `content.join_authorised_via_users_server` 存在，並且[房間版本支持受限房間](https://spec.matrix.org/v1.11/rooms/#feature-matrix)，則 `m.room.member` 事件，其 `state_key` 匹配 `content.join_authorised_via_users_server`。

### 5.1.3 Rejection

1. **事件被拒絕時**：
   - 不應轉發給客戶端。
   - 不應作為新事件的前一事件引用。

2. **其他伺服器引用被拒絕事件時**：
   - 只要這些後續事件仍通過授權規則，應允許它們存在。

3. **檢查中使用的狀態**：
   - 應正常計算。
   - 但不應更新被拒絕的事件（如果它是狀態事件）。

如果進來的交易中的一個事件被拒絕，這不應該導致交易請求回應錯誤。

這意味著，即使事件應該被拒絕，它們仍然可能被包含在房間的有向無環圖（DAG）中。

這與被編輯的事件不同，被編輯的事件仍然可以影響房間的狀態。例如，一個被編輯的 `join` 事件仍然會導致該用戶被視為已加入。


### 5.1.4 Soft failure



It is important that we prevent users from evading bans (or other power
 restrictions) by creating events which reference old parts of the DAG.
 For example, a banned user could continue to send messages to a room by
 having their server send events which reference the event before they
 were banned. Note that such events are entirely valid, and we cannot
 simply reject them, as it is impossible to distinguish such an event
 from a legitimate one which has been delayed. We must therefore accept
 such events and let them participate in state resolution and the
 federation protocol as normal. However, servers may choose not to send
 such events on to their clients, so that end users won’t actually see
 the events.


When this happens it is often fairly obvious to servers, as they can see
 that the new event doesn’t actually pass auth based on the “current
 state” (i.e. the resolved state across all forward extremities). While
 the event is technically valid, the server can choose to not notify
 clients about the new event.


This discourages servers from sending events that evade bans etc. in
 this way, as end users won’t actually see the events.



When the homeserver receives a new event over federation it should also
 check whether the event passes auth checks based on the current state of
 the room (as well as based on the state at the event). If the event does
 not pass the auth checks based on the *current state* of the room (but
 does pass the auth checks based on the state at that event) it should be
 “soft failed”.


When an event is “soft failed” it should not be relayed to the client
 nor be referenced by new events created by the homeserver (i.e. they
 should not be added to the server’s list of forward extremities of the
 room). Soft failed events are otherwise handled as usual.



 Soft failed events participate in state resolution as normal if further
 events are received which reference it. It is the job of the state
 resolution algorithm to ensure that malicious events cannot be injected
 into the room state via this mechanism.
 

 Because soft failed state events participate in state resolution as
 normal, it is possible for such events to appear in the current state of
 the room. In that case the client should be told about the soft failed
 event in the usual way (e.g. by sending it down in the `state` section
 of a sync response).
 

 A soft failed event should be returned in response to federation
 requests where appropriate (e.g. in `/event/<event_id>`). Note that soft
 failed events are returned in `/backfill` and `/get_missing_events`
 responses only if the requests include events referencing the soft
 failed events.
 
Example


As an example consider the event graph:



```
  A
 /
B

```

where `B` is a ban of a user `X`. If the user `X` tries to set the topic
 by sending an event `C` while evading the ban:



```
  A
 / \
B   C

```

servers that receive `C` after `B` should soft fail event `C`, and so
 will neither relay `C` to its clients nor send any events referencing
 `C`.
 


If later another server sends an event `D` that references both `B` and
 `C` (this can happen if it received `C` before `B`):
 



```
  A
 / \
B   C
 \ /
  D

```

then servers will handle `D` as normal. `D` is sent to the servers'
 clients (assuming `D` passes auth checks). The state at `D` may resolve
 to a state that includes `C`, in which case clients should also to be
 told that the state has changed to include `C`. (*Note*: This depends on
 the exact state resolution algorithm used. In the original version of
 the algorithm `C` would be in the resolved state, whereas in latter
 versions the algorithm tries to prioritise the ban over the topic
 change.)


Note that this is essentially equivalent to the situation where one
 server doesn’t receive `C` at all, and so asks another server for the
 state of the `C` branch.


Let’s go back to the graph before `D` was sent:



```
  A
 / \
B   C

```

If all the servers in the room saw `B` before `C` and so soft fail `C`,
 then any new event `D'` will not reference `C`:



```
  A
 / \
B   C
|
D'

```

### 5.1.5 Retrieving event authorization information


The homeserver may be missing event authorization information, or wish
 to check with other servers to ensure it is receiving the correct auth
 chain. These APIs give the homeserver an avenue for getting the
 information it needs.





<!-- markdownlint-disable -->
<h1>GET</h1> 
<!-- markdownlint-enable -->
/\_matrix/federation/v1/event\_auth/{roomId}/{eventId}





---


Retrieves the complete auth chain for a given event.




| Rate-limited: | No |
| --- | --- |
| Requires authentication: | Yes |




---


<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->


#<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable --> parameters




path parameters
| Name | Type | Description |
| --- | --- | --- |
| `eventId` | `string` | **Required:** The event ID to get the auth chain of. |
| `roomId` | `string` | **Required:** The room ID to get the auth chain for. |




---


<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->




| Status | Description |
| --- | --- |
| `200` | The auth chain for the event. |


<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->




| Name | Type | Description |
| --- | --- | --- |
| `auth_chain` | `[PDU]` | **Required:** The [PDUs](/v1.11/server-server-api/#pdus) forming the  auth chain  of the given event. The event format varies depending on the  room version - check the [room version specification](/v1.11/rooms)  for precise event formats. |




```
{
  "auth_chain": [
    {
      "content": {
        "see_room_version_spec": "The event format changes depending on the room version."
      },
      "room_id": "!somewhere:example.org",
      "type": "m.room.minimal_pdu"
    }
  ]
}

```
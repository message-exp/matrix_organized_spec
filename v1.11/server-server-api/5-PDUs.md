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

我們必須防止用戶通過創建引用DAG舊部分的事件來規避封禁（或其他權限限制）。

1. **被封禁的用戶行為**：
   - 透過他們的伺服器引用他們被封禁前的事件
     → 這樣他們可以繼續向房間發送消息。
   - 技術上是完全有效
     → 不能簡單地拒絕它們，因為無法區分這樣的事件和因延遲而合法的事件。
     => 接受這些事件
     → 正常參與狀態解析和聯邦協議
     → 伺服器可以選擇不將這些事件發送給客戶端
     → 用戶不會看到這些事件。

當這種情況發生時，
伺服器通常可以很容易地察覺，
因為他們可以看到新事件根據“當前狀態”（即所有前進端點的解析狀態）並未通過授權檢查。
雖然事件在技術上是有效的，
但伺服器可以選擇不通知客戶端關於這個新事件。

這樣可以阻止伺服器通過這種方式發送規避封禁的事件，
因為最終用戶實際上不會看到這些事件。

1. **事件檢查**：
   - 當家庭伺服器通過聯邦協議接收到新事件時，
     應檢查該事件是否通過基於房間當前狀態的授權檢查（以及基於事件狀態的檢查）。

2. **軟失敗標記**：
   - 如果事件未通過基於房間當前狀態的授權檢查，
     但通過了基於事件狀態的授權檢查，則應該將其標記為“軟失敗”。

3. **軟失敗事件處理**：
   - 當事件被標記為“軟失敗”時：
     - 不會被傳遞給客戶端。
     - 不會被新事件引用（即，它們不應該被添加到伺服器的房間前進端點列表中）。
     - 其他方面則按通常方式處理。

4. **軟失敗事件的影響**：
   - 如果後續事件引用了軟失敗的事件，這些事件將正常參與狀態解析。
   - 狀態解析算法的任務是確保惡意事件無法通過這種機制注入房間狀態。

5. **軟失敗事件通知客戶端**：
   - 由於軟失敗的狀態事件正常參與狀態解析，
     這些事件可能會出現在房間的當前狀態中，
     在這種情況下應按通常方式通知客戶端（例如，在同步響應的 `state` 部分中發送）。

6. **聯邦請求中的軟失敗事件**：
   - 在適當情況下，應該在聯邦請求（例如 `/event/<event_id>`）中返回軟失敗的事件。
   - 注意，只有在請求中包含引用了軟失敗事件的事件時，
     軟失敗事件才會在 `/backfill` 和 `/get_missing_events` 響應中返回。

**例子**
考慮以下事件圖：

```text
  A
 /
B
```

其中 `B` 是對用戶 `X` 的封禁。如果用戶 `X` 試圖通過發送事件 `C` 來設置主題，以規避封禁：

```text
  A
 / \
B   C
```

接收到 `C` 的伺服器應該將事件 `C` 標記為軟失敗，因此不會將 `C` 傳遞給客戶端，也不會發送任何引用 `C` 的事件。

如果稍後另一個伺服器發送了一個同時引用 `B` 和 `C` 的事件 `D`（這可能發生在它先接收到 `C` 而後接收到 `B` 的情況下）：

```text
  A
 / \
B   C
 \ /
  D
```

則伺服器將正常處理 `D`，並將其發送給客戶端（假設 `D` 通過授權檢查）。`D` 的狀態可能解析為包含 `C`，在這種情況下應通知客戶端狀態已更改以包含 `C`。（注意：這取決於使用的確切狀態解析算法。在原始算法中，`C` 會在解析狀態中，而在後來的版本中，算法試圖優先封禁而不是主題變更。）

這基本上等同於一個伺服器完全沒有接收到 `C`，因此請求另一個伺服器獲取 `C` 分支的狀態。

回到發送 `D` 之前的圖：

```text
  A
 / \
B   C
```

如果房間中的所有伺服器在 `C` 之前看到 `B`，並因此軟失敗 `C`，則任何新事件 `D'` 都不會引用 `C`：

```text
  A
 / \
B   C
|
D'
```

> 兩種圖是個能在不同伺服器中共存，雖然圖有些許不同，但呈現的結果是同步的

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
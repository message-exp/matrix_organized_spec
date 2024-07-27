# Leaving Rooms (Rejecting Invites)

- 類似加入房間的機制
- make_leave請求離開的事件模板
- send_leave正式發出離開
- GET /_matrix/federation/v1/make_leave/{roomId}/{userId}
  - 就是要求事件模板
- PUT /_matrix/federation/v1/send_leave/{roomId}/{eventId}
  - 這v1沒要用了看看就好
- PUT/_matrix/federation/v2/send_leave/{roomId}/{eventId}
  - 就是個傳送簽名過的離開事件

正常情況下，
主伺服器可以發送適當的 `m.room.member` 事件來讓用戶離開房間、拒絕本地邀請或撤回敲門。
來自其他主伺服器的遠程邀請/敲門不會涉及伺服器在圖中的位置，
因此需要另一種方法來拒絕邀請。
加入房間並立即離開並不建議，
因為客戶端和伺服器會將其解釋為接受邀請後又離開房間，
而不是拒絕邀請。

類似於[加入房間](/v1.11/server-server-api/10-Joining-Rooms.md)的握手過程，
希望離開房間的伺服器首先向駐留伺服器發送 `/make_leave` 請求。
在拒絕邀請的情況下，
駐留伺服器可能是發送邀請的伺服器。
收到 `/make_leave` 的模板事件後，
離開伺服器會簽署該事件並用自己的 `event_id` 替換原有的 `event_id`。
然後將其通過 `/send_leave` 發送給駐留伺服器。
駐留伺服器隨後會將事件發送給房間中的其他伺服器。

> 透過類似加入房間的方法，
> 先使用make_leave發出想要離開的請求，
> 確認好要發送的資訊後使用send_leave正式離開伺服器

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/make_leave/{roomId}/{userId}</a></h1> 
<!-- markdownlint-enable -->

請求接收伺服器返回發送伺服器需要準備離開房間事件的信息。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 即將離開的房間 ID。 |
| `userId` | `string` | **Required:** 離開事件的用戶 ID。 |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Status | Description |
| --- | --- |
| `200` | 用於調用 `/send_leave` 的模板。請注意，根據房間版本不同，事件格式也有所不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。**此處的響應體描述了常見的事件字段，並且可能缺少 PDU 所需的其他字段。** |
| `403` | 請求未授權。這可能意味著用戶不在房間內。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `event` | `[Event Template]` | 未簽名的模板事件。請注意，根據房間版本不同，事件格式也有所不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。 |
| `room_version` | `string` | 伺服器嘗試離開的房間版本。如果未提供，則房間版本默認為“1”或“2”。 |
<!-- markdownlint-enable -->

Event Template
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **Required:** 事件的內容。 |
| `origin` | `string` | **Required:** 駐留主伺服器的名稱。 |
| `origin_server_ts` | `integer` | **Required:** 駐留主伺服器添加的時間戳。 |
| `sender` | `string` | **Required:** 離開成員的用戶 ID。 |
| `state_key` | `string` | **Required:** 離開成員的用戶 ID。 |
| `type` | `string` | **Required:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `membership` | `string` | **Required:** 值為 `leave`。 |
<!-- markdownlint-enable -->

```json
{
  "event": {
    "content": {
      "membership": "leave"
    },
    "origin": "example.org",
    "origin_server_ts": 1549041175876,
    "room_id": "!somewhere:example.org",
    "sender": "@someone:example.org",
    "state_key": "@someone:example.org",
    "type": "m.room.member"
  },
  "room_version": "2"
}
```

<!-- markdownlint-disable -->
<h3>403 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
Error
| Name | Type | Description |
| --- | --- | --- |
| `errcode` | `string` | **Required:** 錯誤碼。 |
| `error` | `string` | 人類可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "User is not in the room."
}
```

---

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v1/send_leave/{roomId}/{eventId}</a></h1> 
<!-- markdownlint-enable -->

---

此 API 已棄用，將在未來版本中移除。

**注意:** 伺服器應優先使用 v2 `/send_leave` 端點。

提交已簽名的離開事件到駐留伺服器，
使其接受該事件進入房間的圖表。
請注意，
根據房間版本不同，
事件格式也有所不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。
**此處的請求和響應體描述了常見的事件字段，並且可能缺少 PDU 所需的其他字段。**

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `eventId` | `string` | **Required:** 離開事件的事件 ID。 |
| `roomId` | `string` | **Required:** 即將離開的房間 ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `content` | `[Membership Event Content](#put_matrixfederationv1send_leaveroomideventid_request_membership-event-content)` | **Required:** 事件的內容。 |
| `depth` | `integer` | **Required:** 該字段必須存在，但被忽略；它可以為 0。 |
| `origin` | `string` | **Required:** 離開主伺服器的名稱。 |
| `origin_server_ts` | `integer` | **Required:** 離開主伺服器添加的時間戳。 |
| `sender` | `string` | **Required:** 離開成員的用戶 ID。 |
| `state_key` | `string` | **Required:** 離開成員的用戶 ID。 |
| `type` | `string` | **Required:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `membership` | `string` | **Required:** 值為 `leave`。 |
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "leave"
  },
  "depth": 12,
  "origin": "matrix.org",
  "origin_server_ts": 1234567890,
  "sender": "@someone:example.org",
  "state_key": "@someone:example.org",
  "type": "m.room.member"
}
```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Status | Description |
| --- | --- |
| `200` | 空響應，表示事件已被接收伺服器接受進入圖表。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

Array of `integer, Empty Object`.

```json
[
  200,
  {}
]
```

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v2/send_leave/{roomId}/{eventId}</a></h1> 
<!-- markdownlint-enable -->

---

**注意:**
此 API 與 v1 API 幾乎相同，唯一的不同是修正了響應格式。

此端點優先於 v1 API，
因為它提供了更標準化的響應格式。
發送者如果收到 400、404 或其他狀態碼，
表明此端點不可用，
應改用 v1 API 重試。

提交已簽名的離開事件到駐留伺服器，
使其接受該事件進入房間的圖表。
請注意，
根據房間版本不同，
事件格式也有所不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。
**此處的請求和響應體描述了常見的事件字段，並且可能缺少 PDU 所需的其他字段。**

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `eventId` | `string` | **Required:** 離開事件的事件 ID。 |
| `roomId` | `string` | **Required:** 即將離開的房間 ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `content` | `[Membership Event Content](#put_matrixfederationv2send_leaveroomideventid_request_membership-event-content)` | **Required:** 事件的內容。 |
| `depth` | `integer` | **Required:** 該字段必須存在，但被忽略；它可以為 0。 |
| `origin` | `string` | **Required:** 離開主伺服器的名稱。 |
| `origin_server_ts` | `integer` | **Required:** 離開主伺服器添加的時間戳。 |
| `sender` | `string` | **Required:** 離開成員的用戶 ID。 |
| `state_key` | `string` | **Required:** 離開成員的用戶 ID。 |
| `type` | `string` | **Required:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `membership` | `string` | **Required:** 值為 `leave`。 |
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "leave"
  },
  "depth": 12,
  "origin": "matrix.org",
  "origin_server_ts": 1234567890,
  "sender": "@someone:example.org",
  "state_key": "@someone:example.org",
  "type": "m.room.member"
}
```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Status | Description |
| --- | --- |
| `200` | 空響應，表示事件已被接收伺服器接受進入圖表。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

```json
{}
```

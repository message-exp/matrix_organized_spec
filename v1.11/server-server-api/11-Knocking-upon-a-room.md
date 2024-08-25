# Knocking upon a room

- 另一種加入房間的方法叫敲門，簡單來說就是要審核的主動加入
- 一樣透過make_knock得到資訊，簽名候用send_knock來加入
- send過後成功會拿到一組房間狀態，按照這個狀態來連接房間

房間可以通過加入規則允許敲門，
如果允許，
這將為用戶提供一種請求加入（被邀請）房間的方式。
用戶在伺服器已經是該房間的駐留伺服器的情況下敲門，
只需直接發送敲門事件而不使用此過程，
然而，
與[加入房間](/v1.11/server-server-api/10-Joining-Rooms.md)類似，
伺服器必須通過握手過程來代表用戶發送敲門請求。

這個握手過程與加入房間的握手過程基本相同，
只是將“加入伺服器”替換為“敲門伺服器”，
並且要調用的API不同（`/make_knock` 和 `/send_knock`）。

伺服器可以通過離開房間來撤回敲門請求，
如下所述拒絕邀請。

> 敲門主要是主動申請加入房間->房間的管理員等審核後同意/拒絕
>
> 相較於敲門，一般加入就是例如公開房間就可以直接加入，私人房間(受限房間)就只能受邀的情況才能加入

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/make_knock/{roomId}/{userId}</a></h1>
<!-- markdownlint-enable -->

---

**新增於 `v1.1`**

請求接收伺服器返回發送伺服器需要準備敲門事件的資訊。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **必需:** 即將被敲門的房間ID。 |
| `userId` | `string` | **必需:** 敲門事件的用戶ID。 |
<!-- markdownlint-enable -->

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `ver` | `[string]` | **必需:** 發送伺服器支援的房間版本。 |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 用於[敲門房間](/v1.11/server-server-api/#knocking-rooms)握手過程的模板。請注意，根據房間版本的不同，事件格式會有所不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。**此處的響應內容描述了通用事件字段的更多詳細信息，並且可能缺少 PDU 的其他必需字段。** |
| `400` | 請求無效或伺服器嘗試敲門的房間版本未列在 `ver` 參數中。錯誤應傳遞給客戶端，以便客戶端可以為用戶提供更好的反饋。 |
| `403` | 敲門伺服器或用戶無權敲門房間，例如伺服器/用戶被禁或房間未設置為接受敲門。 |
| `404` | 敲門伺服器嘗試敲門的房間對接收伺服器未知。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event` | `[Event Template](#get_matrixfederationv1make_knockroomiduserid_response-200_event-template)` | **必需:** 未簽名的模板事件。請注意，根據房間版本的不同，事件格式會有所不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
| `room_version` | `string` | **必需:** 伺服器嘗試敲門的房間版本。 |
<!-- markdownlint-enable -->

事件模板
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **必需:** 事件的內容。 |
| `origin` | `string` | **必需:** 駐留家庭伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 駐留家庭伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 敲門成員的用戶ID。 |
| `state_key` | `string` | **必需:** 敲門成員的用戶ID。 |
| `type` | `string` | **必需:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `membership` | `string` | **必需:** 值為 `knock`。 |
<!-- markdownlint-enable -->

```json
{
  "event": {
    "content": {
      "membership": "knock"
    },
    "origin": "example.org",
    "origin_server_ts": 1549041175876,
    "room_id": "!somewhere:example.org",
    "sender": "@someone:example.org",
    "state_key": "@someone:example.org",
    "type": "m.room.member"
  },
  "room_version": "7"
}
```

<!-- markdownlint-disable -->
<h3>400 response</h3> 
<!-- markdownlint-enable -->

Error
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必需:** 錯誤碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |
| `room_version` | `string` | 房間的版本。如果 `errcode` 是 `M_INCOMPATIBLE_ROOM_VERSION`，則必需。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
```json
{
  "errcode": "M_INCOMPATIBLE_ROOM_VERSION",
  "error": "Your homeserver does not support the features required to knock on this room",
  "room_version": "7"
}
```
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>403 response</h3> 
<!-- markdownlint-enable -->

Error
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必需:** 錯誤碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "You are not permitted to knock on this room"
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3> 
<!-- markdownlint-enable -->

Error
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必需:** 錯誤碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Unknown room"
}
```

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v1/send_knock/{roomId}/{eventId}</a></h1>
<!-- markdownlint-enable -->

---

**新增於 `v1.1`**

提交已簽名的敲門事件給駐留伺服器，
讓其接受並加入房間的事件圖。
請注意，
根據房間版本的不同，
事件格式會有所不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。
**此處的請求和響應內容描述了通用事件字段的更多詳細信息，並且可能缺少 PDU 的其他必需字段。**

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `eventId` | `string` | **必需:** 敲門事件的事件ID。 |
| `roomId` | `string` | **必需:** 即將被敲門的房間ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content](#put_matrixfederationv1send_knockroomideventid_request_membership-event-content)` | **必需:** 事件的內容。 |
| `origin` | `string` | **必需:** 敲門家庭伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 敲門家庭伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 敲門成員的用戶ID。 |
| `state_key` | `string` | **必需:** 敲門成員的用戶ID。 |
| `type` | `string` | **必需:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

成員事件內容
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `membership` | `string` | **必需:** 值為 `knock`。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "knock"
  },
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

| 狀態 | 描述 |
| --- | --- |
| `200` | 關於房間的信息，用於向客戶端傳遞敲門狀態。 |
| `403` | 敲門伺服器或用戶無權敲門房間，例如伺服器/用戶被禁或房間未設置為接受敲門。 |
| `404` | 敲門伺服器嘗試敲門的房間對接收伺服器未知。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `knock_room_state` | `[StrippedStateEvent]` | **必需:** 一個[精簡狀態事件]( )的列表，幫助敲門請求的發起者識別房間。 |
<!-- markdownlint-enable -->

StrippedStateEvent
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `EventContent` | **必需:** 事件的 `content`。 |
| `sender` | `string` | **必需:** 事件的 `sender`。 |
| `state_key` | `string` | **必需:** 事件的 `state_key`。 |
| `type` | `string` | **必需:** 事件的 `type`。 |
<!-- markdownlint-enable -->

```json
{
  "knock_room_state": [
    {
      "content": {
        "name": "Example Room"
      },
      "sender": "@bob:example.org",
      "state_key": "",
      "type": "m.room.name"
    },
    {
      "content": {
        "join_rule": "knock"
      },
      "sender": "@bob:example.org",
      "state_key": "",
      "type": "m.room.join_rules"
    }
  ]
}
```

<!-- markdownlint-disable -->
<h3>403 response</h3> 
<!-- markdownlint-enable -->

Error
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必需:** 錯誤碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "You are not permitted to knock on this room"
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3> 
<!-- markdownlint-enable -->

Error
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必需:** 錯誤碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Unknown room"
}
```

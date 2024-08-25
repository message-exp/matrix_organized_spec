# Joining Rooms

- 加入自己homeserver的房間就自己檢查
- 加入別人要遠程加入握手
- Server分三種: 加入伺服器、目錄伺服器、駐留伺服器
- 目錄伺服器提供房間ID和server列表
- 駐留伺服器幫忙加入
- 目錄和駐留可能是同一個
- 被動邀請可不用查目錄，但要做好失敗的準備
- GET/_matrix/federation/v1/make_join/{roomId}/{userId}
  - 為了加入先確認加入要提供什麼
  - 提供要加入的房間ID、user id，以及支援的版本
  - 成功就200response，失敗就40X
- PUT/_matrix/federation/v2/send_join/{roomId}/{eventId}
  - 將剛才make_join的資料簽署後再發送
  - 把make_join的`origin`、`origin_server_ts` 和 `event_id`替換掉
- 加入房間後會簽名放進事件圖
- 傳送訊息給其他server
- 受限房間
  - 沒有提供足夠條件驗證就會400 `M_UNABLE_TO_AUTHORISE_JOIN`
  - 用戶滿足條件但駐留伺服器沒法驗證`m.room.member` 就會400 `M_UNABLE_TO_GRANT_JOIN`
  - 如果真的不給過就會403 `M_FORBIDDEN`

當一個新用戶希望加入其主伺服器已知的房間時，
主伺服器可以立即通過檢查房間的狀態來確定這是否允許。
如果可以接受，
則可以生成、簽名並發送一個新的 `m.room.member` 狀態事件，
將該用戶加入到該房間中。
但是，
如果主伺服器尚未了解該房間，
它不能直接這樣做。
相反，
它必須進行一個較長的多階段握手過程，
首先選擇一個已經參與該房間的遠程主伺服器，
並使用它來協助加入過程。這
就是遠程加入握手。

> 如果加入的是homeserver的房間就直接自己檢查就好，
> 但如果是別的伺服器就需要透過多階段握手，稱為遠程加入握手

此握手涉及希望加入的新成員的主伺服器（此處稱為“加入伺服器 JoiningServer”）、
托管用戶請求加入的房間別名的目錄伺服器(DirectoryServer)和已存在房間成員的主伺服器（稱為“駐留伺服器 ResidentServer”）。

總而言之，
遠程加入握手包括加入伺服器向目錄伺服器查詢房間別名信息，
接收房間 ID 和一個候選加入伺服器列表。
然後，
加入伺服器向其中一個駐留伺服器請求房間信息。
它使用這些信息來構建一個 `m.room.member` 事件，
並最終將其發送到駐留伺服器。

概念上，
這裡涉及到三種不同角色的主伺服器。
在實際操作中，
目錄伺服器很可能是房間中的駐留伺服器，
因此可以被加入伺服器選擇為協助的駐留伺服器。
同樣，
加入伺服器在事件構建的兩個階段中可能會選擇同一個候選駐留伺服器，
儘管原則上可以在每個時間點使用任何有效的候選伺服器。
因此，
任何一次加入握手可能涉及兩到四個主伺服器，
但實際操作中通常只使用兩個。

> 主要分為三種伺服器，
> 主動加入的加入伺服器、
> 查詢房間id以及提供候選加入伺服器列表的目錄伺服器、
> 協助加入的駐留伺服器。
> 雖然可以將這些伺服器分開來用不同的伺服器，
> 但實際上通常就兩個

```text
+---------+          +---------------+            +-----------------+ +-----------------+
| Client  |          | JoiningServer |            | DirectoryServer | | ResidentServer  |
+---------+          +---------------+            +-----------------+ +-----------------+
     |                       |                             |                   |
     | join request          |                             |                   |
     |---------------------->|                             |                   |
     |                       |                             |                   |
     |                       | directory request           |                   |
     |                       |---------------------------->|                   |
     |                       |                             |                   |
     |                       |          directory response |                   |
     |                       |<----------------------------|                   |
     |                       |                             |                   |
     |                       | make_join request           |                   |
     |                       |------------------------------------------------>|
     |                       |                             |                   |
     |                       |                             |make_join response |
     |                       |<------------------------------------------------|
     |                       |                             |                   |
     |                       | send_join request           |                   |
     |                       |------------------------------------------------>|
     |                       |                             |                   |
     |                       |                             |send_join response |
     |                       |<------------------------------------------------|
     |                       |                             |                   |
     |         join response |                             |                   |
     |<----------------------|                             |                   |
     |                       |                             |                   |
```

握手的第一部分通常涉及使用目錄伺服器通過 [`/query/directory`]() API 端點請求房間 ID 和加入候選伺服器列表。
如果新用戶是因收到邀請而加入房間，
加入用戶的主伺服器可以通過選擇邀請消息的原伺服器作為加入候選來優化此步驟。
但是，
加入伺服器應該注意，
邀請的原伺服器可能已經離開了房間，
因此應準備在這種優化失敗時返回到常規的加入流程。

> 加入第一步通常是和目標伺服器要資料，
> 但如果是被動邀請可以直接透過消息來優化此步驟
> 不過也要做好此狀況失敗時要改回正常的流程

一旦加入伺服器獲得了房間 ID 和加入候選伺服器列表，
它需要獲取足夠的房間信息來填充 `m.room.member` 事件的必填字段。
它通過從候選列表中選擇一個駐留伺服器，
並使用 `GET /make_join` 端點獲取這些信息。
駐留伺服器將回覆足夠的信息，
讓加入伺服器填充事件。

> 拿到房間id和伺服器列表後就要透過get /make_join來拿資料

預期加入伺服器會在模板事件中添加或替換 `origin`、`origin_server_ts` 和 `event_id`。然後，加入伺服器簽署此事件。

> 添加或替換`origin`、`origin_server_ts` 和 `event_id`後簽署

為了完成加入握手，加入伺服器將此新事件提交給其用於 `GET /make_join` 的駐留伺服器，使用 `PUT /send_join` 端點。

> 哪裡get make_join就用哪裡put send_join

駐留主伺服器然後向此事件添加其簽名，
並接受它進入房間的事件圖。
加入伺服器會接收已加入房間的完整狀態以及新簽名的成員事件。
駐留伺服器還必須將該事件發送給參與房間的其他伺服器。

> 成功加入後駐留伺服器會簽名，
> 進入房間事件圖，
> 加入伺服器接收完整狀態以及簽名過的事件，
> 同時將該事件發送給其他房間內的伺服器

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/make_join/{roomId}/{userId}</a></h1> 
<!-- markdownlint-enable -->

---

請求接收伺服器返回發送伺服器需要的信息，以準備一個加入事件，從而加入房間。

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
| `roomId` | `string` | **必需:** 即將加入的房間 ID。 |
| `userId` | `string` | **必需:** 將為其生成加入事件的用戶 ID。 |
<!-- markdownlint-enable -->

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `ver` | `[string]` | 發送伺服器支持的房間版本。默認為 `[1]`。 |
<!-- markdownlint-enable -->

> 需要roomId、userId、發送伺服器支援的版本

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 用於[加入房間](/v1.11/server-server-api/#joining-rooms)握手其餘部分的模板。請注意，根據房間版本的不同，事件格式會有所不同 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。**此處的request body描述了通用事件字段的更多詳細信息，並且可能缺少 PDU 的其他必需字段。** |
| `400` | 請求無效，伺服器嘗試加入的房間版本不在 `ver` 參數列表中，或伺服器無法驗證[受限房間條件](#restricted-rooms)。錯誤應傳遞給客戶端，以便客戶端可以為用戶提供更好的反饋。自 `v1.2` 起，可能出現以下錯誤條件：如果房間是[受限的](/v1.11/client-server-api/#restricted-rooms)，且伺服器無法驗證任何條件，則必須使用 `M_UNABLE_TO_AUTHORISE_JOIN` 錯誤碼。例如，如果伺服器不知道列為條件的任何房間，這種情況就會發生。`M_UNABLE_TO_GRANT_JOIN` 錯誤碼表明應嘗試其他伺服器加入。這通常是因為駐留伺服器可以看到加入用戶滿足一個或多個條件，例如在[受限房間](/v1.11/client-server-api/#restricted-rooms)的情況下，但駐留伺服器無法滿足 `join_authorised_via_users_server` 規則的認證條件。 |
| `403` | 加入伺服器嘗試加入的房間不允許該用戶加入。 |
| `404` | 加入伺服器嘗試加入的房間對接收伺服器是未知的。 |
<!-- markdownlint-enable -->

> 200: 成功；
> 400: 無效，加入的房間版本不在ver內，
> v1.2new =>
> `M_UNABLE_TO_AUTHORISE_JOIN`: 如果房間受限無法驗證條件(aka 不給加)，
> `M_UNABLE_TO_GRANT_JOIN` 說明應該從其他伺服器加入(aka 這裡不給加，但其他地方可能可以)；
> 403: 完全不給加；
> 404: 不知道這房間是啥。
>
> 403 vs `M_UNABLE_TO_AUTHORISE_JOIN`:
> 403是主動不給加，
> `M_UNABLE_TO_AUTHORISE_JOIN` 是沒有足夠的條件驗證所以不給加。

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event` | `[Event Template]` | 未簽名的模板事件。請注意，根據房間版本的不同，事件格式會有所不同 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
| `room_version` | `string` | 伺服器嘗試加入的房間版本。如果未提供，則房間版本默認為 "1" 或 "2"。 |
<!-- markdownlint-enable -->

Event Template
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **必需:** 事件的內容。 |
| `origin` | `string` | **必需:** 駐留主伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 駐留主伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 加入成員的用戶 ID。 |
| `state_key` | `string` | **必需:** 加入成員的用戶 ID。 |
| `type` | `string` | **必需:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `join_authorised_via_users_server` | `string` | 如果房間是[受限的](/v1.11/client-server-api/#restricted-rooms)，並且是通過可用條件之一加入，則必需。如果用戶是回應邀請，則不需要。屬於駐留伺服器並能夠向其他用戶發出邀請的任意用戶 ID。這在稍後驗證 `m.room.member` 事件的認證規則時使用。**新增於 `v1.2`** |
| `membership` | `string` | **必需:** 值為 `join`。 |
<!-- markdownlint-enable -->

```json
{
  "event": {
    "content": {
      "join_authorised_via_users_server": "@anyone:resident.example.org",
      "membership": "join"
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
<h3>400 response</h3> 
<!-- markdownlint-enable -->

Error
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必需:** 錯誤碼。 |
| `error` | `string` | 可讀的錯誤信息。 |
| `room_version` | `string` | 房間的版本。如果 `errcode` 是 `M_INCOMPATIBLE_ROOM_VERSION`，則必需。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_INCOMPATIBLE_ROOM_VERSION",
  "error": "Your homeserver does not support the features required to join this room",
  "room_version": "3"
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
| `error` | `string` | 可讀的錯誤信息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "You are not invited to this room"
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
| `error` | `string` | 可讀的錯誤信息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Unknown room"
}
```

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v1/send_join/{roomId}/{eventId}</a></h1>
<!-- markdownlint-enable -->

此 API 已棄用，將在未來版本中移除。

**注意:**
伺服器應該改用 v2 `/send_join` 端點。

將已簽名的加入事件提交給駐留伺服器，讓其接受進入房間的圖譜中。請注意，根據房間版本的不同，事件格式會有所不同 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。
**此處的請求和回應內容描述了通用事件字段的更多詳細信息，並且可能缺少 PDU 的其他必需字段。**

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
| `eventId` | `string` | **必需:** 加入事件的事件 ID。 |
| `roomId` | `string` | **必需:** 即將加入的房間 ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content](#put_matrixfederationv1send_joinroomideventid_request_membership-event-content)` | **必需:** 事件的內容。 |
| `origin` | `string` | **必需:** 加入家庭伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 加入家庭伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 加入成員的用戶 ID。 |
| `state_key` | `string` | **必需:** 加入成員的用戶 ID。 |
| `type` | `string` | **必需:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

成員事件內容
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `join_authorised_via_users_server` | `string` | 如果房間是[受限的](/v1.11/client-server-api/#restricted-rooms)，並且是通過可用條件之一加入，則必需。如果用戶是回應邀請，則不需要。屬於駐留伺服器並能夠向其他用戶發出邀請的任意用戶 ID。這在稍後驗證 `m.room.member` 事件的認證規則時使用。提供的用戶 ID 所屬的駐留伺服器必須對事件有有效簽名。如果駐留伺服器正在接收 `/send_join` 請求，則必須在發送或存儲事件之前添加簽名。**新增於 `v1.2`** |
| `membership` | `string` | **必需:** 值為 `join`。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "join"
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
| `200` | 加入事件已被接受進入房間。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

整數數組和房間狀態。

房間狀態
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `auth_chain` | `[PDU]` | **必需:** 整個當前房間狀態的授權鏈，加入事件之前。請注意，根據房間版本的不同，事件格式會有所不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
| `origin` | `string` | **必需:** 駐留伺服器的 DNS 名稱。 |
| `state` | `[PDU]` | **必需:** 加入事件之前解析的當前房間狀態。事件格式根據房間版本不同而有所不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

```json
[
  200,
  {
    "auth_chain": [
      {
        "content": {
          "see_room_version_spec": "事件格式會根據房間版本改變。"
        },
        "room_id": "!somewhere:example.org",
        "type": "m.room.minimal_pdu"
      }
    ],
    "event": {
      "auth_events": [
        "$urlsafe_base64_encoded_eventid",
        "$a-different-event-id"
      ],
      "content": {
        "join_authorised_via_users_server": "@arbitrary:resident.example.com",
        "membership": "join"
      },
      "depth": 12,
      "hashes": {
        "sha256": "thishashcoversallfieldsincasethisisredacted"
      },
      "origin": "example.com",
      "origin_server_ts": 1404838188000,
      "prev_events": [
        "$urlsafe_base64_encoded_eventid",
        "$a-different-event-id"
      ],
      "room_id": "!UcYsUzyxTGDxLBEvLy:example.org",
      "sender": "@alice:example.com",
      "signatures": {
        "example.com": {
          "ed25519:key_version": "these86bytesofbase64signaturecoveressentialfieldsincludinghashessocancheckredactedpdus"
        },
        "resident.example.com": {
          "ed25519:other_key_version": "a different signature"
        }
      },
      "state_key": "@alice:example.com",
      "type": "m.room.member",
      "unsigned": {
        "age": 4612
      }
    },
    "origin": "matrix.org",
    "state": [
      {
        "content": {
          "see_room_version_spec": "事件格式會根據房間版本改變。"
        },
        "room_id": "!somewhere:example.org",
        "type": "m.room.minimal_pdu"
      }
    ]
  }
]
```

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v2/send_join/{roomId}/{eventId}</a></h1>
<!-- markdownlint-enable -->

**注意:**
此 API 與 v1 API 幾乎相同，不同之處在於響應格式已修正。

此端點優先於 v1 API，
因為它提供了更標準化的響應格式。
接收 400、404 或其他狀態碼指示此端點不可用的發送方應重試使用 v1 API。

將已簽名的加入事件提交給駐留伺服器，
讓其接受進入房間的圖譜中。
請注意，
根據房間版本的不同，
事件格式會有所不同 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。
**此處的請求和響應內容描述了通用事件字段的更多詳細信息，並且可能缺少 PDU 的其他必需字段。**

> 將簽名過的事件正式提交給駐留伺服器

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
| `eventId` | `string` | **必需:** 加入事件的事件 ID。 |
| `roomId` | `string` | **必需:** 即將加入的房間 ID。 |
<!-- markdownlint-enable -->

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `omit_members` | `boolean` | 如果為 `true`，表示調用伺服器可以接受精簡的響應，其中成員事件從 `state` 中省略，並且冗余事件從 `auth_chain` 中省略。如果要加入的房間在其當前狀態中沒有 `m.room.name` 或 `m.room.canonical_alias` 事件，駐留伺服器應確定將包含在房間摘要的 `m.heroes` 屬性中的成員。駐留伺服器應在響應的 `state` 字段中包括這些成員的成員資格事件，並在響應的 `auth_chain` 字段中包括這些成員資格事件的授權鏈。**新增於 `v1.6`** |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **必需:** 事件的內容。 |
| `origin` | `string` | **必需:** 加入家庭伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 加入家庭伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 加入成員的用戶 ID。 |
| `state_key` | `string` | **必需:** 加入成員的用戶 ID。 |
| `type` | `string` | **必需:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

---

Membership Event Content
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `join_authorised_via_users_server` | `string` | 如果房間是[受限的](/v1.11/client-server-api/#restricted-rooms)，並且是通過可用條件之一加入，則必需。如果用戶是回應邀請，則不需要。屬於駐留伺服器並能夠向其他用戶發出邀請的任意用戶 ID。這在稍後驗證 `m.room.member` 事件的認證規則時使用。提供的用戶 ID 所屬的駐留伺服器必須對事件有有效簽名。如果駐留伺服器正在接收 `/send_join` 請求，則必須在發送或存儲事件之前添加簽名。**新增於 `v1.2`** |
| `membership` | `string` | **必需:** 值為 `join`。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "join"
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

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 加入事件已被接受進入房間。 |
| `400` | 請求在某種方式上無效。錯誤應傳遞給客戶端，以便客戶端可以為用戶提供更好的反饋。自 `v1.2` 起，可能出現以下錯誤條件：如果房間是[受限的](/v1.11/client-server-api/#restricted-rooms)，且伺服器無法驗證任何條件，則必須使用 `M_UNABLE_TO_AUTHORISE_JOIN` 錯誤碼。例如，如果伺服器不知道列為條件的任何房間，這種情況就會發生。`M_UNABLE_TO_GRANT_JOIN` 錯誤碼表明應嘗試其他伺服器加入。這通常是因為駐留伺服器可以看到加入用戶滿足一個或多個條件，例如在[受限房間](/v1.11/client-server-api/#restricted-rooms)的情況下，但駐留伺服器無法滿足 `join_authorised_via_users_server` 規則的認證條件。 |
| `403` | 加入伺服器嘗試加入的房間不允許該用戶加入。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `auth_chain` | `[PDU]` | **必需:**  新加入事件的授權鏈中的所有事件，以及任何返回的 `state` 中事件的授權鏈中的事件。如果 `omit_members` 查詢參數設置為 `true`，則返回的 `state` 中的任何事件的授權鏈中的事件可能從 `auth_chain` 中省略，無論是否從 `state` 中省略了成員事件。請注意，根據房間版本的不同，事件格式會有所不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 **變更於 `v1.6`：** 修改為僅考慮 `state` 中返回的狀態事件，並允許省略冗餘事件。 |
| `event` | `SignedMembershipEvent` | 駐留伺服器發送給其他伺服器的成員資格事件，包括駐留伺服器的簽名。如果房間是[受限的](/v1.11/client-server-api/#restricted-rooms) 且加入用戶經過某個條件授權，則必需。**新增於 `v1.2`** |
| `members_omitted` | `boolean` | 如果 `state` 中省略了 `m.room.member` 事件，則為 `true`。**新增於 `v1.6`** |
| `origin` | `string` | **必需:** 駐留伺服器的 DNS 名稱。 |
| `servers_in_room` | `[string]` | **必需** 如果 `members_omitted` 為 true。加入前房間中活躍的伺服器列表（即那些有已加入成員的伺服器）。**新增於 `v1.6`** |
| `state` | `[PDU]` | **必需:** 加入事件之前解析的當前房間狀態。如果請求中設置了 `omit_members` 為 `true`，則可能從響應中省略類型為 `m.room.member` 的事件，以減少響應的大小。如果這樣做，則必須設置 `members_omitted` 為 `true`。**變更於 `v1.6`：** 允許省略成員事件。 |
<!-- markdownlint-enable -->

```json
{
  "auth_chain": [
    {
      "content": {
        "see_room_version_spec": "事件格式會根據房間版本改變。

"
      },
      "room_id": "!somewhere:example.org",
      "type": "m.room.minimal_pdu"
    }
  ],
  "event": {
    "auth_events": [
      "$urlsafe_base64_encoded_eventid",
      "$a-different-event-id"
    ],
    "content": {
      "join_authorised_via_users_server": "@arbitrary:resident.example.com",
      "membership": "join"
    },
    "depth": 12,
    "hashes": {
      "sha256": "thishashcoversallfieldsincasethisisredacted"
    },
    "origin": "example.com",
    "origin_server_ts": 1404838188000,
    "prev_events": [
      "$urlsafe_base64_encoded_eventid",
      "$a-different-event-id"
    ],
    "room_id": "!UcYsUzyxTGDxLBEvLy:example.org",
      "sender": "@alice:example.com",
      "signatures": {
        "example.com": {
          "ed25519:key_version": "these86bytesofbase64signaturecoveressentialfieldsincludinghashessocancheckredactedpdus"
        },
        "resident.example.com": {
          "ed25519:other_key_version": "a different signature"
        }
      },
      "state_key": "@alice:example.com",
      "type": "m.room.member",
      "unsigned": {
        "age": 4612
      }
    },
    "members_omitted": true,
    "origin": "matrix.org",
    "servers_in_room": [
      "matrix.org",
      "example.com"
    ],
    "state": [
      {
        "content": {
          "see_room_version_spec": "事件格式會根據房間版本改變。"
        },
        "room_id": "!somewhere:example.org",
        "type": "m.room.minimal_pdu"
      }
    ]
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
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_UNABLE_TO_GRANT_JOIN",
  "error": "This server cannot send invites to you."
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
  "error": "You are not invited to this room"
}
```

## 1.01 受限房間

受限房間的詳細描述請參見[客戶端-伺服器 API]()，
並且僅在[支援受限加入規則]()的房間版本中可用。

處理加入受限房間請求的駐留伺服器必須確保加入伺服器滿足 `m.room.join_rules` 中指定的至少一個條件。
如果沒有可用的條件，
或沒有條件匹配所需的架構，
則認為加入伺服器未能通過所有條件。

駐留伺服器在 `/make_join` 和 `/send_join` 上使用 400 `M_UNABLE_TO_AUTHORISE_JOIN` 錯誤來表示駐留伺服器無法驗證任何條件，
通常是因為駐留伺服器沒有關於條件所需房間的狀態信息。

駐留伺服器在 `/make_join` 和 `/send_join` 上使用 400 `M_UNABLE_TO_GRANT_JOIN` 錯誤來表示加入伺服器應嘗試其他伺服器。
這通常是因為駐留伺服器可以看到加入用戶滿足其中一個條件，
儘管駐留伺服器無法滿足 `join_authorised_via_users_server` 規則對生成的 `m.room.member` 事件的認證要求。

如果加入伺服器未能通過所有條件，
則駐留伺服器使用 403 `M_FORBIDDEN` 錯誤。

> 其實這些前面講過，就是受限房間會有些條件，
> 沒有提供足夠條件驗證就會400 `M_UNABLE_TO_AUTHORISE_JOIN`，
> 用戶滿足條件但駐留伺服器沒法驗證`m.room.member` 就會400 `M_UNABLE_TO_GRANT_JOIN`，
> 如果真的不給過就會403 `M_FORBIDDEN`

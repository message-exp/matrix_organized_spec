# Inviting to a room

- 這篇主要是說如何主動邀請
- PUT /_matrix/federation/v1/invite/{roomId}/{eventId}
  - 就是個邀請的api
  - 如果同意的話會將request body簽名後回傳
  - 目前建議優先使用v2
- PUT /_matrix/federation/v2/invite/{roomId}/{eventId}
  - 我自己看是覺得這兩個差不多就是

When a user on a given homeserver invites another user on the same
 homeserver, the homeserver may sign the membership event itself and skip
 the process defined here. However, when a user invites another user on a
 different homeserver, a request to that homeserver to have the event
 signed and verified must be made.

Note that invites are used to indicate that knocks were accepted. As such,
 receiving servers should be prepared to manually link up a previous knock
 to an invite if the invite event does not directly reference the knock.

當一個家庭伺服器上的用戶邀請另一個同一家庭伺服器上的用戶時，
家庭伺服器可以自行簽名會員事件並跳過此處定義的過程。
然而，
當用戶邀請另一個不同家庭伺服器上的用戶時，
必須向該家庭伺服器請求簽名和驗證事件。

請注意，
邀請用於表示敲門被接受。
因此，
接收伺服器應準備好手動將之前的敲門與邀請聯繫起來，
即使邀請事件並未直接引用敲門事件。

<!-- markdownlint-disable -->
<h1>PUT <a>/matrix/federation/v1/invite/{roomId}/{eventId}</a></h1>
<!-- markdownlint-enable -->

邀請遠端用戶加入房間。
事件一旦由邀請伺服器和被邀請伺服器簽名，
就可以由邀請伺服器發送到房間中的所有伺服器。

伺服器應優先使用 v2 API 邀請，
而不是 v1 API。
收到 v1 邀請請求的伺服器必須假設房間版本為 `"1"` 或 `"2"`。

注意，事件格式因房間版本而異 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。
**此處的請求和回應體描述了常見的事件字段，可能缺少 PDU 的其他必要字段。**

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
| `eventId` | `string` | **Required:** 由邀請伺服器生成的邀請事件 ID。 |
| `roomId` | `string` | **Required:** 被邀請用戶要加入的房間 ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3>
<!-- markdownlint-enable -->

InviteEvent
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **Required:** 事件內容，與[客戶端-伺服器 API](/v1.11/client-server-api/)中的可用內容匹配。必須包括 `invite` 的 `membership`。 |
| `origin` | `string` | **Required:** 邀請伺服器的名稱。 |
| `origin_server_ts` | `integer` | **Required:** 邀請伺服器添加的時間戳。 |
| `sender` | `string` | **Required:** 發送原始 `m.room.third_party_invite` 的用戶 Matrix ID。 |
| `state_key` | `string` | **Required:** 被邀請成員的用戶 ID。 |
| `type` | `string` | **Required:** 值為 `m.room.member`。 |
| `unsigned` | `[UnsignedData]` | 事件中包含的未簽名信息，可能包含此處未列出的更多訊息。 |
<!-- markdownlint-enable -->

Membership Event Content
| Name | Type | Description |
| --- | --- | --- |
| `membership` | `string` | **Required:** 值為 `invite`。 |

UnsignedData
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `invite_room_state` | `[StrippedStateEvent]` | 幫助邀請接收者識別房間的[剝離狀態事件](/v1.11/client-server-api/#stripped-state)的可選列表。 |
<!-- markdownlint-enable -->

StrippedStateEvent
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `content` | `EventContent` | **Required:** 事件的 `content`。 |
| `sender` | `string` | **Required:** 事件的 `sender`。 |
| `state_key` | `string` | **Required:** 事件的 `state_key`。 |
| `type` | `string` | **Required:** 事件的 `type`。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3>
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "invite"
  },
  "origin": "matrix.org",
  "origin_server_ts": 1234567890,
  "sender": "@someone:example.org",
  "state_key": "@joe:elsewhere.com",
  "type": "m.room.member",
  "unsigned": {
    "invite_room_state": [
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
          "join_rule": "invite"
        },
        "sender": "@bob:example.org",
        "state_key": "",
        "type": "m.room.join_rules"
      }
    ]
  }
}
```

---

<!-- markdownlint-disable -->
<h3>Responses</h3>
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| Status | Description |
| --- | --- | --- |
| `200` | 事件已添加邀請伺服器的簽名。事件的所有其他字段應保持不變。請注意，事件格式因房間版本而異 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
| `403` | 不允許邀請。這可能有多種原因，包括：* 發送者不允許邀請目標用戶/伺服器。* 家庭伺服器不允許任何人邀請其用戶。* 家庭伺服器拒絕參與房間。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3>
<!-- markdownlint-enable -->

Array of `integer, Event Container`.

Event Container
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `event` | `[InviteEvent]` | **Required:** 邀請事件。請注意，事件格式因房間版本而異 - 請查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

InviteEvent
<!-- markdownlint-disable -->
| Name | Type | Description |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **Required:** 事件的內容，與[客戶端-伺服器 API](/v1.11/client-server-api/)中的可用內容匹配。必須包括 `invite` 的 `membership`。 |
| `origin` | `string` | **Required:** 邀請伺服器的名稱。 |
| `origin_server_ts` | `integer` | **Required:** 邀請伺服器添加的時間戳。 |
| `sender` | `string` | **Required:** 發送原始 `m.room.third_party_invite` 的用戶 Matrix ID。 |
| `state_key` | `string` | **Required:** 被邀請成員的用戶 ID。 |
| `type` | `string` | **Required:** 值為 `m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
| Name | Type | Description |
| --- | --- | --- |
| `membership` | `string` | **Required:** 值為 `invite`。 |

```json
[
  200,
  {
    "event": {
      "content": {
        "membership": "invite"
      },
      "origin": "example.org",
      "origin_server_ts": 1549041175876,
      "room_id": "!somewhere:example.org",
      "sender": "@someone:example.org",
      "signatures": {
        "elsewhere.com": {
          "ed25519:k3y_version": "SomeOtherSignatureHere"
        },
        "example.com": {
          "ed25519:key_version": "SomeSignatureHere"
        }
      },
      "state_key": "@someone:example.org",
      "type": "m.room.member",
      "unsigned": {
        "invite_room_state": [
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
              "join_rule": "invite"
            },
            "sender": "@bob:example.org",
            "state_key": "",
            "type": "m.room.join_rules"
          }
        ]
      }
    }
  }
]
```
<!-- markdownlint-disable -->
<h3>403 response</h3>
<!-- markdownlint-enable -->

Error
| Name | Type | Description |
| --- | --- | --- |
| `errcode` | `string` | **Required:** 錯誤代碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "User cannot invite the target user."
}
```

> 簡單來說就是，
> 邀請伺服器透過這個api傳送邀請給受邀伺服器，
> 若受邀伺服器同意的話，
> 就將傳送過來的內容簽名後回傳

<!-- markdownlint-disable -->
<h1>PUT <a>/_matrix/federation/v2/invite/{roomId}/{eventId}</a></h1>
<!-- markdownlint-enable -->

**注意：**
此API幾乎與v1 API相同，
不同之處在於請求體不同，且響應格式已修正。

邀請遠端用戶加入房間。
一旦該事件被邀請主伺服器和被邀請主伺服器簽名，
邀請主伺服器可以將其發送給房間中的所有伺服器。

此端點比v1 API更有用於伺服器。
接收到400或404響應的發送者應重試使用v1 API，
因為伺服器可能較舊，若房間版本為“1”或“2”。

注意，事件的格式根據房間版本而不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。
**此處的請求和響應體描述了更詳細的常見事件字段，可能缺少PDU的其他必要字段。**

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
| `eventId` | `string` | **必需:** 邀請事件的事件ID，由邀請伺服器生成。 |
| `roomId` | `string` | **必需:** 用戶被邀請加入的房間ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3>
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event` | `[InviteEvent](#put_matrixfederationv2inviteroomideventid_request_inviteevent)` | **必需:** 一個邀請事件。請注意，根據房間版本，事件的格式不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
| `invite_room_state` | `[[StrippedStateEvent](#put_matrixfederationv2inviteroomideventid_request_strippedstateevent)]` | 一個可選的剝離狀態事件列表，以幫助接收邀請者識別房間。 |
| `room_version` | `string` | **必需:** 用戶被邀請加入的房間版本。 |
<!-- markdownlint-enable -->

InviteEvent
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content](#put_matrixfederationv2inviteroomideventid_request_membership-event-content)` | **必需:** 事件的內容，與[客戶端-伺服器 API](/v1.11/client-server-api/)中的內容匹配。必須包括`invite`的`membership`。 |
| `origin` | `string` | **必需:** 邀請主伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 由邀請主伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 發送原始`m.room.third_party_invite`的用戶的Matrix ID。 |
| `state_key` | `string` | **必需:** 被邀請成員的用戶ID。 |
| `type` | `string` | **必需:** 值為`m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `membership` | `string` | **必需:** 值為`invite`。 |
<!-- markdownlint-enable -->

StrippedStateEvent
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `EventContent` | **必需:** 事件的`content`。 |
| `sender` | `string` | **必需:** 事件的`sender`。 |
| `state_key` | `string` | **必需:** 事件的`state_key`。 |
| `type` | `string` | **必需:** 事件的`type`。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3>
<!-- markdownlint-enable -->

```json
{
  "event": {
    "content": {
      "membership": "invite"
    },
    "origin": "matrix.org",
    "origin_server_ts": 1234567890,
    "sender": "@someone:example.org",
    "state_key": "@joe:elsewhere.com",
    "type": "m.room.member"
  },
  "invite_room_state": [
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
        "join_rule": "invite"
      },
      "sender": "@bob:example.org",
      "state_key": "",
      "type": "m.room.join_rules"
    }
  ],
  "room_version": "2"
}
```

---

<!-- markdownlint-disable -->
<h3>Responses</h3>
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 加上被邀請伺服器簽名的事件。事件的其他字段應保持不變。注意，事件的格式根據房間版本而不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
| `400` | 請求無效或伺服器嘗試加入的房間版本不在`ver`參數中列出。錯誤應傳遞給客戶端，以便他們能夠給用戶提供更好的反饋。 |
| `403` | 不允許邀請。這可能有多種原因，包括：* 發送者不允許向目標用戶/伺服器發送邀請。* 伺服器不允許任何人邀請其用戶。* 伺服器拒絕參與房間。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3>
<!-- markdownlint-enable -->

Event Container
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event` | `[InviteEvent](#put_matrixfederationv2inviteroomideventid_response-200_inviteevent)` | **必需:** 一個邀請事件。請注意，根據房間版本，事件的格式不同 - 查看[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

InviteEvent
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Membership Event Content]` | **必需:** 事件的內容，與[客戶端-伺服器 API](/v1.11/client-server-api/)中的內容匹配。必須包括`invite`的`membership`。 |
| `origin` | `string` | **必需:** 邀請主伺服器的名稱。 |
| `origin_server_ts` | `integer` | **必需:** 由邀請主伺服器添加的時間戳。 |
| `sender` | `string` | **必需:** 發送原始`m.room.third_party_invite`的用戶的Matrix ID。 |
| `state_key` | `string` | **必需:** 被邀請成員的用戶ID。 |
| `type` | `string` | **必需:** 值為`m.room.member`。 |
<!-- markdownlint-enable -->

Membership Event Content
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `membership` | `string` | **必需:** 值為`invite`。 |
<!-- markdownlint-enable -->

```json
{
  "event": {
    "content": {
      "membership": "invite"
    },
    "origin": "example.org",
    "origin_server_ts": 1549041175876,
    "room_id": "!somewhere:example.org",
    "sender": "@someone:example.org",
    "signatures": {
      "elsewhere.com": {
        "ed25519:k3y_version": "SomeOtherSignatureHere"
      },
      "example.com": {
        "ed25519:key_version": "SomeSignatureHere

"
      }
    },
    "state_key": "@someone:example.org",
    "type": "m.room.member",
    "unsigned": {
      "invite_room_state": [
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
            "join_rule": "invite"
          },
          "sender": "@bob:example.org",
          "state_key": "",
          "type": "m.room.join_rules"
        }
      ]
    }
  }
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
| `error` | `string` | 一個可讀的錯誤訊息。 |
| `room_version` | `string` | 房間的版本。如果`errcode`是`M_INCOMPATIBLE_ROOM_VERSION`，則必需。 |
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
| `error` | `string` | 一個可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "User cannot invite the target user."
}
```

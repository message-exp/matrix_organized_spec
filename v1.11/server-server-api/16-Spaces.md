# Spaces

這段內容描述了Matrix協議中用於查詢空間(Spaces)層次結構的API端點。以下是主要內容的概述:

1. GET /\_matrix/federation/v1/hierarchy/{roomId}
   - 用途: 獲取指定空間房間的層次結構信息
   - 主要特點:
     - 這是客戶端-服務器API中 GET /hierarchy 端點的聯邦版本
     - 不進行分頁,直接返回所有可訪問的子房間
     - 僅考慮房間的 m.space.child 狀態事件
     - 響應應被緩存一段時間
   - 主要參數:
     - roomId: 要獲取層次結構的空間房間ID
     - suggested_only: 是否只考慮建議的房間
   - 響應內容:
     - children: 空間子房間的摘要
     - inaccessible_children: 無法訪問的房間ID列表
     - room: 請求的房間摘要

響應包含詳細的房間信息,如房間ID、名稱、主題、成員數量、加入規則等。

此API允許服務器之間查詢彼此的空間結構,對於構建和維護分佈式空間網絡至關重要。它提供了跨服務器發現和瀏覽空間層次結構的能力。

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/hierarchy/{roomId}</a></h1> 
<!-- markdownlint-enable -->

**已在 `v1.2` 中添加**

這是 Client-Server [`GET /hierarchy`](/v1.11/client-server-api/#get_matrixclientv1roomsroomidhierarchy) 端點的聯邦版本。
與 Client-Server API 版本不同，此端點不會分頁。取而代之的是，請求伺服器可以合理地查看或加入的所有空間房間的子房間將會返回。請求伺服器負責進一步過濾用戶請求的結果。

此端點僅考慮房間的 [`m.space.child`](/v1.11/client-server-api/#mspacechild) 狀態事件。無效的子房間和父事件不在此端點的範圍內。

對此端點的響應應該緩存一段時間。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要獲取層級的空間房間的房間 ID。 |
<!-- markdownlint-enable -->

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `suggested_only` | `boolean` | 可選的（默認為 `false`）標誌，指示伺服器是否應該僅考慮推薦的房間。推薦的房間在其 [`m.space.child`](/v1.11/client-server-api/#mspacechild) 事件內容中被註明。 |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 空間房間及其子房間。 |
| `404` | 該房間在伺服器中未知，或者請求伺服器無法查看/加入它（如果嘗試這樣做）。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `children` | `[SpaceHierarchyChildRoomsChunk]` | **Required:** 空間子房間的摘要。請求伺服器無法查看/加入的房間將被排除。 |
| `inaccessible_children` | `[string]` | **Required:** 請求伺服器無法通過合理方式查看/加入的房間 ID 列表。無法提供詳細信息的房間將直接從響應中排除。假設請求伺服器和響應伺服器都表現良好，請求伺服器應將這些房間 ID 視為任何地方都無法訪問。它們不應該被重新請求。 |
| `room` | `[SpaceHierarchyParentRoom]` | **Required:** 請求的房間摘要。 |
<!-- markdownlint-enable -->

SpaceHierarchyChildRoomsChunk
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `allowed_room_ids` | `[string]` | 如果該房間是[受限房間](#restricted-rooms)，這些是加入規則中指定的房間 ID。否則為空或省略。 |
| `avatar_url` | `[URI](http://tools.ietf.org/html/rfc3986)` | 房間的頭像 URL，如果設置了頭像。 |
| `canonical_alias` | `string` | 房間的標準別名（如果有）。 |
| `guest_can_join` | `boolean` | **Required:** 訪客用戶是否可以加入並參與房間。如果可以，他們將像其他用戶一樣受普通權限級別規則約束。 |
| `join_rule` | `string` | 房間的加入規則。如果未顯示，則假定房間為 `public`。 |
| `name` | `string` | 房間的名稱（如果有）。 |
| `num_joined_members` | `integer` | **Required:** 已加入房間的成員數量。 |
| `room_id` | `string` | **Required:** 房間的 ID。 |
| `room_type` | `string` | 房間的 `type`（來自 [`m.room.create`](https://spec.matrix.org/v1.11/client-server-api/#mroomcreate)），如果有。**Added in `v1.4`** |
| `topic` | `string` | 房間的主題（如果有）。 |
| `world_readable` | `boolean` | **Required:** 房間是否可供訪客用戶在未加入的情況下查看。 |
<!-- markdownlint-enable -->

SpaceHierarchyParentRoom
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `allowed_room_ids` | `[string]` | 如果該房間是[受限房間](#restricted-rooms)，這些是加入規則中指定的房間 ID。否則為空或省略。 |
| `avatar_url` | `[URI](http://tools.ietf.org/html/rfc3986)` | 房間的頭像 URL，如果設置了頭像。 |
| `canonical_alias` | `string` | 房間的標準別名（如果有）。 |
| `children_state` | `[StrippedStateEvent]` | **Required:**  空間房間的 [`m.space.child`](/v1.11/client-server-api/#mspacechild) 事件，以 [Stripped State Events](/v1.11/client-server-api/#stripped-state) 的形式表示，並添加 `origin_server_ts` 鍵。如果房間不是空間房間，這應該是空的。 |
| `guest_can_join` | `boolean` | **Required:** 訪客用戶是否可以加入並參與房間。如果可以，他們將像其他用戶一樣受普通權限級別規則約束。 |
| `join_rule` | `string` | 房間的加入規則。如果未顯示，則假定房間為 `public`。 |
| `name` | `string` | 房間的名稱（如果有）。 |
| `num_joined_members` | `integer` | **Required:** 已加入房間的成員數量。 |
| `room_id` | `string` | **Required:** 房間的 ID。 |
| `room_type` | `string` | 房間的 `type`（來自 [`m.room.create`](https://spec.matrix.org/v1.11/client-server-api/#mroomcreate)），如果有。**Added in `v1.4`** |
| `topic` | `string` | 房間的主題（如果有）。 |
| `world_readable` | `boolean` | **Required:** 房間是否可供訪客用戶在未加入的情況下查看。 |
<!-- markdownlint-enable -->

StrippedStateEvent
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `EventContent` | **Required:** 事件的 `content`。 |
| `origin_server_ts` | `integer` | **Required:** 事件的 `origin_server_ts`。 |
| `sender` | `string` | **Required:** 事件的 `sender`。 |
| `state_key` | `string` | **Required:** 事件的 `state_key`。 |
| `type` | `string` | **Required:** 事件的 `type`。 |
<!-- markdownlint-enable -->

```json
{
  "children": [
    {
      "allowed_room_ids": [
        "!upstream:example.org"
      ],
      "avatar_url": "mxc://example.org/abcdef2",
      "canonical_alias": "#general:example.org",
      "children_state": [
        {
          "content": {
            "via": [
              "remote.example.org"
            ]
          },
          "origin_server_ts": 1629422222222,
          "sender": "@alice:example.org",
          "state_key": "!b:example.org",
          "type": "m.space.child"
        }
      ],
      "guest_can_join": false,
      "join_rule": "restricted",
      "name": "The ~~First~~ Second Space",


      "num_joined_members": 42,
      "room_id": "!second_room:example.org",
      "room_type": "m.space",
      "topic": "Hello world",
      "world_readable": true
    }
  ],
  "inaccessible_children": [
    "!secret:example.org"
  ],
  "room": {
    "allowed_room_ids": [],
    "avatar_url": "mxc://example.org/abcdef",
    "canonical_alias": "#general:example.org",
    "children_state": [
      {
        "content": {
          "via": [
            "remote.example.org"
          ]
        },
        "origin_server_ts": 1629413349153,
        "sender": "@alice:example.org",
        "state_key": "!a:example.org",
        "type": "m.space.child"
      }
    ],
    "guest_can_join": false,
    "join_rule": "public",
    "name": "The First Space",
    "num_joined_members": 42,
    "room_id": "!space:example.org",
    "room_type": "m.space",
    "topic": "No other spaces were created first, ever",
    "world_readable": true
  }
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **Required:** 錯誤代碼。 |
| `error` | `string` | 一個可讀的錯誤訊息。 |
<!-- markdownlint-enable -->

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Room does not exist."
}
```

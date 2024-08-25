# Public Room Directory

---
這段內容主要描述了Matrix協議中用於查詢公共房間目錄的兩個API端點。以下是主要內容的概述:

1. GET /\_matrix/federation/v1/publicRooms
   - 用途:獲取特定homeserver上的所有公共房間列表
   - 主要參數:
     - include_all_networks:是否包括所有網絡/協議
     - limit:返回房間的最大數量
     - since:分頁標記
     - third_party_instance_id:特定第三方網絡/協議ID

2. POST /\_matrix/federation/v1/publicRooms
   - 用途:列出服務器上的公共房間,可選擇性過濾
   - 主要參數:
     - filter:應用於結果的過濾器
     - include_all_networks:是否包括所有已知網絡/協議
     - limit:限制返回結果數量
     - since:分頁標記
     - third_party_instance_id:特定第三方網絡/協議ID

兩個端點都返回分頁的房間列表,包含房間的詳細信息如房間ID、名稱、主題、成員數量等。返回的數據還包括下一頁和上一頁的分頁標記,以及公共房間總數的估計值。

這些API允許服務器之間查詢彼此的公共房間目錄,有助於實現跨服務器的房間發現功能。

---
---

<!-- markdownlint-disable -->
<h1>GET <a>/_matrix/federation/v1/publicRooms</a></h1> 
<!-- markdownlint-enable -->


獲取該主伺服器的所有公開房間。這不應該返回列在其他主伺服器目錄中的房間，只返回列在接收伺服器目錄中的房間。

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

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `include_all_networks` | `boolean` | 是否包括由主伺服器上的應用服務定義的所有網絡/協議。默認為 false。 |
| `limit` | `integer` | 返回房間的最大數量。默認為 0（無限制）。 |
| `since` | `string` | 從以前調用此端點獲取更多房間的分頁令牌。 |
| `third_party_instance_id` | `string` | 從主伺服器請求的特定第三方網絡/協議。只能在 `include_all_networks` 為 false 時使用。 |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 主伺服器的公開房間列表。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `chunk` | `[PublicRoomsChunk]` | **Required:** 公開房間的分頁塊。 |
| `next_batch` | `string` | 響應的分頁令牌。沒有此令牌表示沒有更多結果可獲取，客戶端應停止分頁。 |
| `prev_batch` | `string` | 允許獲取以前結果的分頁令牌。沒有此令牌表示此批之前沒有結果，即這是第一批。 |
| `total_room_count_estimate` | `integer` | 對公開房間總數的估計，如果伺服器有估計值。 |
<!-- markdownlint-enable -->

PublicRoomsChunk
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `avatar_url` | `[URI](http://tools.ietf.org/html/rfc3986)` | 房間的頭像 URL，如果設置了頭像。 |
| `canonical_alias` | `string` | 房間的標準別名（如果有）。 |
| `guest_can_join` | `boolean` | **Required:** 訪客用戶是否可以加入並參與房間。如果他們可以，則他們將像其他用戶一樣受普通權限級別規則約束。 |
| `join_rule` | `string` | 房間的加入規則。如果未顯示，則房間假定為 `public`。請注意，帶有 `invite` 加入規則的房間不應出現在這裡，但由於其接近公開性質，帶有 `knock` 規則的房間可以出現。 |
| `name` | `string` | 房間的名稱（如果有）。 |
| `num_joined_members` | `integer` | **Required:** 已加入房間的成員數量。 |
| `room_id` | `string` | **Required:** 房間的 ID。 |
| `room_type` | `string` | 房間的 `type`（來自 [`m.room.create`](https://spec.matrix.org/v1.11/client-server-api/#mroomcreate)），如果有。**Added in `v1.4`** |
| `topic` | `string` | 房間的主題（如果有）。 |
| `world_readable` | `boolean` | **Required:** 房間是否可供訪客用戶在未加入的情況下查看。 |
<!-- markdownlint-enable -->

```json
{
  "chunk": [
    {
      "avatar_url": "mxc://bleecker.street/CHEDDARandBRIE",
      "guest_can_join": false,
      "join_rule": "public",
      "name": "CHEESE",
      "num_joined_members": 37,
      "room_id": "!ol19s:bleecker.street",
      "room_type": "m.space",
      "topic": "Tasty tasty cheese",
      "world_readable": true
    }
  ],
  "next_batch": "p190q",
  "prev_batch": "p1902",
  "total_room_count_estimate": 115
}
```

---

<!-- markdownlint-disable -->
<h1>POST<a>/_matrix/federation/v1/publicRooms</a></h1> 
<!-- markdownlint-enable -->

列出伺服器上的公開房間，並可選擇應用過濾器。

此 API 返回分頁響應。房間按加入成員數量排序，最大房間在前。

請注意，此端點接收並返回的格式與 Client-Server API 的 `POST /publicRooms` 端點中看到的格式相同。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `filter` | `[Filter]` | 要應用於結果的過濾器。 |
| `include_all_networks` | `boolean` | 是否包括來自主伺服器上的應用服務的所有已知網絡/協議。默認為 false。 |
| `limit` | `integer` | 限制返回的結果數量。 |
| `since` | `string` | 來自之前請求的分頁令牌，允許伺服器獲取下一批（或上一批）房間。分頁方向僅由提供的令牌決定，而不是通過明確的標誌來指定。 |
| `third_party_instance_id` | `string` | 從主伺服器請求的特定第三方網絡/協議。只能在 `include_all_networks` 為 false 時使用。 |
<!-- markdownlint-enable -->

Filter
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `generic_search_term` | `string` | 要在房間元數據中搜索的可選字符串，例如名稱、主題、標準別名等。 |
| `room_types` | `[string\|null]` | 要搜索的可選 [房間類型](https://spec.matrix.org/v1.11/client-server-api/#types) 列表。要包括沒有房間類型的房間，請在此列表中指定 `null`。當未指定時，將返回所有適用的房間（無論類型）。**Added in `v1.4`** |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "filter": {
    "generic_search_term": "foo",
    "room_types": [
      null,
      "m.space"
    ]
  },
  "include_all_networks": false,
  "limit": 10,
  "third_party_instance_id": "irc"
}
```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 伺服器上的房間列表。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `chunk` | `[PublicRoomsChunk]` | **Required:** 公開房間的分頁塊。 |
| `next_batch` | `string` | 響應的分頁令牌。沒有此令牌表示沒有更多結果可獲取，客戶端應停止分頁。 |
| `prev_batch` | `string` | 允許獲取以前結果的分頁令牌。沒有此令牌表示此批之前沒有結果，即這是第一批。 |
| `total_room_count_estimate` | `integer` | 對公開房間總數的估計，如果伺服

器有估計值。 |
<!-- markdownlint-enable -->

PublicRoomsChunk
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `avatar_url` | `[URI](http://tools.ietf.org/html/rfc3986)` | 房間的頭像 URL，如果設置了頭像。 |
| `canonical_alias` | `string` | 房間的標準別名（如果有）。 |
| `guest_can_join` | `boolean` | **Required:** 訪客用戶是否可以加入並參與房間。如果他們可以，則他們將像其他用戶一樣受普通權限級別規則約束。 |
| `join_rule` | `string` | 房間的加入規則。如果未顯示，則房間假定為 `public`。請注意，帶有 `invite` 加入規則的房間不應出現在這裡，但由於其接近公開性質，帶有 `knock` 規則的房間可以出現。 |
| `name` | `string` | 房間的名稱（如果有）。 |
| `num_joined_members` | `integer` | **Required:** 已加入房間的成員數量。 |
| `room_id` | `string` | **Required:** 房間的 ID。 |
| `room_type` | `string` | 房間的 `type`（來自 [`m.room.create`](https://spec.matrix.org/v1.11/client-server-api/#mroomcreate)），如果有。**Added in `v1.4`** |
| `topic` | `string` | 房間的主題（如果有）。 |
| `world_readable` | `boolean` | **Required:** 房間是否可供訪客用戶在未加入的情況下查看。 |
<!-- markdownlint-enable -->

```json
{
  "chunk": [
    {
      "avatar_url": "mxc://bleecker.street/CHEDDARandBRIE",
      "guest_can_join": false,
      "join_rule": "public",
      "name": "CHEESE",
      "num_joined_members": 37,
      "room_id": "!ol19s:bleecker.street",
      "room_type": "m.space",
      "topic": "Tasty tasty cheese",
      "world_readable": true
    }
  ],
  "next_batch": "p190q",
  "prev_batch": "p1902",
  "total_room_count_estimate": 115
}
```


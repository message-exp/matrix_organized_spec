# Backfilling and retrieving missing events

一旦一個 homeserver 加入了房間，它會接收到該房間中其他 homeserver 發出的所有事件，從而了解該房間從那一刻起的全部歷史。由於房間內的使用者可以通過 `/messages` 客戶端 API 端點請求歷史記錄，可能會出現這種情況：他們可能回溯到 homeserver 本身還不是該房間成員之前的歷史。

為了應對這種情況，聯邦 API 提供了一個 `/messages` 客戶端 API 的伺服器到伺服器的類比，允許一個 homeserver 從另一個 homeserver 獲取歷史記錄。這就是 `/backfill` API。

要請求更多歷史記錄，請求的 homeserver 會選擇另一個它認為可能擁有更多歷史記錄的 homeserver（最有可能的是那些在當前歷史的最早時間點上已經存在的使用者的 homeserver），並發出 `/backfill` 請求。

類似於填補房間的歷史記錄，伺服器可能並沒有圖中的所有事件。該伺服器可以使用 `/get_missing_events` API 來獲取它缺少的事件。

<!-- markdownlint-disable -->
<h1>GET <a>/\_matrix/federation/v1/backfill/{roomId}</a></h1> 
<!-- markdownlint-enable -->

檢索給定房間中之前 PDU 的滑動窗口歷史。
從 `v` 參數中給定的 PDU ID(s) 開始，檢索 `v` 中給定的 PDU 及其之前的 PDU，最多檢索 `limit` 中給定的總數。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

Request parameters

path parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要填補的房間 ID。 |

<!-- markdownlint-disable -->
query parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `limit` | `integer` | **Required:** 檢索的最大 PDU 數量，包括給定的事件。 |
| `v` | `[string]` | **Required:** 從這些事件 ID 開始進行填補。 |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 包含給定事件及其之前事件的交易，最多到達給定的限制。 **注意:** 雖然 PDU 定義要求 `prev_events` 和 `auth_events` 的數量受到限制，但填補的回應不必根據這些特定限制進行驗證。由於歷史原因，先前被接受的事件現在可能會被這些限制拒絕。事件應按照 `/send`、`/get_missing_events` 和其餘端點的通常規則拒絕。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
交易
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `origin` | `string` | **Required:** 發送此交易的 homeserver 的 `server_name`。 |
| `origin_server_ts` | `integer` | **Required:** 此交易開始時在發起 homeserver 上的 POSIX 毫秒時間戳。 |
| `pdus` | `[PDU]` | **Required:** 房間的持久更新列表。注意，根據房間版本的不同，事件格式也不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

```json
{
  "origin": "matrix.org",
  "origin_server_ts": 1234567890,
  "pdus": [
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

---

<!-- markdownlint-disable -->
<h1>POST <a>/\_matrix/federation/v1/get\_missing\_events/{roomId}</a></h1> 
<!-- markdownlint-enable -->

檢索發送者缺少的先前事件。
這是通過對 `latest_events` 的 `prev_events` 進行廣度優先遍歷來完成的，
忽略 `earliest_events` 中的任何事件，並在到達 `limit` 時停止。

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

路徑參數
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要搜索的房間 ID。 |

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `earliest_events` | `[string]` | **Required:** 發送者已經擁有的最新事件 ID。檢索 `latest_events` 的先前事件時會跳過這些事件。 |
| `latest_events` | `[string]` | **Required:** 要檢索先前事件的事件 ID。 |
| `limit` | `integer` | 檢索的最大事件數量。預設為 10。 |
| `min_depth` | `integer` | 要檢索事件的最小深度。預設為 0。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "earliest_events": [
    "$missing_event:example.org"
  ],
  "latest_events": [
    "$event_that_has_the_missing_event_as_a_previous_event:example.org"
  ],
  "limit": 10
}
```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | `latest_events` 的先前事件，不包括任何 `earliest_events`，最多到達提供的 `limit`。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `events` | `[PDU]` | **Required:** 缺少的事件。事件格式根據房間版本而變化 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

```json
{
  "events": [
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

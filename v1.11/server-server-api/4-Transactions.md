# 4. Transactions

- [4. Transactions](#4-transactions)
      - [Ephemeral Data Unit](#ephemeral-data-unit)
      - [PDU Processing Result](#pdu-processing-result)

在homeserver之間傳輸EDUs和PDUs是通過交易消息（Transaction messages）進行的，
這些消息被編碼為JSON對象，
通過HTTP PUT請求傳送。
交易僅對交換它們的家庭伺服器對有意義；它們不具有全球意義。

交易的大小是有限制的；它們最多可以包含50個PDUs和100個EDUs。

<!-- markdownlint-disable -->
<h1>PUT <a>/_matrix/federation/v1/send/{txnId}</a></h1>
<!-- markdownlint-enable -->

將表示即時活動的消息推送到另一個伺服器。
目標名稱將設置為接收伺服器本身。
交易體中的每個嵌入的PDU將被處理。

發送伺服器必須等待並重試，
直到收到200 OK響應，
然後才能向接收伺服器發送不同`txnId`的交易。

注意，事件格式根據房間版本不同而有所不同 - 請參考[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。

| 受速率限制： | 否 |
| --- | --- |
| 需要認證： | 是 |

<!-- markdownlint-disable -->
<h2> Request</h2>
<h3> Request parameters </h3>
<!-- markdownlint-enable -->

| 名稱 | 類型 | 說明 |
| --- | --- | --- |
| `txnId` | `string` | **必需:** 交易ID。 |

<!-- markdownlint-disable -->
<h3> Request body </h3>
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 說明 |
| --- | --- | --- |
| `edus` | [[Ephemeral Data Unit](#ephemeral-data-unit)] | 短暫消息列表。如果沒有要發送的短暫消息，可以省略。不得包含超過100個EDUs。 |
| `origin` | `string` | **必需:** 發送此交易的家庭伺服器的`server_name`。 |
| `origin_server_ts` | `integer` | **必需:** 發送此交易時起始家庭伺服器的POSIX時間戳（毫秒）。 |
| `pdus` | `[PDU]` | **必需:** 房間的持久更新列表。不得包含超過50個PDUs。注意，事件格式根據房間版本不同而有所不同 - 請參考[房間版本規範](/v1.11/rooms)以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
#### Ephemeral Data Unit
<!-- markdownlint-enable -->

| 名稱 | 類型 | 說明 |
| --- | --- | --- |
| `content` | `object` | **必需:** 短暫消息的內容。 |
| `edu_type` | `string` | **必需:** 短暫消息的類型。 |

<!-- markdownlint-disable -->
<h3> Request body example</h3>
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
```json
{
  "origin": "matrix.org",
  "origin_server_ts": 1234567890,
  "pdus": [
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
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h2> Responses </h2>
<!-- markdownlint-enable -->

| 狀態 | 說明 |
| --- | --- |
| `200` | 處理交易的結果。即使一個或多個PDUs處理失敗，伺服器也會使用此響應。 |

<!-- markdownlint-disable -->
<h3> 200 response </h3>
<h4> PDU Processing Results </h4>
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 說明 |
| --- | --- | --- |
| `pdus` | {[事件ID](/v1.11/appendices#event-ids): [PDU處理結果](#pdu-processing-result)} | **必需:** 原交易中的PDUs。字串鍵代表被處理的PDU（事件）的ID。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
#### PDU Processing Result
<!-- markdownlint-enable -->

| 名稱 | 類型 | 說明 |
| --- | --- | --- |
| `error` | `string` | 處理此PDU時出現問題的描述。如果沒有錯誤，則表示PDU已成功處理。 |

```json
{
  "pdus": {
    "$failed_event:example.org": {
      "error": "You are not allowed to send a message to this room."
    },
    "$successful_event:example.org": {}
  }
}
```

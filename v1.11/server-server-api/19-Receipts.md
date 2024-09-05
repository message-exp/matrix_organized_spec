# Receipts

1. 回執是一種 EDU (Ephemeral Data Unit),用於傳達特定事件的標記。
2. 目前只支持"已讀回執",表示用戶在事件圖中讀到的位置。
3. 用戶發送的事件不需要發送已讀回執,因為發送事件本身就暗示了用戶已讀。
4. 主要的 EDU 類型是 "m.receipt"。
5. m.receipt EDU 的結構:
   - content: 包含每個房間的回執信息
   - 每個房間包含 "m.read" 字段,列出用戶的已讀狀態
6. 用戶的已讀回執信息包括:
   - event_ids: 用戶已讀到的極端事件 ID 列表
   - data: 元數據,包含時間戳 (ts) 和可選的線程 ID (thread_id)
7. 時間戳 (ts) 是毫秒級的 POSIX 時間戳,表示用戶讀取事件的時間。
8. 線程 ID (thread_id) 用於指定回執所屬的線程,如果未指定則為非線程回執。
9. 接收回執時,伺服器只應更新 EDU 中列出的條目,不應刪除或修改先前接收的未出現在新 EDU 中的回執。

回條（Receipts）是用於傳遞給定事件標記的 EDU。目前唯一支援的回條類型是「已讀回條」，也就是使用者已讀事件圖中的某一位置。

對於使用者自己發送的事件，不需要發送已讀回條。因為發送事件本身就意味著使用者已讀該事件。

<!-- markdownlint-disable -->
<h1>`m.receipt`</h1>
<!-- markdownlint-enable -->

代表發送 homeserver 使用者回條更新的 EDU。接收回條時，伺服器應該僅更新 EDU 中列出的條目。之前接收到但未出現在 EDU 中的回條不應被移除或更改。

`m.receipt`
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `{[Room ID](/v1.11/appendices#room-ids): [Room Receipts]}` | **必填項:** 某個房間的回條。字串 key 是房間 ID，對應其下的回條。 |
| `edu_type` | `string` | **必填項:** 字串 `m.receipt`，其中之一: `[m.receipt]`。 |
<!-- markdownlint-enable -->

Room Receipts
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `m.read` | `{[User ID](/v1.11/appendices#user-identifiers): [User Read Receipt]}` | **必填項:** 房間中使用者的已讀回條。字串 key 是該回條所屬的使用者 ID。 |
<!-- markdownlint-enable -->

User Read Receipt
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `data` | `[Read Receipt Metadata]` | **必填項:** 已讀回條的元數據。 |
| `event_ids` | `[string]` | **必填項:** 使用者已讀的最末事件 ID。 |
<!-- markdownlint-enable -->

Read Receipt Metadata
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `thread_id` | `string` | 此回條所屬的根執行緒事件 ID（或 `main`）。如果未指定，則回條為未綫程化（默認）。**於 `v1.4` 添加**。 |
| `ts` | `integer` | **必填項:** 使用者已讀回條中指定事件的 POSIX 毫秒級時間戳。 |
<!-- markdownlint-enable -->

## 範例

```json
{
  "content": {
    "!some_room:example.org": {
      "m.read": {
        "@john:matrix.org": {
          "data": {
            "ts": 1533358089009
          },
          "event_ids": [
            "$read_this_event:matrix.org"
          ]
        }
      }
    }
  },
  "edu_type": "m.receipt"
}
```

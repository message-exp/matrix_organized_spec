### 發送至設備的消息

此模組提供了一種方式，讓用戶端可以交換信號消息，而無需將其永久存儲為共享通信歷史的一部分。每條消息都會準確地傳遞給每個用戶端設備一次。

這個 API 的主要動機是交換在房間 DAG 中無意義或不希望持久化的數據 - 例如，一次性認證令牌或密鑰數據。它不適用於對話數據，對話數據應該使用正常的 [`/rooms/<room_id>/send`](/client-server-api/#put_matrixclientv3roomsroomidsendeventtypetxnid) API 發送，以保持 Matrix 的一致性。

#### 用戶端行為

要向其他設備發送消息，用戶端應調用 [`/sendToDevice`](/client-server-api/#put_matrixclientv3sendtodeviceeventtypetxnid)。每個交易中只能向每個設備發送一條消息，並且它們必須具有相同的事件類型。請求正文中的設備 ID 可以設置為 `*`，以請求將消息發送到所有已知設備。

如果有發送至設備的消息等待用戶端處理，它們將由 [`/sync`](/client-server-api/#get_matrixclientv3sync) 返回，詳情見 [/sync 的擴展](/client-server-api/#extensions-to-sync)。用戶端應檢查每個返回事件的 `type`，並忽略任何它們不理解的事件。

#### 伺服器行為

伺服器應該為本地用戶存儲待處理的消息，直到它們成功傳遞到目標設備。當用戶端使用與有待處理消息的設備對應的訪問令牌調用 [`/sync`](/client-server-api/#get_matrixclientv3sync) 時，伺服器應該按照到達順序在回應正文中列出待處理的消息。

當用戶端再次使用第一個回應中的 `next_batch` 令牌調用 `/sync` 時，伺服器應該推斷該回應中的任何發送至設備的消息已成功傳遞，並將它們從存儲中刪除。

如果有大量待發送至設備的消息，伺服器應該限制每個 `/sync` 回應中發送的消息數量。建議以 100 條消息為合理限制。

如果用戶端向遠程域的用戶發送消息，這些消息應該通過[聯邦](/server-server-api#send-to-device-messaging)發送到遠程伺服器。

#### 協議定義

{{% http-api spec="client-server" api="to_device" %}}

##### /sync 的擴展

此模組向 [`/sync`](/client-server-api/#get_matrixclientv3sync) 回應添加以下屬性：

| 參數      | 類型      | 描述                                                   |
|-----------|-----------|--------------------------------------------------------|
| to_device | ToDevice  | 可選。用戶端設備的發送至設備消息的資訊。              |

`ToDevice`

| 參數   | 類型      | 描述                     |
|--------|-----------|--------------------------|
| events | [Event]   | 發送至設備消息的列表。  |

`Event`

| 參數     | 類型         | 描述                                                                        |
|----------|--------------|-----------------------------------------------------------------------------|
| content  | EventContent | 此事件的內容。此對象中的欄位將根據事件類型而變化。                        |
| sender   | string       | 發送此事件的 Matrix 用戶 ID。                                              |
| type     | string       | 事件類型。                                                                 |

示例回應：

```json
{
  "next_batch": "s72595_4483_1934",
  "rooms": {"leave": {}, "join": {}, "invite": {}},
  "to_device": {
    "events": [
      {
        "sender": "@alice:example.com",
        "type": "m.new_device",
        "content": {
          "device_id": "XYZABCDE",
          "rooms": ["!726s6s6q:example.com"]
        }
      }
    ]
  }
}
```

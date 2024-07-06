### 輸入通知

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/typing_notifications.md)

使用者可能希望在另一個使用者在房間中輸入時得到通知。這可以通過使用輸入通知來實現。這些是臨時事件，所以它們不構成[事件圖](/#event-graphs)的一部分。輸入通知的範圍限於房間。

#### 事件

{{% event event="m.typing" %}}

#### 用戶端行為

當用戶端收到 `m.typing` 事件時，它必須使用使用者 ID 列表來**替換**它對當前正在輸入的每個使用者的知識。這樣做的原因是伺服器*不記住*當前不在輸入的使用者，因為那個列表很快就會變大。用戶端應將不在該列表中的任何使用者 ID 標記為不輸入。

建議用戶端存儲一個 `boolean` 值，指示使用者是否正在輸入。當這個值為 `true` 時，一個計時器應該每 N 秒定期觸發一次，以發送輸入 HTTP 請求。建議 N 的值不超過 20-30 秒。用戶端應重新發送此請求，以繼續通知伺服器使用者仍在輸入。由於後續請求將替換較舊的請求，建議在預期超時運行之前留出 5 秒的安全餘量。當使用者停止輸入時，`boolean` 值變為 `false` 的狀態變化應觸發另一個 HTTP 請求，通知伺服器使用者已停止輸入。

{{% http-api spec="client-server" api="typing" %}}

#### 安全考慮

用戶端可能不希望通知房間中的每個人他們正在輸入，而只通知房間中的特定使用者。

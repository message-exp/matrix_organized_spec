### 聊天室預覽

有時候希望提供聊天室的預覽，讓用戶可以"潛伏"並閱讀發布到聊天室的訊息，而無需加入聊天室。當與[訪客訪問](#guest-access)結合使用時，這可能特別有效。

預覽是通過`world_readable` [聊天室歷史可見性](#room-history-visibility)設置以及[GET /events](#get_matrixclientv3events)端點的特殊版本來實現的。

#### 用戶端行為

希望在不加入聊天室的情況下查看聊天室的用戶端應該調用[GET /rooms/:room\_id/initialSync](#get_matrixclientv3roomsroomidinitialsync)，然後是[GET /events](#get_matrixclientv3events)。用戶端需要為每個希望查看的聊天室並行執行此操作。

用戶端當然也可以調用其他端點，如[GET /rooms/:room\_id/messages](#get_matrixclientv3roomsroomidmessages)和[GET /search](#post_matrixclientv3search)，以訪問`/events`流之外的事件。

{{% http-api spec="client-server" api="peeking_events" anchor_base="peeking" %}}

#### 伺服器行為

對於尚未加入聊天室的用戶端，伺服器只需返回事件時聊天室狀態中存在`m.room.history_visibility`狀態事件，且`history_visibility`值為`world_readable`的事件。

#### 安全考慮

用戶端可能希望向其用戶顯示，`world_readable`的聊天室*可能*向未加入的用戶顯示訊息。使用此模塊無法得知是否有任何未加入的訪客用戶*確實*看到了聊天室中的事件，也無法列出或計算任何潛伏的用戶。

### 完全閱讀標記

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/read_markers.md)

給定房間的歷史可能分為三個部分：使用者已閱讀的訊息（或表示他們對這些訊息不感興趣），使用者可能閱讀了一些但未閱讀其他的訊息，以及使用者尚未看到的訊息。"完全閱讀標記"（也稱為"閱讀標記"）標記第一部分的最後一個事件，而使用者的閱讀回執標記第二部分的最後一個事件。

#### 事件

使用者的完全閱讀標記作為事件保存在房間的[帳戶資料](#client-config)中。可以讀取該事件以確定使用者在房間中當前的完全閱讀標記位置，就像其他帳戶資料事件一樣，更新時該事件將被推送到事件流中。

完全閱讀標記保存在 `m.fully_read` 事件下。如果使用者的帳戶資料中不存在該事件，完全閱讀標記應被視為使用者的閱讀回執位置。

{{% event event="m.fully_read" %}}

#### 用戶端行為

用戶端不能通過直接修改 `m.fully_read` 帳戶資料事件來更新完全閱讀標記。相反，用戶端必須使用閱讀標記 API 來更改值。

{{< changed-in v="1.4" >}} 現在可以從 `/read_markers` 發送 `m.read.private` 回執。

閱讀標記 API 還可以在設置完全閱讀標記位置的同一操作中更新使用者的閱讀回執（`m.read` 或 `m.read.private`）位置。這是因為閱讀回執和閱讀標記通常同時更新，因此用戶端可能希望節省額外的 HTTP 調用。提供 `m.read` 和/或 `m.read.private` 執行與請求 [`/receipt/{receiptType}/{eventId}`](#post_matrixclientv3roomsroomidreceiptreceipttypeeventid) 相同的任務。

{{% http-api spec="client-server" api="read_markers" %}}

#### 伺服器行為

伺服器必須阻止用戶端直接在房間帳戶資料中設置 `m.fully_read`。伺服器還必須確保它對 `/read_markers` 請求中 `m.read` 和 `m.read.private` 的存在的處理與它對 [`/receipt/{receiptType}/{eventId}`](#post_matrixclientv3roomsroomidreceiptreceipttypeeventid) 請求的處理相同。

由於 `/read_markers` 的請求而更新 `m.fully_read` 事件時，伺服器必須通過事件流（例如：`/sync`）將更新後的帳戶資料事件發送給用戶端，前提是滿足任何適用的過濾器。

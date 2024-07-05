### 房間歷史可見性

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/history_visibility.md)

此模組增加了控制房間中先前事件可見性的支持。

除 `world_readable` 外的所有情況下，用戶需要加入房間才能查看該房間中的事件。一旦他們加入了房間，他們將獲得對房間中一部分事件的訪問權限。如何選擇這個子集由下面概述的 `m.room.history_visibility` 事件控制。在用戶離開房間後，他們可以看到他們在離開房間之前被允許看到的任何事件，但不能看到他們離開後收到的事件。

`m.room.history_visibility` 事件有四個選項：

-   `world_readable` - 當這是 `m.room.history_visibility` 值時，任何參與的主伺服器都可以與任何人分享所有事件，無論他們是否曾經加入過房間。
-   `shared` - 先前的事件始終對新加入的成員可見。房間中的所有事件都是可訪問的，即使是在成員不是房間一部分時發送的事件。
-   `invited` - 事件從新成員被邀請的時刻起對其可見。當成員的狀態變為 `invite` 或 `join` 以外的狀態時，事件停止可訪問。
-   `joined` - 事件從新成員加入房間的時刻起對其可見。當成員的狀態變為 `join` 以外的狀態時，事件停止可訪問。

{{% boxes/warning %}}
這些選項在事件*發送*時應用。檢查是在相關事件被添加到 DAG 時，根據當時 `m.room.history_visibility` 事件的狀態進行的。這意味著客戶端不能在事後選擇向新用戶顯示或隱藏歷史記錄，如果當時的設置更具限制性。
{{% /boxes/warning %}}

#### 事件

```
{{% event event="m.room.history_visibility" %}}
```

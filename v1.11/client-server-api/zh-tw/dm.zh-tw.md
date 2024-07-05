### 私人訊息

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/dm.md)

Matrix 上的所有通信都發生在房間內。有時希望為用戶提供直接與特定人交談的概念。本模組定義了一種將某些房間標記為與給定人的「私人聊天」的方式。這並不限制聊天只能在兩個人之間進行，因為這會排除自動化的「機器人」用戶，甚至是能夠在用戶缺席時代表用戶回答私人訊息的「個人助理」。

房間不一定被所有房間成員視為「私人」，但存在一種信號機制來向被邀請者傳播聊天是否為「私人」的信息。

#### 事件

{{% event event="m.direct" %}}

#### 客戶端行為

要與另一個用戶開始私人聊天，邀請用戶的客戶端應在 [`/createRoom`](/client-server-api/#post_matrixclientv3createroom) 中設置 `is_direct` 標誌。當用戶遵循的流程是其意圖直接與另一個人交談，而不是將該人帶入共享房間時，客戶端應該這樣做。例如，點擊某人的個人資料圖片旁邊的「開始聊天」會暗示應設置 `is_direct` 標誌。

被邀請者的客戶端可以使用 [m.room.member](#mroommember) 事件中的 `is_direct` 標誌自動將房間標記為私人聊天，但這不是必需的：例如，它可能會提示用戶，或完全忽略該標誌。

邀請客戶端和被邀請者的客戶端都應通過使用 [`/user/<user_id>/account_data/<type>`](/client-server-api/#put_matrixclientv3useruseridaccount_datatype) 存儲 `m.direct` 事件來記錄房間是私人聊天的事實。

#### 伺服器行為

當 [`/createRoom`](/client-server-api/#post_matrixclientv3createroom) 中給出 `is_direct` 標誌時，主伺服器必須在 [`/createRoom`](/client-server-api/#post_matrixclientv3createroom) 調用中邀請的任何用戶的邀請成員事件中設置 `is_direct` 標誌。

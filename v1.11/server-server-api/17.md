# Typing Notifications

這段內容描述了Matrix協議中的打字通知(Typing Notifications)功能。以下是主要內容的概述:

API: m.typing

用途: 在聯邦網絡中傳播用戶的打字狀態

特色:

1. 允許服務器將用戶的打字狀態通知給房間中的其他服務器
2. 接收服務器應驗證用戶是否在房間中,以及是否屬於發送服務器

請求內容 (EDU):

- edu_type: "m.typing" (必填)
- content: 打字通知內容 (必填)

打字通知內容:

- room_id: 用戶打字狀態更新的房間ID (必填)
- typing: 用戶是否正在打字 (布爾值,必填)
- user_id: 打字狀態變更的用戶ID (必填)

響應:
此API不需要響應,它是一個單向的通知機制。

這個API使得不同服務器上的用戶可以即時看到其他用戶的打字狀態,增強了跨服務器聊天的即時性和互動性。接收服務器需要確保只處理來自合法用戶和正確房間的打字通知。

<!-- markdownlint-disable -->
<h1> `m.typing` </h1>
<!-- markdownlint-enable -->

用戶在房間中的正在輸入通知 EDU。

m.typing
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Typing Notification]` | **Required:** 輸入通知。 |
| `edu_type` | `string` | **Required:** 字串 `m.typing`。必須是：`[m.typing]` 之一。 |

Typing Notification
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `room_id` | `string` | **Required:** 用戶的輸入狀態已更新的房間。 |
| `typing` | `boolean` | **Required:** 用戶是否在房間中輸入。 |
| `user_id` | `string` | **Required:** 其輸入狀態已更改的用戶 ID。 |

<!-- markdownlint-disable -->
<h2> Example</h2>
<!-- markdownlint-enable -->

```json
{
  "content": {
    "room_id": "!somewhere:matrix.org",
    "typing": true,
    "user_id": "@john:matrix.org"
  },
  "edu_type": "m.typing"
}
```

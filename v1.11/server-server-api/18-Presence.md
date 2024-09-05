# Presence

1. 存在感(Presence)的伺服器 API 完全基於 EDU (Ephemeral Data Unit) 的交換,不涉及 PDU 或聯邦查詢。
2. 伺服器應只發送接收伺服器可能感興趣的用戶的存在感更新,例如共享房間的用戶。
3. 主要 EDU 類型是 "m.presence",用於表示發送方伺服器用戶的存在感更新。
4. m.presence EDU 的內容包含:
   - push: 一個存在感更新列表
   - 每個更新包含:用戶ID、在線狀態、最後活動時間、當前是否活躍、狀態消息等信息
5. 存在感狀態可以是:離線(offline)、不可用(unavailable)、在線(online)
6. last_active_ago 表示用戶最後活動距現在的毫秒數
7. currently_active 表示用戶最近幾分鐘內可能正在與客戶端互動
8. status_msg 是可選的描述性狀態消息

伺服器的 Presence API 完全基於以下 EDU 的交換。此過程不涉及 PDU 或 Federation Queries。

伺服器應該只為接收伺服器感興趣的使用者發送 presence 更新，例如接收伺服器與某個使用者共享同一個房間時。

<!-- markdownlint-disable -->
<h1>`m.presence`</h1>
<!-- markdownlint-enable -->

---

代表發送 homeserver 使用者的 presence 更新的 EDU。

`m.presence`
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Presence Update]` | **必填項:** Presence 更新與請求。 |
| `edu_type` | `string` | **必填項:** 字符串 `m.presence`，其中之一: `[m.presence]`。 |
<!-- markdownlint-enable -->

Presence Update
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `push` | `[User Presence Update]` | **必填項:** 接收伺服器可能感興趣的 presence 更新列表。 |

User Presence Update
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `currently_active` | `boolean` | 如果使用者很可能正在與其客戶端互動，則為 True。這可能是由於使用者在最近幾分鐘內有 `last_active_ago` 記錄。默認值為 false。 |
| `last_active_ago` | `integer` | **必填項:** 自使用者上次進行某些操作以來經過的毫秒數。 |
| `presence` | `string` | **必填項:** 使用者的 presence 狀態。可選之一: `[offline, unavailable, online]`。 |
| `status_msg` | `string` | Presence 狀態的可選描述。 |
| `user_id` | `string` | **必填項:** 此 presence EDU 所屬的使用者 ID。 |
<!-- markdownlint-enable -->

## 範例

```json
{
  "content": {
    "push": [
      {
        "currently_active": true,
        "last_active_ago": 5000,
        "presence": "online",
        "status_msg": "Making cupcakes",
        "user_id": "@john:matrix.org"
      }
    ]
  },
  "edu_type": "m.presence"
}
```

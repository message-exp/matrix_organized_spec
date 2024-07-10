# 6. EDUs

與 PDUs 相比，EDUs 沒有 ID、房間 ID 或“先前”ID 列表。它們旨在用作非持續性資料，例如使用者狀態、正在輸入通知等。

**`Ephemeral Data Unit`**

臨時資料單元。

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `object` | **Required:** 臨時消息的內容。 |
| `edu_type` | `string` | **Required:** 臨時消息的類型。 |

---

範例

```json
{
  "content": {
    "key": "value"
  },
  "edu_type": "m.presence"
}
```

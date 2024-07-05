### 使用者和房間提及

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/mentions.md)

{{% changed-in v="1.7" %}}

此模組允許使用者在房間事件中"提及"其他使用者和房間。這主要用作指示接收者應該收到關於該事件的通知。
這是通過在事件的 `m.mentions` 內容屬性中包含元數據來引用被提及的實體來實現的。

`m.mentions` 定義如下：

{{% definition path="api/client-server/definitions/m.mentions" %}}

事件的內容將如下所示：

```json
{
    "body": "你好 Alice！",
    "msgtype": "m.text",
    "format": "org.matrix.custom.html",
    "formatted_body": "你好 <a href='https://matrix.to/#/@alice:example.org'>Alice</a>！",
    "m.mentions": {
        "user_ids": ["@alice:example.org"]
    }
}
```

此外，請參見 [`.m.rule.is_user_mention`](#_m_rule_is_user_mention) 和
[`.m.rule.is_room_mention`](#_m_rule_is_room_mention) 推送規則。
使用者不應將自己的 Matrix ID 添加到 `m.mentions` 屬性中，因為外發消息不能自我通知。

{{% boxes/warning %}}
如果加密事件在其有效載荷中包含 `m.mentions`，它應該正常加密。要在加密房間中正確處理提及，必須先解密事件。請參見[接收通知](#receiving-notifications)。
{{% /boxes/warning %}}

請注意，為了向後兼容，如果事件的 `body` 包含使用者的顯示名稱或 ID，諸如 [`.m.rule.contains_display_name`](#_m_rule_contains_display_name)、
[`.m.rule.contains_user_name`](#_m_rule_contains_user_name) 和
[`.m.rule.roomnotif`](#_m_rule_roomnotif) 等推送規則將繼續匹配。為避免意外通知，
**建議客戶端在每個事件上包含 `m.mentions` 屬性**。
（如果沒有要包含的提及，它可以是一個空對象。）

{{% boxes/rationale %}}
在規範的先前版本中，提及使用者是通過在事件的純文本 `body` 中包含使用者的顯示名稱或其 Matrix ID 的本地部分來完成的，而房間提及是通過包含字符串 "@room" 來完成的。這容易導致混淆和錯誤的行為。
{{% /boxes/rationale %}}

#### 客戶端行為

雖然可以靜默提及使用者，但建議在 [m.room.message](#mroommessage) 事件的 HTML 正文中包含
[Matrix URI](/appendices/#uris)。這僅適用於 `msgtype` 為
`m.text`、`m.emote` 或 `m.notice` 的 [m.room.message](#mroommessage) 事件。事件的 `format` 必須為
`org.matrix.custom.html`，因此需要 `formatted_body`。

在將代表提及的 `Matrix URI` 添加到要發送的事件時，客戶端應使用以下指導原則：

-   鏈接到使用者時，使用使用者可能有歧義的顯示名稱作為錨點文本。如果使用者沒有顯示名稱，則使用使用者的 ID。
-   鏈接到房間時，使用房間的規範別名。如果房間沒有規範別名，優先使用房間列出的別名之一。如果找不到別名，則回退到房間 ID。在所有情況下，使用被鏈接的別名/房間 ID 作為錨點文本。

錨點的文本組件應在事件的 `body` 中使用，通常會表示鏈接的位置，如上面的示例所示。

客戶端應該以不同於其他元素的方式顯示提及。例如，可以通過改變提及的背景顏色來表示它與普通鏈接不同。

如果當前使用者在消息中被提及，客戶端應該以不同於其他提及的方式顯示該提及，例如使用紅色背景來表示使用者被提及。請注意，
可能在事件中不包含使用者的 `Matrix URI` 而仍然提及使用者。

當被點擊時，提及應該將使用者導航到適當的使用者或房間信息。
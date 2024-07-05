### 事件註解和反應

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/event_annotations.md)

{{% added-in v="1.7" %}}

#### `m.annotation` 關係類型

註解是使用[事件關係](#forming-relationships-between-events)且 `rel_type` 為 `m.annotation` 的事件。

註解通常用於"反應"：例如，如果用戶想對一個事件做出豎起大拇指的反應，那麼客戶端會發送一個帶有相應表情符號（👍）的註解事件。另一個潛在用途是允許機器人發送指示命令成功或失敗的事件。

除了正常的 `event_id` 和 `rel_type` 屬性外，帶有 `rel_type: m.annotation` 的 `m.relates_to` 屬性應包含一個 `key`，用於指示所應用的註解。例如，當使用表情符號反應時，key 包含所使用的表情符號。

以下是 `m.annotation` 關係的示例：

```json
"m.relates_to": {
    "rel_type": "m.annotation",
    "event_id": "$some_event_id",
    "key": "👍"
}
```

{{% boxes/note %}}
任何 `type` 的事件都有資格進行註解，包括狀態事件。
{{% /boxes/note %}}

#### 事件

```
{{% event event="m.reaction" %}}
```

#### 客戶端行為 {id="annotations-client-behaviour"}

註解的目的是被計數，而不是單獨顯示。客戶端必須對它們觀察到的每個事件的給定事件 `type` 和註解 `key` 的註解數量進行計數；這些計數通常與時間軸中的事件一起顯示。

在進行此計數時：

 * 每個事件 `type` 和註解 `key` 通常應該分別計數，但是否這樣做是一個實現決定。

 * 應從計數中排除[被忽略用戶](#ignoring-users)發送的註解事件。

 * 來自同一用戶的多個相同註解（即，具有相同事件 `type` 和註解 `key` 的事件）（即，具有相同 `sender` 的事件）應被視為單個註解。

 * 實現應忽略任何引用具有 `m.relates_to` 且 `rel_type: m.annotation` 或 `rel_type: m.replace` 的事件的註解事件。換句話說，不可能對[替換事件](#event-replacements)或註解進行註解。註解應該引用原始事件。

 * 當註解被撤回時，它將從計數中移除。

{{% boxes/note %}}
無法編輯反應，因為替換事件不會更改 `m.relates_to`（參見 [應用 `m.new_content`](#applying-mnew_content)），並且 `m.reaction` 中沒有其他有意義的內容。如果用戶希望更改他們的反應，應該撤回原始反應並發送新的反應來替代。
{{% /boxes/note %}}

{{% boxes/note %}}
`m.reaction` 中的 `key` 字段可以是任何字符串，因此客戶端必須注意以合理的方式呈現長反應。例如，客戶端可以省略過長的反應。
{{% /boxes/note %}}

#### 伺服器行為

##### 避免重複註解

主伺服器應該防止用戶對給定事件發送具有相同事件 `type` 和註解 `key` 的第二個註解（除非第一個事件已被撤回）。

嘗試發送此類註解的行為應被拒絕，並返回 400 錯誤和錯誤代碼 `M_DUPLICATE_ANNOTATION`。

請注意，這並不能保證重複的註解不會通過聯邦到達。客戶端負責在[計算註解](#annotations-client-behaviour)時對接收到的註解進行去重。

##### 伺服器端 `m.annotation` 關係的聚合

`m.annotation` 關係*不*由伺服器[聚合](#aggregations-of-child-events)。換句話說，`m.annotation` 不包含在 `m.relations` 屬性中。

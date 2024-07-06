### 參考關係

{{% added-in v="1.5" %}}

通過使用`rel_type`為`m.reference`的[關係](#forming-relationships-between-events)可以泛型地引用另一個事件。這種引用沒有隱含的含義,通常是依賴上下文的。一個例子是[密鑰驗證框架](#key-verification-framework),它使用參考關係將不同的事件與特定的驗證嘗試相關聯。

{{% boxes/note %}}
希望使用主題或回覆的用戶端應該使用參考以外的其他關係類型。參考通常用於關聯數據而不是訊息。
{{% /boxes/note %}}

#### 伺服器行為

##### `m.reference`的伺服器端聚合

`m.reference`關係的[聚合](#aggregations-of-child-events)格式包含一個單一的`chunk`屬性,它列出了所有`m.reference`該事件(父事件)的事件。目前,`chunk`中的事件只包含一個`event_id`字段。

例如,給定一個具有以下`m.reference`關係的事件:

```json
{
  "content": {
    "m.relates_to": {
      "rel_type": "m.reference",
      "event_id": "$another_event"
    }
    // 其他必要的內容字段
  }
  // 事件所需的其他字段
}
```

聚合將類似於以下內容:

```json
{
  "m.reference": {
    "chunk": [
      { "event_id": "$one" },
      { "event_id": "$two" }
    ]
  }
}
```

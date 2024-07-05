### 事件上下文

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/event_context.md)

此 API 返回指定事件之前和之後發生的一些事件。這允許客戶端獲取圍繞事件的上下文。

#### 客戶端行為

有一個用於檢索事件上下文的單一 HTTP API，如下所述。

```
{{% http-api spec="client-server" api="event_context" %}}
```

#### 安全考慮

伺服器必須只返回用戶有權查看的結果。
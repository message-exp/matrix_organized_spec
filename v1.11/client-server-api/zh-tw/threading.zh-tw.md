### 討論串

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/threading.md)

{{% added-in v="1.4" %}}

討論串允許使用者在房間中視覺上分支他們的對話。通常主要用於房間討論多個主題時，討論串提供了比傳統[豐富回覆](#rich-replies)更多的通信組織，這是傳統回覆有時無法提供的。

用戶端應該以不同於時間線中常規消息或回覆的方式呈現討論串，例如通過提供一些關於討論串中正在發生的事情的上下文，但將完整的對話歷史隱藏在一個展開項後面。

討論串使用 `rel_type` 為 `m.thread` 來建立，並引用*討論串根*（討論串事件所指的主時間線事件）。無法從本身是事件關係子事件的事件（即具有帶有 `rel_type` 屬性的 `m.relates_to` 屬性的事件 - 參見[關係類型](#relationship-types)）創建討論串。因此，也不可能嵌套討論串。

與豐富回覆鏈不同，討論串中的所有事件都引用討論串根，而不是最近的消息。

作為一個實際例子，以下表示一個討論串及其形成方式：

```json
{
  // 無關字段已排除
  "type": "m.room.message",
  "event_id": "$alice_hello",
  "sender": "@alice:example.org",
  "content": {
    "msgtype": "m.text",
    "body": "你好世界！你好嗎？"
  }
}
```

```json
{
  // 無關字段已排除
  "type": "m.room.message",
  "event_id": "$bob_hello",
  "sender": "@bob:example.org",
  "content": {
    "m.relates_to": {
      "rel_type": "m.thread",
      "event_id": "$alice_hello"
    },
    "msgtype": "m.text",
    "body": "我很好，謝謝！你呢？"
  }
}
```

```json
{
  // 無關字段已排除
  "type": "m.room.message",
  "event_id": "$alice_reply",
  "sender": "@alice:example.org",
  "content": {
    "m.relates_to": {
      "rel_type": "m.thread",
      "event_id": "$alice_hello" // 注意：始終引用*討論串根*
    },
    "msgtype": "m.text",
    "body": "我很好！謝謝你的關心。"
  }
}
```

如所示，任何沒有 `rel_type` 的事件都可以通過簡單地使用 `m.thread` 關係引用它來成為討論串根。

#### 對於不支持討論串的用戶端的回退

了解如何處理討論串的用戶端應該直接這樣做，但可能不了解討論串的用戶端（由於年代或範圍）可能無法有效地向其用戶呈現對話歷史。

為了解決這個問題，了解討論串的用戶端發送的事件應該包括[豐富回覆](#rich-replies)元數據，以嘗試形成對話的回覆鏈表示。這種表示對於大量使用討論串的房間來說並不理想，但允許用戶了解正在討論的內容與房間中其他消息的關係。

這種表示通過合併兩種關係並設置一個新的 `is_falling_back` 標誌為 `true` 來實現。

```json
// 在事件的內容中...
"m.relates_to": {
  // m.thread 關係結構
  "rel_type": "m.thread",
  "event_id": "$root",

  // 豐富回覆結構
  "m.in_reply_to": {
    // 用戶端在討論串中已知的最近消息。
    // 這應該是有很大機會被其他用戶端渲染的內容，
    // 例如 `m.room.message` 事件。
    "event_id": "$target"
  },

  // 表示這是具有回覆回退的討論串的標誌
  "is_falling_back": true
}
```

對於以這種方式表示的 `m.room.message` 事件，不指定[回覆回退](#fallbacks-for-rich-replies)。這允許了解討論串的用戶端在 `is_falling_back` 為 `true` 時完全丟棄 `m.in_reply_to` 對象。

{{% boxes/note %}}
非常了解討論串的用戶端（它們不渲染討論串，但知道規範中存在此功能）可以將對具有 `rel_type` 為 `m.thread` 的事件的豐富回覆視為討論串回覆，以保持討論串用戶端側的對話連續性。

為此，從被回覆的事件中複製 `event_id`（討論串根），添加 `m.in_reply_to` 元數據，並將 `is_falling_back: true` 添加到 `m.relates_to` 中。
{{% /boxes/note %}}

#### 討論串內的回覆

在[對於不支持討論串的用戶端的回退](#fallback-for-unthreaded-clients)部分，一個新的 `is_falling_back` 標誌被添加到 `m.relates_to` 中。當未提供時，此標誌默認為 `false`，這也允許討論串消息本身包含回覆。

除了 `is_falling_back` 為 `false`（或未指定）外，不支持討論串的用戶端的回退用於在討論串內創建回覆：用戶端應相應地渲染事件。

#### 伺服器行為

##### `m.thread` 關係的驗證

伺服器應該拒絕試圖從具有 `m.relates_to` 屬性的事件開始討論串的用戶端請求。如果用戶端試圖針對本身具有 `m.relates_to` 屬性的事件，則應收到 HTTP 400 錯誤回應，並附帶適當的錯誤消息，符合[標準錯誤回應](#standard-error-response)結構。

{{% boxes/note %}}
目前沒有針對此情況的特定錯誤代碼：伺服器應使用 `M_UNKNOWN` 以及 HTTP 400 狀態代碼。
{{% /boxes/note %}}

##### `m.thread` 關係的伺服器端聚合

由於討論串始終引用討論串根，一個事件可以有多個"子"事件，然後形成討論串本身。這些事件應該由伺服器[聚合](#aggregations-of-child-events)。

討論串的聚合包括一些關於用戶在討論串中的參與、討論串中事件的大致數量（據伺服器所知）以及討論串中最新事件（拓撲上）的信息。

與任何其他子事件聚合一樣，`m.thread` 聚合包含在討論串根的 `unsigned` 中的 `m.relations` 屬性下。例如：

```json
{
  "event_id": "$root_event",
  // 無關字段未顯示
  "unsigned": {
    "m.relations": {
      "m.thread": {
        "latest_event": {
          // 討論串中最新事件的序列化副本。
          // 為簡潔起見，此處未顯示某些字段。
          "event_id": "$message",
          "sender": "@alice:example.org",
          "room_id": "!room:example.org",
          "type": "m.room.message",
          "content": {
            "msgtype": "m.text",
            "body": "耶！討論串！"
          },
          "unsigned": {
            "m.relations": {
              // ...
            }
          }
        },
        "count": 7,
        "current_user_participated": true
      }
    }
  }
}
```

`latest_event` 是討論串中最新的事件（在伺服器的拓撲中），由未[被忽略的用戶](#ignoring-users)發送。

請注意，如上例所示，`latest_event` 的子事件本身應該被聚合並包含在該事件的 `m.relations` 下。伺服器應該小心避免循環，儘管由於不允許 `m.thread` 針對具有 `m.relates_to` 屬性的事件，目前不可能出現循環。

`count` 只是使用 `m.thread` 作為 `rel_type` 指向目標事件的事件數量。它不包括[被忽略用戶](#ignoring-users)發送的事件。

當認證用戶是以下情況之一時，`current_user_participated` 為 `true`：
1. 討論串根事件的 `sender`。
2. 使用 `rel_type` 為 `m.thread` 引用討論串根的事件的 `sender`。

#### 查詢房間中的討論串

用戶端可以使用 [`GET /relations/{threadRootId}/m.thread`](#get_matrixclientv1roomsroomidrelationseventidreltype) 來獲取討論串中的所有事件，但是獲取房間中的所有討論串是通過專用 API 完成的：

{{% http-api spec="client-server" api="threads_list" %}}

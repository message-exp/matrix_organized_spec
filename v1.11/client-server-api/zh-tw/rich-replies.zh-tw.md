### 富文本回覆

{{% changed-in v="1.3" %}}

富文本回覆是一種特殊的[關係](#forming-relationships-between-events)，它有效地引用了被參考事件，供用戶端按其意願進行渲染/處理。它們通常與 [`m.room.message`](#mroommessage) 事件一起使用。

{{% boxes/note %}}
在規範的 v1.3 版本之前，富文本回覆僅限於可以表示 HTML 格式正文的 `m.room.message` 事件。從 v1.3 版本開始，通過取消包含 HTML 格式正文的要求，這一限制已擴展到*所有*事件類型。

此外，從 v1.3 版本開始，富文本回覆可以參考任何其他事件類型。之前，富文本回覆只能參考另一個 `m.room.message` 事件。
{{% /boxes/note %}}

在可能的情況下，事件應該包括[後備表示](#fallbacks-for-rich-replies)，以允許不渲染富文本回覆的用戶端仍能看到看似引用回覆的內容。

雖然富文本回覆與另一個事件形成關係，但它們不使用 `rel_type` 來創建這種關係。相反，使用名為 `m.in_reply_to` 的子鍵來描述回覆的關係，保留 `m.relates_to` 的其他屬性來描述事件的主要關係。這意味著如果一個事件僅僅是對另一個事件的回覆，沒有進一步的關係，`m.relates_to` 的 `rel_type` 和 `event_id` 屬性就變成了*可選的*。

一個回覆的例子如下：

```json5
{
  "content": {
    "m.relates_to": {
      "m.in_reply_to": {
        "event_id": "$another_event"
      }
    },
    "body": "這聽起來是個好主意！"
  },
  // 事件所需的其他欄位
}
```

請注意，`m.in_reply_to` 對象的 `event_id` 與直接放在 `m.relates_to` 下的要求相同。

#### 富文本回覆的後備方案

某些用戶端可能不支持富文本回覆，因此需要使用後備方案。不支持富文本回覆的用戶端應該像富文本回覆不特殊一樣渲染事件。

支持富文本回覆的用戶端應該在回覆中提供後備格式，並且必須在渲染回覆前去除後備內容。每種 `msgtype` 的具體後備文本不同，但 `body` 的一般格式為：

```text
> <@alice:example.org> 這是原始正文的第一行
> 這是第二行

這是回覆的內容
```

如果存在 `formatted_body` 且使用 `org.matrix.custom.html` 的相關 `format`，應該使用以下模板：

```html
<mx-reply>
  <blockquote>
    <a href="https://matrix.to/#/!somewhere:example.org/$event:example.org">回覆</a>
    <a href="https://matrix.to/#/@alice:example.org">@alice:example.org</a>
    <br />
    <!-- 這裡是相關事件的 HTML 內容。 -->
  </blockquote>
</mx-reply>
這是回覆的內容。
```

如果相關事件沒有 `formatted_body`，應該考慮在編碼任何 HTML 特殊字符後使用事件的 `body`。注意，兩個錨點中的 `href` 都使用 [matrix.to URI](/appendices#matrixto-navigation)。

##### 去除後備內容

支持富文本回覆的用戶端必須在渲染事件之前去除事件中的後備內容。這是因為後備中提供的文本不能被信任為事件的準確表示。移除後備內容後，建議用戶端以類似於後備表示的方式呈現 `m.in_reply_to` 引用的事件，儘管用戶端在用戶界面上有創作自由。用戶端應該優先選擇 `formatted_body` 而不是 `body`，就像處理其他 `m.room.message` 事件一樣。

要去除 `body` 中的後備內容，用戶端應該遍歷字符串的每一行，移除任何以後備前綴（"&gt; "，包括空格，不帶引號）開頭的行，並在遇到沒有前綴的行時停止。這個前綴被稱為"後備前綴序列"。

要去除 `formatted_body` 中的後備內容，用戶端應該移除整個 `mx-reply` 標籤。

##### `m.text`、`m.notice` 和未識別消息類型的後備方案

使用前綴序列，相關事件 `body` 的第一行應該以用戶 ID 為前綴，然後每行都以後備前綴序列為前綴。例如：

```text
> <@alice:example.org> 這是第一行
> 這是第二行

這是回覆
```

`formatted_body` 使用本節前面定義的模板。

##### `m.emote` 的後備方案

類似於 `m.text` 的後備方案，每行都以後備前綴序列為前綴。但是應該在用戶 ID 之前插入一個星號，如下所示：

```text
> * <@alice:example.org> 感覺今天會是個美好的一天

這是回覆
```

`formatted_body` 的模板有一個細微的差別，其中星號也插入在用戶 ID 之前：

```html
<mx-reply>
  <blockquote>
    <a href="https://matrix.to/#/!somewhere:example.org/$event:example.org">回覆</a>
    * <a href="https://matrix.to/#/@alice:example.org">@alice:example.org</a>
    <br />
    <!-- 這裡是相關事件的 HTML 內容。 -->
  </blockquote>
</mx-reply>
這是回覆的內容。
```

##### `m.image`、`m.video`、`m.audio` 和 `m.file` 的後備方案

相關事件的 `body` 將是一個文件名，可能不太具有描述性。此外，相關事件不應該在 `content` 中有 `format` 或 `formatted_body` - 如果事件確實有 `format` 和/或 `formatted_body`，這些欄位應該被忽略。由於單獨的文件名可能不具描述性，相關事件的 `body` 應該被視為 `"sent a file."`，使得輸出看起來類似於以下內容：

```text
> <@alice:example.org> 發送了一個文件。

這是回覆
```
```html
<mx-reply>
  <blockquote>
    <a href="https://matrix.to/#/!somewhere:example.org/$event:example.org">回覆</a>
    <a href="https://matrix.to/#/@alice:example.org">@alice:example.org</a>
    <br />
    發送了一個文件。
  </blockquote>
</mx-reply>
這是回覆的內容。
```

對於 `m.image`，文本應為 `"發送了一張圖片。"`。對於 `m.video`，文本應為 `"發送了一個視頻。"`。對於 `m.audio`，文本應為 `"發送了一個音頻文件。"`。

#### 提及被回覆的用戶

為了通知用戶有關回覆，可能需要包括被回覆事件的 `sender` 和該事件中提到的任何用戶。有關更多資訊，請參見[用戶和房間提及](#user-and-room-mentions)。

一個包括提及原始發送者和其他用戶的例子：

```json5
{
  "content": {
    "m.relates_to": {
      "m.in_reply_to": {
        "event_id": "$another_event"
      }
    },
    "body": "這聽起來是個好主意！",
    "m.mentions": {
      "user_ids": [
        // $another_event 的發送者。
        "@alice:example.org",
        // 從 $another_event 的 m.mentions 屬性複製的另一個 Matrix ID。
        "@bob:example.org"
      ]
    }
  },
  // 事件所需的其他欄位
}
```

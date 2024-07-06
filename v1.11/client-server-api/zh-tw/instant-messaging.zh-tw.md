### 即時通訊

此模組添加了向房間發送人類可讀訊息的支持。
它還添加了支持將人類可讀資訊與房間本身相關聯的功能，如房間名稱和主題。

#### 事件

{{% event event="m.room.message" desired_example_name="m.room.message$m.text" %}}

{{% event event="m.room.name" %}}

{{% event event="m.room.topic" %}}

{{% event event="m.room.avatar" %}}

{{% event event="m.room.pinned_events" %}}

##### m.room.message 訊息類型

每個 [m.room.message](#mroommessage) 必須有一個 `msgtype` 鍵，用於識別正在發送的訊息類型。每種類型都有自己的必需和可選鍵，如下所述。如果用戶端無法顯示給定的 `msgtype`，則應該顯示後備的純文本 `body` 鍵。

某些訊息類型在事件內容中支持 HTML，用戶端應優先顯示（如果可用）。目前 `m.text`、`m.emote`、`m.notice`、`m.image`、`m.file`、`m.audio`、`m.video` 和 `m.key.verification.request` 支持額外的 `format` 參數 `org.matrix.custom.html`。當此字段存在時，必須提供帶有 HTML 的 `formatted_body`。HTML 的純文本版本應該在 `body` 中提供。

> [!NOTE]
> [Changed in v1.10]
> 在之前的規範版本中，`format` 和 `formatted` 字段僅限於 `m.text`、`m.emote`、`m.notice` 和 `m.key.verification.request`。此列表擴展到包括 `m.image`、`m.file`、`m.audio` 和 `m.video` 用於[媒體標題](#media-captions)。

用戶端應限制它們渲染的 HTML 以避免跨站腳本攻擊、HTML 注入和類似攻擊。強烈建議的 HTML 標籤集合為：`del`、`h1`、`h2`、`h3`、`h4`、`h5`、`h6`、`blockquote`、`p`、`a`、`ul`、`ol`、`sup`、`sub`、`li`、`b`、`i`、`u`、`strong`、`em`、`s`、`code`、`hr`、`br`、`div`、`table`、`thead`、`tbody`、`tr`、`th`、`td`、`caption`、`pre`、`span`、`img`、`details`、`summary`。

> [!NOTE]
> [Added-in v1.10]
> 當 HTML 特性在 [WHATWG HTML 活標準](https://html.spec.whatwg.org/multipage/) 中被棄用時，可以在不需要[規範變更提案](/proposals)的情況下將其棄用並替換為現代等效物。

> [!NOTE]
> [Changed-in v1.10]
> 在之前的規範版本中，建議使用 `font` 標籤，並帶有 `data-mx-bg-color`、`data-mx-color` 和 `color` 屬性。現在在新訊息中，此標籤已被棄用，改為使用帶有 `data-mx-bg-color` 和 `data-mx-color` 屬性的 `span` 標籤。

不應允許這些標籤上的所有屬性，因為它們可能是其他干擾嘗試的途徑，例如添加 `onclick` 處理程序或過大的文本。用戶端應只允許下面列出的標籤屬性。對於列出 `data-mx-bg-color` 和 `data-mx-color` 的地方，用戶端應將值（一個 `#` 字符後跟 6 字符的十六進制顏色代碼）轉換為標籤的適當 CSS/屬性。

| 標籤   | 允許的屬性                                                                                                                                 |
|--------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `span` | `data-mx-bg-color`、`data-mx-color`、`data-mx-spoiler`（見[劇透訊息](#spoiler-messages)）、`data-mx-maths`（見[數學訊息](#mathematical-messages)） |
| `a`    | `name`、`target`、`href`（提供的值不是相對的，並且具有與以下之一匹配的方案：`https`、`http`、`ftp`、`mailto`、`magnet`）                    |
| `img`  | `width`、`height`、`alt`、`title`、`src`（提供的是 [Matrix 內容（`mxc://`）URI](#matrix-content-mxc-uris)）                                  |
| `ol`   | `start`                                                                                                                                    |
| `code` | `class`（僅用於以 `language-` 開頭的類，用於語法高亮）                                                                                      |
| `div`  | `data-mx-maths`（見[數學訊息](#mathematical-messages)）                                                                                     |

此外，網頁用戶端應確保所有 `a` 標籤都獲得 `rel="noopener"`，以防止目標頁面引用用戶端的標籤/窗口。

標籤的嵌套深度不得超過 100 級。用戶端應只支持它們可以渲染的標籤子集，在可能的情況下退回到標籤的其他表示形式。例如，用戶端可能無法正確渲染表格，而可以退回到渲染製表符分隔的文本。

除了不渲染不安全的 HTML 外，用戶端也不應在事件中發出不安全的 HTML。同樣，用戶端不應生成不需要的 HTML，例如由於富文本編輯器而在文本周圍添加多餘的段落標籤。事件中包含的 HTML 應該在其他方面是有效的，例如具有適當的結束標籤、適當的屬性（考慮到本規範中定義的自定義屬性），以及通常有效的結構。

一個特殊的標籤 `mx-reply` 可能出現在富文本回覆中（如下所述），如果且僅當該標籤作為 `formatted_body` 中的第一個標籤出現時，應該允許使用。該標籤不能嵌套，也不能位於樹中的另一個標籤之後。由於該標籤包含 HTML，預期 `mx-reply` 有一個配對的結束標籤，應該像 `div` 一樣對待。支持富文本回覆的用戶端最終會剝離該標籤及其內容，因此可能希望完全排除該標籤。

> [!NOTE]
> 規範的未來迭代將支持更強大和可擴展的訊息格式選項，例如提案 [MSC1767](https://github.com/matrix-org/matrix-spec-proposals/pull/1767)。

{{% msgtypes %}}

#### 用戶端行為

用戶端應驗證傳入事件的結構，以確保預期的鍵存在且類型正確。用戶端可以丟棄格式錯誤的事件或向用戶顯示佔位符訊息。必須從用戶端中刪除已編輯的 `m.room.message` 事件。這可以用佔位符文本（例如"[已編輯]"）替換，或者可以從訊息視圖中完全刪除已編輯的訊息。

具有附件的事件（例如 `m.image`、`m.file`）應使用[內容存儲庫模組](#content-repository)（如果可用）上傳。結果的 `mxc://` URI 然後可以用在 `url` 鍵中。

用戶端可以在 `info.thumbnail_url` 鍵下包含附件的用戶端生成的縮略圖。縮略圖也應該是 `mxc://` URI。顯示帶有附件的事件的用戶端可以使用用戶端生成的縮略圖，或者要求其家伺服器使用[內容存儲庫模組](#content-repository)從原始附件生成縮略圖。

##### 發送訊息時的建議

在發送失敗的情況下，用戶端應使用指數退避算法在一定時間 T 內重試請求。建議 T 不超過 5 分鐘。在此時間之後，用戶端應停止重試並將訊息標記為"未發送"。用戶應能夠手動重新發送未發送的訊息。

用戶可能一次輸入幾條訊息並快速連續發送它們。用戶端應保持用戶發送它們的順序。這意味著用戶端應等待前一個請求的回應，然後再發送下一個請求。這可能導致頭部阻塞。為了減少頭部阻塞的影響，用戶端應該為每個房間使用一個隊列，而不是一個全局隊列，因為排序只在單個房間內相關，而不是在房間之間。

##### 本地回顯

當用戶按下"發送"按鈕時，訊息應立即出現在訊息視圖中。即使訊息仍在發送中，這也應該發生。這被稱為"本地回顯"。用戶端應實現訊息的"本地回顯"。用戶端可能會以不同的格式顯示訊息，以表明伺服器尚未處理該訊息。當伺服器回應時，應移除此格式。

用戶端需要能夠將它們正在發送的訊息與它們從事件流接收到的相同訊息匹配。從事件流接收到的相同訊息的回顯被稱為"遠程回顯"。兩種回顯都需要被識別為同一條訊息，以防止顯示重複的訊息。理想情況下，這種配對對用戶來說是透明的：UI 在從本地過渡到遠程時不會閃爍。通過用戶端使用它們用於發送特定事件的交易 ID，可以減少閃爍。當事件通過事件流到達時，使用的交易 ID 將包含在事件的 `unsigned` 數據中作為 `transaction_id`。

無法利用交易 ID 的用戶端在遠程回顯通過事件流到達*之前*發送訊息的請求完成時可能會遇到閃爍。在這種情況下，事件在用戶端獲得事件 ID 之前到達，使得無法將其識別為遠程回顯。這導致用戶端在一段時間內（取決於伺服器回應性）顯示訊息兩次，直到發送訊息的原始請求完成。一旦完成，用戶端可以通過查找重複的事件 ID 來採取補救措施以刪除重複的事件。

##### 計算用戶的顯示名稱

用戶端可能希望在成員列表中或當他們發送訊息時顯示房間成員的人類可讀顯示名稱。然而，不同的成員可能有衝突的顯示名稱。在向用戶顯示之前，必須消除顯示名稱的歧義，以防止冒充其他用戶。

為確保在用戶端之間一致地執行此操作，用戶端應使用以下算法來計算給定用戶的無歧義顯示名稱：

1.  檢查相關用戶 ID 的 `m.room.member` 狀態事件。
2.  如果 `m.room.member` 狀態事件沒有 `displayname` 字段，或者該字段的值為 `null`，則使用原始用戶 ID 作為顯示名稱。否則：
3.  如果 `m.room.member` 事件有一個在 `membership: join` 或 `membership: invite` 的房間成員中是唯一的 `displayname`，則使用給定的 `displayname` 作為用戶可見的顯示名稱。否則：
4.  `m.room.member` 事件有一個非唯一的 `displayname`。這應該使用用戶 ID 來消除歧義，例如"顯示名稱 (@id:homeserver.org)"。

開發人員在實現上述算法時應注意以下幾點：

-   一個成員的用戶可見顯示名稱可能會受到另一個成員狀態變化的影響。例如，如果 `@user1:matrix.org` 在房間中，`displayname: Alice`，然後當 `@user2:example.com` 加入房間時，也有 `displayname: Alice`，*兩個*用戶都必須給予消除歧義的顯示名稱。同樣，當其中一個用戶然後更改他們的顯示名稱時，不再有衝突，*兩個*用戶都可以給予他們選擇的顯示名稱。用戶端應該警惕這種可能性，並確保所有受影響的用戶都被正確重命名。
-   房間的顯示名稱也可能受到成員列表變化的影響。這是因為房間名稱有時基於用戶顯示名稱（參見[計算房間的顯示名稱](#計算房間的顯示名稱)）。
-   如果搜索整個成員列表以查找衝突的顯示名稱，這將導致構建房間成員列表的 O(N^2) 實現。對於具有大量成員的房間，這將非常低效。建議用戶端實現維護一個哈希表，將 `displayname` 映射到使用該名稱的房間成員列表。然後可以使用這樣的表格來高效計算是否需要消除歧義。

##### 顯示訊息的成員資訊

用戶端可能希望顯示發送訊息的房間成員的顯示名稱和頭像 URL。這可以通過檢查該用戶 ID 的 `m.room.member` 狀態事件來實現（參見[計算用戶的顯示名稱](#計算用戶的顯示名稱)）。

當用戶分頁瀏覽訊息歷史時，用戶端可能希望顯示房間成員的**歷史**顯示名稱和頭像 URL。這是可能的，因為在分頁時會返回舊的 `m.room.member` 事件。這可以通過保持兩組房間狀態：舊的和當前的，來有效實現。隨著新事件的到來和/或用戶向後分頁，這兩組狀態彼此偏離。新事件更新當前狀態，分頁事件更新舊狀態。當按順序處理分頁事件時，舊狀態代表*事件發送時*房間的狀態。然後可以用這個來設置歷史顯示名稱和頭像 URL。

##### 計算房間的顯示名稱

用戶端可能希望為房間顯示一個人類可讀的名稱。選擇有用名稱有多種可能性。為確保房間在用戶端之間一致命名，用戶端應使用以下算法選擇名稱：

1.  如果房間有一個 [m.room.name](#mroomname) 狀態事件，其 `name` 字段非空，則使用該字段給出的名稱。
2.  如果房間有一個 [m.room.canonical\_alias](#mroomcanonical_alias) 狀態事件，其 `alias` 字段有效，則使用該字段給出的別名作為名稱。注意，用戶端在計算房間名稱時應避免使用 `alt_aliases`。
3.  如果不滿足上述條件，應根據房間成員組成名稱。用戶端應考慮除登錄用戶之外的用戶的 [m.room.member](#mroommember) 事件，如下所定義。
    1.  如果房間的 `m.heroes` 數量大於或等於 `m.joined_member_count + m.invited_member_count - 1`，則使用英雄的成員事件來計算用戶的顯示名稱（如果需要[消除歧義](#計算用戶的顯示名稱)）並連接它們。例如，用戶端可能選擇顯示"Alice、Bob 和 Charlie (@charlie:example.org)"作為房間名稱。用戶端可以選擇限制用於生成房間名稱的用戶數量。
    2.  如果英雄數量少於 `m.joined_member_count + m.invited_member_count - 1`，並且 `m.joined_member_count + m.invited_member_count` 大於 1，用戶端應使用英雄來計算用戶的顯示名稱（如果需要[消除歧義](#計算用戶的顯示名稱)），並將它們與剩餘用戶的計數連接起來。例如，"Alice、Bob 和 1234 其他人"。
    3.  如果 `m.joined_member_count + m.invited_member_count` 小於或等於 1（表示成員是孤獨的），用戶端應使用上述規則來表明房間是空的。例如，"空房間（曾經是 Alice）"，"空房間（曾經是 Alice 和 1234 其他人）"，或者如果沒有英雄，就是"空房間"。

用戶端應該將房間名稱國際化為用戶的語言，當使用 `m.heroes` 計算名稱時。用戶端應該儘可能使用至少 5 個英雄來計算房間名稱，但可以使用更多或更少以更好地適應其用戶體驗。

##### 劇透訊息

{{% added-in v="1.1" %}}

訊息的部分可以通過使用劇透在視覺上對用戶隱藏。這不影響伺服器對事件內容的表示 - 它只是一個視覺提示，告訴用戶該訊息可能會揭示有關某事的重要資訊，從而破壞任何相關的驚喜。

要發送劇透，用戶端必須使用 `formatted_body` 和上面描述的 `org.matrix.custom.html` 格式。這使得劇透在任何可以適當支持此格式的 `msgtype` 上都有效。

劇透本身包含在 `span` 標籤中，原因（可選）在 `data-mx-spoiler` 屬性中。沒有原因的劇透至少必須指定屬性，儘管值可能為空/未定義。

劇透的一個例子是：

```json
{
  "msgtype": "m.text",
  "format": "org.matrix.custom.html",
  "body": "Alice [劇透](mxc://example.org/abc123) 在電影中。",
  "formatted_body": "Alice <span data-mx-spoiler>幸福地生活在一起</span> 在電影中。"
}
```

如果要提供原因，它會看起來像這樣：

```json
{
  "msgtype": "m.text",
  "format": "org.matrix.custom.html",
  "body": "Alice [Alice 健康狀況的劇透](mxc://example.org/abc123) 在電影中。",
  "formatted_body": "Alice <span data-mx-spoiler='alice 的健康狀況'>幸福地生活在一起</span> 在電影中。"
}
```

發送劇透時，用戶端應該如上所示在 `body` 中提供後備（包括原因）。後備不應包括包含劇透的文本，因為 `body` 可能會在純文本用戶端或通知中顯示。為防止劇透在這種情況下顯示，強烈鼓勵用戶端首先將包含劇透的文本上傳到媒體存儲庫，然後在 markdown 風格的鏈接中引用 `mxc://` URI，如上所示。

用戶端應該以某種披露的方式不同地渲染劇透。例如，用戶端可以模糊實際文本，並要求用戶點擊它以揭示。

##### 媒體標題

{{% added-in v="1.10" %}}

媒體訊息，包括 `m.image`、`m.file`、`m.audio` 和 `m.video`，可以包含標題以傳達有關媒體的額外資訊。

要發送標題，用戶端必須使用 `filename` 和 `body`，並可選地使用 `formatted_body` 和上面描述的 `org.matrix.custom.html` 格式。

如果存在 `filename`，且其值與 `body` 不同，則 `body` 被視為標題，否則 `body` 是文件名。`format` 和 `formatted_body` 僅用於標題。

> [!NOTE]
> 在規範的先前版本中，`body` 通常用於設置上傳文件的文件名，而 `filename` 只在 `m.file` 上出現，目的相同。

帶有標題的媒體訊息的示例是：

```json
{
    "msgtype": "m.image",
    "url": "mxc://example.org/abc123",
    "filename": "dog.jpg",
    "body": "這是一張~~貓~~圖片 :3",
    "format": "org.matrix.custom.html",
    "formatted_body": "這是一張<s>貓</s>圖片 :3",
    "info": {
        "w": 479,
        "h": 640,
        "mimetype": "image/jpeg",
        "size": 27253
    },
    "m.mentions": {}
}
```

用戶端必須在媒體旁邊渲染標題，並且應該優先使用其格式化表示。

##### 數學訊息

{{% added-in v="1.11" %}}

用戶可能希望在他們的訊息中發送數學符號。

要發送數學符號，用戶端必須使用 `formatted_body` 和上面描述的 `org.matrix.custom.html` 格式。這使得數學符號在任何可以適當支持此格式的 `msgtype` 上都有效。

數學符號本身使用 `span` 或 `div` 標籤，取決於符號應該內聯呈現還是不應該。數學符號使用 `data-mx-maths` 屬性以 [LaTeX](https://www.latex-project.org/) 格式編寫。

標籤的內容應該是無法渲染 LaTeX 格式的用戶端的後備表示。後備表示可以是，例如，一個圖像，或一個 HTML 近似，或原始 LaTeX 源代碼。當使用圖像作為後備時，發送用戶端應該意識到可能由於接收用戶端使用不同的背景顏色而產生的問題。`body` 應包括符號的文本表示。

數學符號的一個例子是：

```json
{
  "msgtype": "m.text",
  "format": "org.matrix.custom.html",
  "body": "這是一個方程：sin(x)=a/b。",
  "formatted_body": "這是一個方程：
      <span data-mx-maths=\"\\sin(x)=\\frac{a}{b}\">
        sin(<i>x</i>)=<sup><i>a</i></sup>/<sub><i>b</i></sub>
      </span>"
}
```

LaTeX 格式定義不明確，有幾個擴展，所以如果用戶端遇到它無法渲染的語法，它應該呈現後備表示。然而，用戶端應該至少支持基本的 [LaTeX2e](https://www.latex-project.org/) 數學命令和 [TeX](https://tug.org/) 數學命令，可能的例外是可能存在安全風險的命令。

> [!WARNING]
> 一般來說，確保 LaTeX 被安全處理，為用戶端的作者帶來了沉重的負擔。某些命令，例如[那些可以創建巨集的命令](https://katex.org/docs/supported#macros)具有潛在的危險。用戶端應該要麼拒絕處理這些命令，要麼應該注意確保它們以安全的方式處理（例如，通過限制遞歸）。一般來說，LaTeX 命令應該通過允許已知好的命令而不是禁止已知壞的命令來過濾。
> 
> 因此，用戶端不應該通過調用 LaTeX 編譯器來渲染數學，除非有適當的沙盒，因為這些可執行文件並不是為處理不可信輸入而編寫的。一些 LaTeX 渲染庫更適合這種情況，因為它們只允許 LaTeX 的子集並強制執行遞歸限制。

#### 伺服器行為

家伺服器應該拒絕沒有 `msgtype` 鍵或沒有文本 `body` 鍵的 `m.room.message` 事件，並回傳 HTTP 狀態碼 400。

#### 安全考慮

使用此模組發送的訊息未加密，儘管端到端加密正在開發中（見 [E2E 模組](#end-to-end-encryption)）。

用戶端應該為不安全的 HTML 清理**所有顯示的鍵**，以防止跨站腳本（XSS）攻擊。這包括房間名稱和主題。

### 內容存儲庫

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/content_repo.md)

內容存儲庫（或稱"媒體存儲庫"）允許用戶將文件上傳到其主伺服器以供日後使用。例如，用戶想要發送到房間的文件會上傳到這裡，用戶想要使用的頭像也是如此。

上傳通過 POST 請求發送到用戶本地主伺服器上的資源，該資源返回一個 `mxc://` URI，之後可用於 GET 下載。內容從接收者的本地主伺服器下載，除非源和目標主伺服器相同，否則必須先使用相同的 API 從源主伺服器傳輸內容。

在提供內容時，伺服器應該提供一個 `Content-Security-Policy` 標頭。推薦的策略是 `sandbox; default-src 'none'; script-src 'none'; plugin-types application/pdf; style-src 'unsafe-inline'; object-src 'self';`。

{{% boxes/added-in-paragraph %}}
{{< added-in v="1.4" >}} 在提供內容時，伺服器還應該額外提供 `Cross-Origin-Resource-Policy: cross-origin`，以允許（網頁）用戶端在與媒體存儲庫交互時訪問受限制的 API，如 `SharedArrayBuffer`。
{{% /boxes/added-in-paragraph %}}

{{% boxes/added-in-paragraph %}}
{{< changed-in v="1.11" >}} 未經身份驗證的下載端點已被棄用，取而代之的是更新的、需要身份驗證的端點。這個變更包括將所有媒體端點的路徑從 `/_matrix/media/*` 更新為 `/_matrix/client/{version}/media/*`，但 `/upload` 和 `/create` 端點除外。上傳/創建端點預計將在規範的後續版本中進行類似的轉變。
{{% /boxes/added-in-paragraph %}}

#### Matrix 內容（`mxc://`）URI

內容位置以 Matrix 內容（`mxc://`）URI 表示。它們看起來像這樣：

```
mxc://<server-name>/<media-id>

<server-name> : 此內容源自的主伺服器名稱，例如 matrix.org
<media-id> : 標識內容的不透明 ID。
```

#### 用戶端行為 {id="content-repo-client-behaviour"}

用戶端可以使用以下端點訪問內容存儲庫。

{{% boxes/added-in-paragraph %}}
{{< changed-in v="1.11" >}} 用戶端不應使用下面描述的已棄用媒體端點。相反，它們應該使用需要身份驗證的新端點。
{{% /boxes/added-in-paragraph %}}

{{% boxes/warning %}}
到 Matrix 1.12，伺服器應該"凍結"已棄用的、不需要身份驗證的端點，以防止新上傳的媒體被下載。這應該意味著在凍結之前上傳的任何媒體仍然可以通過已棄用的端點訪問，而在凍結之後（或期間）上傳的任何媒體應該只能通過新的、需要身份驗證的端點訪問。對於遠程媒體，"新上傳"由緩存填充日期決定。這可能意味著媒體比凍結更早，但因為伺服器必須重新下載它，所以現在被視為"新"。

用戶端應該在伺服器凍結未經身份驗證的訪問之前更新以支持經過身份驗證的端點。

在實施凍結之前，伺服器應該考慮其本地生態系統的影響。這可能意味著確保其用戶的典型用戶端在可用時支持新端點，或更新橋接器以開始使用媒體代理。

除上述內容外，伺服器應該將 [`m.login.sso` 流程中使用的 IdP 圖標](/client-server-api/#definition-mloginsso-flow-schema)排除在凍結之外。有關詳細信息，請參閱 `m.login.sso` 流程架構。

伺服器的*示例*時間表可能是：

* Matrix 1.11 發布：用戶端開始支持經過身份驗證的媒體。
* Matrix 1.12 發布：伺服器凍結未經身份驗證的媒體訪問。
  * 在此之前上傳的媒體仍然可以使用已棄用的端點。
  * 新上傳（或緩存）的媒體*只*在經過身份驗證的端點上工作。

預計 Matrix 1.12 將在 2024 年 7 月至 9 月的日曆季度發布。
{{% /boxes/warning %}}

```
{{% http-api spec="client-server" api="authed-content-repo" %}}

{{% http-api spec="client-server" api="content-repo" %}}
```

##### 縮略圖

主伺服器應該能夠為上傳的圖像和視頻提供縮略圖。目前尚未指定可以生成縮略圖的確切文件類型 - 詳見 [Issue \#1938](https://github.com/matrix-org/matrix-doc/issues/1938) 以獲取更多信息。

縮略圖方法有"crop"和"scale"。"scale"嘗試返回一個寬度或高度小於請求大小的圖像。如果用戶端需要適應給定的矩形，則應該縮放並加上黑邊。"crop"嘗試返回一個寬度和高度接近請求大小且長寬比匹配請求大小的圖像。如果用戶端需要適應給定的矩形，則應該縮放圖像。

給予縮略圖 API 的尺寸是用戶端偏好的最小尺寸。伺服器絕不能返回小於用戶端請求尺寸的縮略圖，除非被縮略的內容本身小於請求的尺寸。當內容小於請求的尺寸時，伺服器應該返回原始內容而不是縮略圖。

伺服器應該生成具有以下尺寸和方法的縮略圖：

- 32x32，crop
- 96x96，crop
- 320x240，scale
- 640x480，scale
- 800x600，scale

總結：
- "scale"保持圖像的原始長寬比
- "crop"提供與請求中給定尺寸長寬比相同的圖像
- 在可能的情況下，伺服器將返回大於或等於請求尺寸的圖像。

伺服器在任何情況下都不得放大縮略圖。除非原始內容使其不可能，否則伺服器不得返回比請求更小的縮略圖。

#### 安全考慮

HTTP GET 端點不需要任何身份驗證。知道內容的 URL 就足以檢索內容，即使實體不在房間中。

`mxc://` URI 容易受到目錄遍歷攻擊，如 `mxc://127.0.0.1/../../../some_service/etc/passwd`。這會導致目標主伺服器嘗試訪問並返回此文件。因此，主伺服器必須通過只允許 `server-name` 和 `media-id` 值中使用字母數字（`A-Za-z0-9`）、`_` 和 `-` 字符來清理 `mxc://` URI。這組白名單字符允許 RFC 4648 中指定的 URL 安全的 base64 編碼。應用此字符白名單比黑名單 `.` 和 `/` 更好，因為有一些技術可以繞過黑名單字符（百分比編碼字符、UTF-8 編碼遍歷等）。

主伺服器還有其他特定於內容的考慮：

- 用戶端可能嘗試上傳非常大的文件。主伺服器不應存儲過大的文件，也不應將它們提供給用戶端，而應返回帶有 `M_TOO_LARGE` 代碼的 HTTP 413 錯誤。
- 用戶端可能嘗試上傳非常大的圖像。主伺服器不應嘗試為過大的圖像生成縮略圖，而應返回帶有 `M_TOO_LARGE` 代碼的 HTTP 413 錯誤。
- 遠程主伺服器可能託管非常大的文件或圖像。主伺服器不應代理或為來自遠程主伺服器的大文件或圖像生成縮略圖，而應返回帶有 `M_TOO_LARGE` 代碼的 HTTP 502 錯誤。
- 用戶端可能嘗試上傳大量文件。主伺服器應限制用戶端可以上傳的媒體數量和總大小，返回帶有 `M_FORBIDDEN` 代碼的 HTTP 403 錯誤。
- 用戶端可能嘗試通過主伺服器訪問大量遠程文件。主伺服器應限制其緩存的遠程文件的數量和大小。
- 用戶端或遠程主伺服器可能嘗試上傳惡意文件，針對主伺服器縮略圖生成或用戶端解碼器中的漏洞。

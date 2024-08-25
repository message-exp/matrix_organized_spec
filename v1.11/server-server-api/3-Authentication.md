# 3. Authentication

<!-- markdownlint-disable -->
- [3. Authentication](#3-authentication)
  - [3.1 Request Authentication](#31-request-authentication)
  - [3.2 Response Authentication](#32-response-authentication)
  - [3.3 Client TLS Certificates](#33-client-tls-certificates)
<!-- markdownlint-enable -->

---

- 主要是說明如何透過金鑰來簽名每個資訊
- 後面的部分主要是說如何兼容舊版本
- 確認伺服器身份前不發送請求
- 因為伺服器會需要檢查TLS證書，所以通常是在HTTP層進行身份驗證

## 3.1 Request Authentication

每個由主伺服器發出的 HTTP 請求都使用公鑰數字簽名進行身份驗證。
請求方法、目標和主體會被包裹在一個 JSON 對象中，
並使用 JSON 簽名算法進行簽名。
結果簽名會作為一個 Authorization 標頭添加，
並使用 `X-Matrix` 認證方案。
請注意，目標字段應包括從 `/_matrix/...` 開始的完整路徑，
包括 `?` 和任何查詢參數（如果有），
但不應包括前導的 `https:`，也不包括目標伺服器的主機名。

步驟 1 簽署 JSON：

```json
{
    "method": "POST",
    "uri": "/target",
    "origin": "origin.hs.example.com",
    "destination": "destination.hs.example.com",
    "content": <JSON-parsed request body>,
    "signatures": {
        "origin.hs.example.com": {
            "ed25519:key1": "ABCDEF..."
        }
    }
}
```

JSON 中的伺服器名稱是每個參與主伺服器的名稱。
來自[伺服器名稱解析部分](/v1.11/server-server-api/2-Server-discovery.md#21-resolving-server-names)的委派不影響這些伺服器名稱——使用委派之前的伺服器名稱。
在請求簽名過程中，這一條件始終適用。

步驟 2 添加 Authorization 標頭：

```plaintext
POST /target HTTP/1.1
Authorization: X-Matrix origin="origin.hs.example.com",destination="destination.hs.example.com",key="ed25519:key1",sig="ABCDEF..."
Content-Type: application/json

<JSON-encoded request body>
```

示例 Python 程式碼：

```python
def authorization_headers(
    origin_name, 
    origin_signing_key, 
    destination_name, 
    request_method, 
    request_target, 
    content=None
):
    request_json = {
         "method": request_method,
         "uri": request_target,
         "origin": origin_name,
         "destination": destination_name,
    }

    if content is not None:
        # 假設 content 已經解析為 JSON
        request_json["content"] = content

    signed_json = sign_json(request_json, origin_name, origin_signing_key)

    authorization_headers = []

    for key, sig in signed_json["signatures"][origin_name].items():
        authorization_headers.append(bytes(
            "X-Matrix origin=\"%s\",destination=\"%s\",key=\"%s\",sig=\"%s\"" % (
                origin_name, destination_name, key, sig,
            )
        ))

    return ("Authorization", authorization_headers[0])
```

<!-- markdownlint-disable -->
Authorization 標頭的格式如 [RFC 9110 第 11.4 節](https://datatracker.ietf.org/doc/html/rfc9110#section-11.4) 所述。
<!-- markdownlint-enable -->
簡而言之，標頭以認證方案 `X-Matrix` 開頭，
後面跟著一個或多個空格，
然後是逗號分隔的參數列表，
參數以 `name=value` 的形式表示。
每個逗號周圍允許有零個或多個空格和制表符。
名稱不區分大小寫，順序無關緊要。
如果值包含不允許在 `token` 中的字符，
則必須用引號括起來，
<!-- markdownlint-disable -->
如 [RFC 9110 第 5.6.2 節](https://datatracker.ietf.org/doc/html/rfc9110#section-5.6.2) 所定義的；
<!-- markdownlint-enable -->
如果值是一個有效的 `token`，
則可以選擇是否用引號括起來。
引用的值可以包括反斜杠轉義字符。
解析標頭時，接收者必須反轉義這些字符，
即反斜杠字符對被替換為反斜杠後的字符。

為了與舊伺服器兼容，發送者應：

- 在 `X-Matrix` 後只包含一個空格，
- 只使用小寫名稱，
- 避免在參數值中使用反斜杠，
- 避免在 name=value 對之間的逗號周圍包含空白。

為了與舊伺服器兼容，接收者應允許在值中包含冒號而不要求將值用引號括起來。

要包含的認證參數有：

- `origin`：發送伺服器的伺服器名稱。這與步驟 1 中 JSON 的 `origin` 字段相同。
- `destination`：**[在 `v1.3` 中添加]** 接收伺服器的伺服器名稱。
  - 與步驟 1 中 JSON 的 `destination` 字段相同。為了與舊伺服器兼容，接收者應接受不帶此參數的請求，但必須始終發送該參數。
  - 如果包含此屬性，但值與接收伺服器的名稱不匹配，接收伺服器必須以 HTTP 狀態碼 401 Unauthorized 拒絕該請求。
- `key`：發送伺服器用來簽署請求的密鑰 ID，包括算法名稱。
- `signature`：步驟 1 中計算的 JSON 簽名。

未知的參數將被忽略。

<!-- markdownlint-disable -->
**[在 `v1.11` 中更改]** 本節曾引用 [RFC 7235](https://datatracker.ietf.org/doc/html/rfc7235#section-2.1) 
和 [RFC 7230](https://datatracker.ietf.org/doc/html/rfc9110#section-5.6.2)，
這些已被 RFC 9110 取代，相關部分沒有變更。
<!-- markdownlint-enable -->

## 3.2 Response Authentication

回應是由 TLS 伺服器證書進行認證的。主伺服器在確認連接伺服器身份之前，不應發送請求，以避免訊息洩漏給竊聽者。

## 3.3 Client TLS Certificates

請求是在 HTTP 層進行認證，
而不是在 TLS 層，因為像 Matrix 這樣的 HTTP 服務通常部署在負載均衡器後面，
這些負載均衡器處理 TLS 並使得檢查 TLS 客戶端證書變得困難。

主伺服器可以提供 TLS 客戶端證書，
接收主伺服器可以檢查該客戶端證書是否與原始主伺服器的證書匹配。

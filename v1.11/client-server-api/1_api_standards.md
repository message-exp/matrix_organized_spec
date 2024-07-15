## API Standard

- HTTP APIs
- JSON
- UTF-8
- 使用不公開的 `access_token` 進行驗證
- 所有 POST 及 PUT 的 endpoint，客戶端都必須提供包含（可能為空）JSON 的請求（request），且標頭（header）應註明 `Content-Type: application/json`（非必須），但以下 endpoint 除外：
  - [`POST /_matrix/media/v3/upload`](https://spec.matrix.org/v1.11/client-server-api/#post_matrixmediav3upload)  
    [`PUT /_matrix/media/v3/upload/{serverName}/{mediaId}`](https://spec.matrix.org/v1.11/client-server-api/#put_matrixmediav3uploadservernamemediaid)  
    以上傳的媒體作為 request body
  - [`POST /_matrix/client/v3/logout`](https://spec.matrix.org/v1.11/client-server-api/#post_matrixclientv3logout)  
    [`POST /_matrix/client/v3/logout/all`](https://spec.matrix.org/v1.11/client-server-api/#post_matrixclientv3logoutall)  
    採用空 request body
- [Conventions for Matrix APIs](https://spec.matrix.org/v1.11/appendices#conventions-for-matrix-apis)
- [Web Browser Clients](https://spec.matrix.org/v1.11/client-server-api/#web-browser-clients)

### 標準錯誤回應

#### 格式

```json
{
  "errcode": "<error code>",
  "error": "<error message>"
}
```

**error**: 人類可讀的訊息，通常是解釋出錯原因的句子

**errcode**: 
- 唯一字串（unique string）
- 大寫 namespace 加底線 `_`  
  namespace 可自訂  
  Matrix 規範的 namespace 以 `M_` 開頭  
  _例：`COM.MYDOMAIN.HERE_FORBIDDEN`_
  
其他 additional key: 視 `errcode` 規範而定

#### 使用

- 有 error code -> 看 error code
- `M_UNKNOWN` -> 看 HTTP 狀態碼

#### 常見錯誤代碼

`M_FORBIDDEN` 禁止存取

`M_UNKNOWN_TOKEN` 無法辨識指定的 存取或刷新令牌  
401 HTTP 狀態碼（Unauthorized）：可能有附加回應參數（additional response parameter）`soft_logout`，見 [soft logout](https://spec.matrix.org/v1.11/client-server-api/#soft-logout)

`M_MISSING_TOKEN` 沒給 access token

`M_BAD_JSON` 格式錯誤

`M_NOT_JSON` 沒給有效的 JSON

`M_NOT_FOUND` 找不到

`M_LIMIT_EXCEEDED` 傳太快了，慢一點

`M_UNRECOGNIZED` 伺服器無法理解該請求  
endpoint 沒被 implement: 傳回 404 (HTTP 狀態碼)  
endpoint 有 implement，但用了不正確的 HTTP method: 傳回 405（Method Not Allowed）

`M_UNKNOWN` 發生未知錯誤

#### 其他錯誤代碼

`M_UNAUTHORIZED` 請求未正確授權，通常是登入失敗

`M_USER_DEACTIVATED` User ID 已停用。通常用於 prove authentication 的端點，例如 `/login`

`M_USER_IN_USE` 欲註冊的 User ID 已經被使用

`M_INVALID_USERNAME` 嘗試註冊無效的 User ID

`M_ROOM_IN_USE` 提供給 `createRoom` API 的房間別名已被使用

`M_INVALID_ROOM_STATE` 提供給 `createRoom` API 的初始狀態無效

`M_THREEPID_IN_USE` 給予 API 的第三方 pid 無法使用，因為相同的第三方 pid 已在使用中

`M_THREEPID_NOT_FOUND` 由於找不到與第三方 pid 相符的記錄而無法使用給予 API 的第三方 pid 

`M_THREEPID_AUTH_FAILED` 無法對第三方識別碼（identifier）行身份驗證

`M_THREEPID_DENIED` 伺服器不允許此第三方識別碼。這可能發生在伺服器僅允許來自特定網域的電子郵件地址等情況

`M_SERVER_NOT_TRUSTED`
用戶端的請求使用了此伺服器不信任的第三方伺服器，例如不信任的 identity 伺服器

`M_UNSUPPORTED_ROOM_VERSION` 用戶端請求建立 room 時使用了伺服器不支援的 room 版本

`M_INCOMPATIBLE_ROOM_VERSION` 用戶端嘗試加入伺服器不支援版本的 room。請檢查錯誤回應的 `room_version` 屬性以了解 room 的版本

`M_BAD_STATE`
無法執行要求的狀態更改，例如嘗試取消禁止未被禁止的用戶

`M_GUEST_ACCESS_FORBIDDEN` room 或資源不允許訪客訪問

`M_CAPTCHA_NEEDED` 需要 Captcha 以完成請求

`M_CAPTCHA_INVALID` 提供的 Captcha 與預期不符

`M_MISSING_PARAM` 請求中缺少必需的參數

`M_INVALID_PARAM` 特定參數的值 錯誤。例如，伺服器預期為整數但收到字串

`M_TOO_LARGE` 請求或實體太大

`M_EXCLUSIVE` 請求的資源被應用服務（application service）保留，或者請求的應用服務尚未創建該資源

`M_RESOURCE_LIMIT_EXCEEDED` 由於主伺服器達到了對其施加的資源限制，無法完成請求。例如，如果主伺服器位於共享託管環境中，則可能會在使用過多記憶體或磁碟空間時達到資源限制。  
錯誤必須具有 `admin_contact` 欄位，以便接收錯誤的用戶能夠進行聯繫。  
此錯誤通常出現在嘗試修改狀態的路由（route）（例如：發送訊息、帳戶資料等），而不是僅讀取狀態的路由（例如：`/sync`，取得帳戶資料等）

`M_CANNOT_LEAVE_SERVER_NOTICE_ROOM` 用戶無法拒絕加入伺服器通知 room （server notices room）的邀請。見 [伺服器通知](#server-notices)

#### Rate limiting 速率限制

- 主伺服器**應該**實作速率限制機制以降低過載的風險
- 超過速率限制錯誤訊息：  
  ```json
  {
    "errcode": "M_LIMIT_EXCEEDED",
    "error": "string",
    "retry_after_ms": integer (optional, deprecated)
  }
  ```
- 主伺服器**應該**於 429 狀態碼的任何回應中包含 `Retry-After` 標頭
- _`retry_after_ms` 已棄用（v1.10）_

### Transaction identifiers 交易識別碼

- client-server API 通常使用 `HTTP PUT` 提交 附帶交易識別碼（由客戶端生成） 的請求
- 目的：讓主伺服器區分 新請求/重傳請求 （就這樣，沒了）
- 範圍（scope）：單一裝置及單一 HTTP endpoint（即同一裝置對不同 endpoint 使用相同的交易識別碼，會被當作是不同的請求；登出前與重新登入後的請求也不同。見 [access tokens 與裝置間的關係](https://spec.matrix.org/v1.11/client-server-api/#relationship-between-access-tokens-and-devices)）
- 用戶端：請求完成後，下個請求的 `{txnId}` 值應該更改（未規範具體方式，建議使用單調遞增的整數）
- 伺服器：如果交易 ID 與先前的請求相同、HTTP 請求的路徑相同  
  →重傳：主伺服器應傳回與原始請求相同的 HTTP 回應代碼和內容
- 某些 API 端點可能允許或要求使用不含交易識別碼 的 POST 請求。如果這是可選的（optional），則強烈建議使用 PUT 請求

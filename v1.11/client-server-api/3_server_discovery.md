## 伺服器探索

- 用戶端應該利用自動探索機制，使用使用者的 Matrix ID 決定伺服器的 URL
- 自動探索僅用於登入時
- 本節術語：
  - `PROMPT`
  - `IGNORE` 停止目前的自動探索機制。若無更多自動探索機制可用，用戶端可使用其他方式來決定所需參數
  - `FAIL_PROMPT` 通知使用者由於參數無效/空資料及 `PROMPT`，自動探索失敗
  - `FAIL_ERROR` 通知使用者自動探索未傳回任何可用的 URL。   
    不要繼續目前的登入流程。此時已經取得了有效資料，但是還沒有伺服器可以為用戶端提供服務。不應嘗試進一步猜測，使用者應決定下一步該做什麼。

### Well-known URI

> [!NOTE]
> 依規範中的 CORS 章節，hosting `.well-known` 的伺服器**應該**提供 CORS 標頭

`.well-known` 方法使用預先定下的位置來指定參數值，流程如下：
1. 透過在第一個冒號處拆分 Matrix ID，從使用者的 Matrix ID 中提取[伺服器名稱（server name）](https://spec.matrix.org/v1.11/appendices/#server-name)
2. 依照[語法](https://spec.matrix.org/v1.11/appendices/#server-name)從伺服器名稱中提取主機名稱（host name）
3. 向 `https://hostname/.well-known/matrix/client` 發出 GET 請求
   1. 404 => `IGNORE`
   2. 不是 200 或回應 body 為空 => `FAIL_PROMPT`
   3. 將回應 body 解析成 JSON 物件
      1. 無法解析內容 => `FAIL_PROMPT`
   4. 從 `m.homeserver` 屬性中提取 `base_url`。此值將用作主伺服器的基本 URL
      1. 未提供此值 => `FAIL_PROMPT`
   5. 驗證主伺服器基本 URL
      1. 將其解析為 URL  
         不是 URL => `FAIL_ERROR`
      2. 用戶端應該在接受之前透過連接到 [`/_matrix/client/versions`](https://spec.matrix.org/v1.11/client-server-api/#get_matrixclientversions) endpoint 來驗證 URL 是否指向有效的主伺服器，確定它不會傳回錯誤，並解析和驗證資料是否符合預期的回應格式  
         驗證中的任何步驟失敗 => `FAIL_ERROR`  
         透過對配置錯誤的簡單檢查來進行驗證，以確保探索到的地址指向有效的主伺服器
      4. `base_url` 可能以 `/` 結尾
   6. 如果存在 `m.identity_server` 屬性，請擷取 `base_url` 值以用作身分識別伺服器的基本 URL。此 URL 的驗證與上述步驟相同，但使用 `/_matrix/identity/v2` 作為要連線的 endpoint  
      `m.identity_server` 屬性存在，但沒有 `base_url` 值 => `FAIL_PROMPT`

[GET `/.well-known/matrix/client`](https://spec.matrix.org/v1.11/client-server-api/#getwell-knownmatrixclient)

[GET `/_matrix/client/versions`](https://spec.matrix.org/v1.11/client-server-api/#get_matrixclientversions)

[GET `/.well-known/matrix/support`](https://spec.matrix.org/v1.11/client-server-api/#getwell-knownmatrixsupport)

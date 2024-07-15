## 用戶端驗證

大多數 API endpoint 要求使用者透過以 access token 的形式提供先前獲得的憑證來識別自己的身分

access token 通常是透過登入或註冊過程獲得的。access token 可能會過期；可以使用 refresh token 產生新的 access token

> [!NOTE]
> 本規範不強制要求 access token 採用特定格式。用戶端應將其視為不透明的位元組序列。伺服器可以自由選擇合適的格式。伺服器實現者可能會想研究 [macaroons](http://research.google.com/pubs/pub41892.html)

### 使用 access token

access token 可以使用身分驗證承載方案 透過請求標頭提供：`Authorization: Bearer TheTokenHere`

_`access_token=TheTokenHere` 方式已棄用，但主伺服器一樣要支援_

需要憑證但漏給（missing） => 401 `M_MISSING_TOKEN`  
需要憑證但憑證已失效 => 401 `M_UNKNOWN_TOKEN`

`M_UNKNOWN_TOKEN` 可能代表：
1. access token 從未有效
2. access token 已被登出（註銷）
3. access token 已被軟登出
4. access token 需要 refresh

用戶端收到 `M_UNKNOWN_TOKEN` 時，應該
- 若有 refresh token 則嘗試更新 token
- 若軟登出設定為 `true`，它可以重新登入該用戶，且保留任何用戶端的持續資訊
- 否則，認定該用戶已登出

### access token 與裝置間的關係

- 用戶端裝置與 access token 及 refresh token 密切相關
- Matrix 伺服器應紀錄每個 access token 與 refresh token 屬於哪個裝置，以正確處理請求
- 預設情況下，登入和註冊會自動生成新的 `device_id`，用戶端也可以自由生成新 `device_id`
- 用戶端應在請求 body 中傳遞 `devcice_id`
- 如果用戶端設定 `device_id` ，伺服器將使先前指派給該裝置的任何 access token 和 refresh token 失效

### 更新 access token

- access token 會在一段時間後過期，任何使用過期 access token 的 HTTP 呼叫都會傳回 `M_UNKNOWN_TOKEN`，最好加個 `soft_logout: true`  
  用戶端收到此錯誤，應嘗試呼叫 [`/refresh`](https://spec.matrix.org/v1.11/client-server-api/#post_matrixclientv3refresh) 更新 token 
- token 未過期也隨時可以更新
- 更新後應使用新 token（即使是重試之前失敗的請求）
- refresh token 更新後，舊的 refresh token 會失效，access token 需要被更新時就應該使用新的 refresh token
- 若 token 更新失敗，  
  錯誤回應包含 `soft_logout: true` => 將其視為軟登出並嘗試重新登入以獲取新的 token  
  錯誤回應不包含 `soft_logout: true` => 視為登出
- 不支援 refresh token 的用戶端的處理由主伺服器決定  
  用戶端透過在 `/login` 和 `/register` endpoint 的請求 body 中加入 `refresh_token: true` 屬性來表示對 refresh token 的支援

### 軟登出（soft logout）

......

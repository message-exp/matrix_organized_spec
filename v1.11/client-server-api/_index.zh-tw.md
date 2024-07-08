# Client-Server API

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

## 標準錯誤回應

### 格式

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

### 使用

- 有 error code -> 看 error code
- `M_UNKNOWN` -> 看 HTTP 狀態碼

### 常見錯誤代碼

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

### 其他錯誤代碼

`M_UNAUTHORIZED` 請求未正確授權，通常是登入失敗

`M_USER_DEACTIVATED` User ID 已停用。通常用於 prove authentication 的端點，例如 `/login`

`M_USER_IN_USE` 欲註冊的 User ID 已經被使用

`M_INVALID_USERNAME` 嘗試註冊無效的 User ID

`M_ROOM_IN_USE` 提供給 `createRoom` API 的房間別名已被使用

`M_INVALID_ROOM_STATE` 提供給 `createRoom` API 的初始狀態無效

`M_THREEPID_IN_USE` 給予 API 的第三方 pid 無法使用，因為相同的第三方 pid 已在使用中

`M_THREEPID_NOT_FOUND` 由於找不到與第三方 pid 相符的記錄而無法使用給予 API 的第三方 pid 

`M_THREEPID_AUTH_FAILED` 無法對第三方 identifier 進行身份驗證

`M_THREEPID_DENIED` 伺服器不允許此第三方 identifier。這可能發生在伺服器僅允許來自特定網域的電子郵件地址等情況

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

### 速率限制

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

### 交易標識符

用戶端-伺服器 API 通常使用 `HTTP PUT` 提交請求，並在 HTTP 路徑中使用用戶端生成的交易標識符。

交易 ID 的目的是讓主伺服器能夠區分新請求和先前請求的重傳，以使請求具備冪等性。

交易 ID 應**僅**用於此目的。

請求完成後，用戶端應更改下一個請求的 `{txnId}` 值。如何實現這一點由實現細節決定。建議用戶端使用版本 4 的 UUID 或當前時間戳和單調遞增整數的組合。

如果交易 ID 與先前請求相同，並且 HTTP 請求的路徑也相同，主伺服器應識別該請求為重傳。

如果識別到重傳，主伺服器應返回與原始請求相同的 HTTP 回應碼和內容。例如，`PUT /_matrix/client/v3/rooms/{roomId}/send/{eventType}/{txnId}` 將返回 `200 OK`，並在回應體中返回原始請求的 `event_id`。

交易 ID 的範圍僅限於單個 [設備](../index.html#devices) 和單個 HTTP 端點。換句話說：單個設備可以使用相同的交易 ID 發送請求到 [`PUT /_matrix/client/v3/rooms/{roomId}/send/{eventType}/{txnId}`](#put_matrixclientv3roomsroomidsendeventtypetxnid) 和 [`PUT /_matrix/client/v3/sendToDevice/{eventType}/{txnId}`](#put_matrixclientv3sendtodeviceeventtypetxnid)，這兩個請求會被認為是不同的，因為這兩個端點被視為獨立端點。同樣，如果用戶端在兩次使用相同交易 ID 的請求之間登出並重新登錄，這兩個請求是不同的，因為登錄和登出的操作創建了一個新設備（除非在 [`POST /_matrix/client/v3/login`](#post_matrixclientv3login) 中傳遞了現有的 `device_id`）。另一方面，如果用戶端在 [刷新](#refreshing-access-tokens) 訪問令牌後重新使用相同端點的交易 ID，則將其視為重複請求並被忽略。另見 [訪問令牌和設備之間的關係](#relationship-between-access-tokens-and-devices)。

一些 API 端點可能允許或要求使用沒有交易 ID 的 `POST` 請求。在這是可選的情況下，強烈建議使用 `PUT` 請求。

> [!NOTE]
> RATIONALE: 在 `v1.7` 之前，交易 ID 的範圍是“用戶端會話”而不是設備。

## 網頁瀏覽器用戶端

在現實中，可以預期一些用戶端將被編寫為在網頁瀏覽器或類似環境中運行。在這些情況下，主伺服器應回應預檢請求，並在所有請求中提供跨來源資源共享（CORS）標頭。

伺服器必須預期用戶端將使用 `OPTIONS` 請求接近它們，允許用戶端探索 CORS 標頭。本規範中的所有端點都支持 `OPTIONS` 方法，然而當使用 `OPTIONS` 請求接近時，伺服器不得執行為端點定義的任何邏輯。

當用戶端使用請求接近伺服器時，伺服器應回應該路由的 CORS 標頭。推薦伺服器在所有請求中返回的 CORS 標頭為：

    Access-Control-Allow-Origin: *
    Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
    Access-Control-Allow-Headers: X-Requested-With, Content-Type, Authorization

## 伺服器探索

為了允許用戶在不明確指定主伺服器的 URL 或其他參數的情況下連接到 Matrix 伺服器，用戶端應使用自動探索機制根據用戶的 Matrix ID 確定伺服器的 URL。自動探索應僅在登錄時進行。

在本節中，以下術語具有特定含義：

`PROMPT`
以符合現有用戶端用戶體驗的方式從用戶那裡檢索特定資訊，如果用戶端傾向於這樣做。如果在此時無法提供良好的用戶體驗，可以發生失敗。

`IGNORE`
停止當前的自動探索機制。如果沒有更多的自動探索機制可用，那麼用戶端可以使用其他方法來確定所需的參數，例如提示用戶或使用預設值。

`FAIL_PROMPT`
通知用戶自動探索由於無效/空數據而失敗，並 `PROMPT` 該參數。

`FAIL_ERROR`
通知用戶自動探索沒有返回任何可用的 URL。不要繼續當前的登錄過程。此時，已獲得有效數據，但沒有伺服器可為用戶端提供服務。不應進一步猜測，用戶應該做出下一步的慎重決定。

### Well-known URI

> [!NOTE]
> INFO: 根據本規範中的 [CORS](#web-browser-clients) 部分，託管 `.well-known` JSON 文件的伺服器應提供 CORS 標頭。

`.well-known` 方法使用位於預定位置的 JSON 文件來指定參數值。此方法的流程如下：

1. 從用戶的 Matrix ID 中提取 [伺服器名稱](/appendices/#server-name)，方法是按第一個冒號拆分 Matrix ID。
2. 根據 [語法](/appendices/#server-name) 從伺服器名稱中提取主機名。
3. 發出 GET 請求到 `https://hostname/.well-known/matrix/client`。
    1. 如果返回的狀態碼是 404，則 `IGNORE`。
    2. 如果返回的狀態碼不是 200，或者回應主體為空，則 `FAIL_PROMPT`。
    3. 將回應主體解析為 JSON 對象
        1. 如果無法解析內容，則 `FAIL_PROMPT`。
    4. 從 `m.homeserver` 屬性中提取 `base_url` 值。此值將用作主伺服器的基礎 URL。
        1. 如果未提供此值，則 `FAIL_PROMPT`。
    5. 驗證主伺服器基礎 URL：
        1. 將其解析為 URL。如果它不是 URL，則 `FAIL_ERROR`。
        2. 用戶端應通過連接到 [`/_matrix/client/versions`](/client-server-api/#get_matrixclientversions) 端點驗證該 URL 指向有效的主伺服器，確保它不返回錯誤，並解析和驗證數據是否符合預期的回應格式。如果驗證中的任何步驟失敗，則 `FAIL_ERROR`。驗證僅作為對配置錯誤的簡單檢查，以確保發現的地址指向有效的主伺服器。
        3. 需要注意的是，`base_url` 值可能包含結尾的 `/`。消費者應準備好處理這兩種情況。
    6. 如果存在 `m.identity_server` 屬性，則提取 `base_url` 值用作身份伺服器的基礎 URL。對此 URL 的驗證與上述步驟相同，但使用 `/_matrix/identity/v2` 作為連接端點。如果存在 `m.identity_server` 屬性，但沒有 `base_url` 值，則 `FAIL_PROMPT`。

{{% http-api spec="client-server" api="wellknown" %}}

{{% http-api spec="client-server" api="versions" %}}

{{% http-api spec="client-server" api="support" %}}

## 用戶端身份驗證

大多數 API 端點要求用戶通過提供先前獲得的憑據（形式為訪問令牌）來識別自己。訪問令牌通常通過 [登錄](#login) 或 [註冊](#account-registration-and-management) 過程獲得。訪問令牌可能會過期；可以使用刷新令牌生成新的訪問令牌。

> [!NOTE]
> INFO: 本規範不強制要求訪問令牌的特定格式。用戶端應將其視為不透明的字節序列。伺服器可以自由選擇合適的格式。伺服器實現者可能會研究 [macaroons](http://research.google.com/pubs/pub41892.html)。

### 使用訪問令牌

訪問令牌可以通過請求標頭提供，使用身份驗證持票人方案：`Authorization: Bearer TheTokenHere`。

用戶端也可以通過查詢字符串參數提供訪問令牌：`access_token=TheTokenHere`。此方法已被棄用，以防止訪問令牌在訪問/HTTP 日誌中泄露，用戶端不應使用此方法。

主伺服器必須支持這兩種方法。

> [!NOTE]
> INFO: [Changed-in v1.11] 將訪問令牌作為查詢字符串參數發送現在已被棄用。

當憑據需要但缺失或無效時，HTTP 調用將返回狀態 401 和錯誤代碼，分別為 `M_MISSING_TOKEN` 或 `M_UNKNOWN_TOKEN`。請注意，錯誤代碼 `M_UNKNOWN_TOKEN` 可能意味著以下四種情況之一：

1. 訪問令牌從未有效。
2. 訪問令牌已被註銷。
3. 訪問令牌已被 [軟登出](#soft-logout)。
4. {{< added-in v="1.3" >}} 訪問令牌 [需要刷新](#refreshing-access-tokens)。

當用戶端收到 `M_UNKNOWN_TOKEN` 錯誤代碼時，應：

- 如果有刷新令牌，嘗試 [刷新令牌](#refreshing-access-tokens)；
- 如果 [`soft_logout`](#soft-logout) 設置為 `true`，可以提供重新登錄用戶，保留用戶端的任何持久化資訊；
- 否則，認為用戶已登出。

### 訪問令牌和設備之間的關係

用戶端 [設備](../index.html#devices) 與訪問令牌和刷新令牌密切相關。Matrix 伺服器應記錄每個訪問令牌和刷新令牌分配給哪個設備，以便後續請求可以正確處理。當使用刷新令牌生成新的訪問令牌和刷新令牌時，新訪問令牌和刷新令牌現在綁定到與初始刷新令牌相關的設備。

預設情況下，[登錄](#login) 和 [註冊](#account-registration-and-management) 過程會自動生成新的 `device_id`。用戶端也可以自由生成自己的 `device_id`，或者在用戶保持不變的情況下重用設備：在任一情況下，用戶端應在請求體中傳遞 `device_id`。如果用戶端設置了 `device_id`，伺服器將使之前分配給該設備的任何訪問令牌和刷新令牌失效。

### 刷新訪問令牌

[Added-in v1.3]

訪問令牌可能在一定時間後過期。任何使用過期訪問令牌的 HTTP 調用都會返回錯誤代碼 `M_UNKNOWN_TOKEN`，最好帶有 `soft_logout: true`。當用戶端收到此錯誤並且它有刷新令牌時，應嘗試通過調用 [`/refresh`](#post_matrixclientv3refresh) 刷新訪問令牌。用戶端也可以在任何時候刷新其訪問令牌，即使它尚未過期。如果令牌刷新成功，用戶端應使用新令牌進行未來的請求，並可以使用新令牌重新嘗試先前失敗的請求。當訪問令牌刷新時，可能會返回新的刷新令牌；如果給出了新的刷新令牌，舊的刷新令牌將失效，並且當需要刷新訪問令牌時應使用新的刷新令牌。

舊的刷新令牌在新訪問令牌或刷新令牌被使用之前仍然有效，此時舊的刷新令牌將被撤銷。這確保了如果用戶端未能接收或保存新令牌，它將能夠重複刷新操作。

如果令牌刷新失敗並且錯誤回應包含 `soft_logout: true` 屬性，則用戶端可以將其視為 [軟登出](#soft-logout) 並嘗試通過重新登錄獲取新的訪問令牌。如果錯誤回應不包含 `soft_logout: true` 屬性，用戶端應認為用戶已登出。

不支持刷新令牌的用戶端的處理由主伺服器決定；用戶端通過在 [`/login`](#post_matrixclientv3login) 和 [`/register`](#post_matrixclientv3register) 端點的請求體中包含 `refresh_token: true` 屬性來表明其支持刷新令牌。例如，主伺服器可能允許使用不會過期的訪問令牌，或者仍然使訪問令牌過期並依賴於不支持刷新的用戶端的軟登出行為。

### 軟登出

如果伺服器要求在繼續之前重新驗證，但不希望使用戶端的會話失效，用戶端可以處於「軟登出」狀態。伺服器通過在 `M_UNKNOWN_TOKEN` 錯誤回應中包含 `soft_logout: true` 參數來指示用戶端處於軟登出狀態；`soft_logout` 參數預設為 `false`。如果 `soft_logout` 參數被省略或為 `false`，這意味著伺服器已銷毀會話，用戶端不應重用它。也就是說，用戶端持有的任何持久狀態（如加密密鑰和設備資訊）不得重用，必須丟棄。如果 `soft_logout` 為 `true`，用戶端可以重用任何持久狀態。

{{% changed-in v="1.3" %}} 收到此類回應的用戶端可以嘗試 [刷新其訪問令牌](#refreshing-access-tokens)，如果它有可用的刷新令牌。如果它沒有可用的刷新令牌，或者刷新失敗並且帶有 `soft_logout: true`，用戶端可以通過將其已使用的設備 ID 指定給登錄 API 來獲取新的訪問令牌。

### 用戶互動身份驗證 API

#### 概述

某些 API 端點需要與用戶互動的身份驗證。主伺服器可能提供多種身份驗證方式，如用戶名/密碼身份驗證、通過單點登錄服務器 (SSO) 登錄等。此規範不定義主伺服器應如何授權其用戶，而是定義了實現應遵循的標準接口，以便任何用戶端都可以登錄到任何主伺服器。

該過程以一個或多個“階段”的形式進行。在每個階段，用戶端提交一組給定身份驗證類型的數據並等待伺服器的回應，這可能是最終成功或要求執行另一個階段的請求。這種交換持續進行，直到最終成功。

對於每個端點，伺服器提供一個或多個用戶端可以用來驗證自己的“流程”。每個流程包含一系列階段，如上所述。用戶端可以自由選擇其遵循的流程，但流程的階段必須按順序完成。未按順序遵循流程必須導致 HTTP 401 回應，如下所述。當流程中的所有階段完成時，身份驗證完成，API 調用成功。

#### REST API 中的用戶互動 API

在本規範中描述的 REST API 中，身份驗證通過用戶端和伺服器交換 JSON 字典來工作。伺服器通過 HTTP 401 回應的正文指示所需的身份驗證資料，用戶端通過 `auth` 請求參數提交該身份驗證資料。

用戶端應首先在沒有 `auth` 參數的情況下發出請求。主伺服器返回一個包含 JSON 正文的 HTTP 401 回應，如下所示：

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "flows": [
    {
      "stages": [ "example.type.foo", "example.type.bar" ]
    },
    {
      "stages": [ "example.type.foo", "example.type.baz" ]
    }
  ],
  "params": {
      "example.type.baz": {
          "example_key": "foobar"
      }
  },
  "session": "xxxxxx"
}
```

除了 `flows`，此對象還包含一些額外資訊：

* `params`：此部分包含用戶端在使用給定類型的身份驗證時需要了解的任何資訊。對於每個呈現的身份驗證類型，該類型可能會作為此字典中的鍵出現。例如，可以在這裡給出 OAuth 客戶端 ID 的公共部分。

* `session`：這是一個會話標識符，如果提供了此標識符，用戶端必須在後續嘗試在同一 API 調用中進行身份驗證時將其傳回主伺服器。

然後，用戶端選擇一個流程並嘗試完成第一階段。它通過重新提交相同的請求，並在提交的對象中添加一個 `auth` 鍵來完成這一點。此字典包含一個 `type` 鍵，其值是用戶端嘗試完成的身份驗證類型的名稱。它還必須包含一個 `session` 鍵，其值是主伺服器提供的會話鍵（如果有的話）。此外，它還包含根據正在嘗試的身份驗證類型而定的其他鍵。例如，如果用戶端嘗試完成身份驗證類型 `example.type.foo`，它可能會提交如下所示的內容：

```
POST /_matrix/client/v3/endpoint HTTP/1.1
Content-Type: application/json
```

```json
{
  "a_request_parameter": "something",
  "another_request_parameter": "something else",
  "auth": {
      "type": "example.type.foo",
      "session": "xxxxxx",
      "example_credential": "verypoorsharedsecret"
  }
}
```

如果主伺服器認為身份驗證嘗試成功但仍需完成更多階段，它會返回 HTTP 狀態 401，並返回與未嘗試身份驗證時相同的對象，附加一個 completed 鍵，該鍵是一個用戶端已成功完成的身份驗證類型的數組：

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "completed": [ "example.type.foo" ],
  "flows": [
    {
      "stages": [ "example.type.foo", "example.type.bar" ]
    },
    {
      "stages": [ "example.type.foo", "example.type.baz" ]
    }
  ],
  "params": {
      "example.type.baz": {
          "example_key": "foobar"
      }
  },
  "session": "xxxxxx"
}
```

各個階段可能需要多次請求才能完成，在這種情況下，回應將如同請求未經身份驗證，並附加身份驗證類型定義的任何其他鍵。

如果主伺服器認為某個階段的嘗試不成功，但用戶端可以再嘗試一次，它將返回與上述相同的 HTTP 狀態 401 回應，並附加描述錯誤的標準 `errcode` 和 `error` 字段。例如：

```
HTTP/1.1 401 Unauthorized
Content-Type: application/json
```

```json
{
  "errcode": "M_FORBIDDEN",
  "error": "Invalid password",
  "completed": [ "example.type.foo" ],
  "flows": [
    {
      "stages": [ "example.type.foo", "example.type.bar" ]
    },
    {
      "stages": [ "example.type.foo", "example.type.baz" ]
    }
  ],
  "params": {
      "example.type.baz": {
          "example_key": "foobar"
      }
  },
  "session": "xxxxxx"
}
```

如果請求因身份驗證以外的原因失敗，伺服器會以標準格式傳回錯誤訊息。例如：

```
HTTP/1.1 400 Bad request
Content-Type: application/json
```

```json
{
  "errcode": "M_EXAMPLE_ERROR",
  "error": "Something was wrong"
}
```

如果用戶端已完成某個流程的所有階段，主伺服器將執行 API 請求並正常返回結果。用戶端不能重試已完成的階段，因此伺服器必須返回包含已完成階段的 401 回應，或者在用戶端重試某個階段時，如果所有階段已完成，則返回 API 請求的結果。

某些身份驗證類型可以通過 Matrix 用戶端之外的方式完成，例如，當用戶點擊電子郵件中的鏈接時，電子郵件確認可以完成。在這種情況下，用戶端重試請求時，提交的身份驗證字典只包含會話鍵。此時的回應與用戶端正常完成身份驗證階段時相同，即請求將要麼完成，要麼請求身份驗證，且根據該身份驗證類型在“completed”數組中的存在或缺失來指示該階段是否完成。

> [!NOTE]
> INFO: 對使用用戶互動身份驗證的端點的請求，在沒有身份驗證的情況下永遠不會成功。主伺服器可以通過提供只有 `m.login.dummy` 身份驗證類型的階段來允許不需要身份驗證的請求，但它們仍然必須對沒有身份驗證數據的請求給出 401 回應。

#### 範例

在高層次上，為完成具有三個階段的身份驗證流程的 API 請求所做的請求類似於以下圖表：

```
    _______________________
    |       Stage 0         |
    | No auth               |
    |  ___________________  |
    | |_Request_1_________| | <-- 傳回自始至終使用的「會話」金鑰
    |_______________________|
             |
             |
    _________V_____________
    |       Stage 1         |
    | type: "<auth type1>"  |
    |  ___________________  |
    | |_Request_1_________| |
    |_______________________|
             |
             |
    _________V_____________
    |       Stage 2         |
    | type: "<auth type2>"  |
    |  ___________________  |
    | |_Request_1_________| |
    |  ___________________  |
    | |_Request_2_________| |
    |  ___________________  |
    | |_Request_3_________| |
    |_______________________|
             |
             |
    _________V_____________
    |       Stage 3         |
    | type: "<auth type3>"  |
    |  ___________________  |
    | |_Request_1_________| | <-- 回傳 API 回應
    |_______________________|
```

#### 身份驗證類型

本規範定義了以下身份驗證類型：
-   `m.login.password`
-   `m.login.recaptcha`
-   `m.login.sso`
-   `m.login.email.identity`
-   `m.login.msisdn`
-   `m.login.dummy`
-   `m.login.registration_token`

##### 基於密碼的驗證

| 類型               | 描述                                                                    |
|--------------------|--------------------------------------------------------------------------|
| `m.login.password` | 用戶端提交標識符和密碼，兩者均以純文本形式發送。 |

要使用這種類型的身份驗證，用戶端應提交如下所示的身份驗證字典：

```
{
  "type": "m.login.password",
  "identifier": {
    ...
  },
  "password": "<password>",
  "session": "<session ID>"
}
```

其中 `identifier` 屬性是一個用戶標識符對象，如[標識符類型](#identifier-types)中所述。

例如，要使用用戶的 Matrix ID 進行身份驗證，用戶端將提交：

```json
{
  "type": "m.login.password",
  "identifier": {
    "type": "m.id.user",
    "user": "<user_id or user localpart>"
  },
  "password": "<password>",
  "session": "<session ID>"
}
```

或者，可以使用 [`/account/3pid`](#get_matrixclientv3account3pid) API 綁定到用戶帳戶的 3PID 來回應，而不是明確提供 `user`，如下所示：

```json
{
  "type": "m.login.password",
  "identifier": {
    "type": "m.id.thirdparty",
    "medium": "<The medium of the third-party identifier.>",
    "address": "<The third-party address of the user>"
  },
  "password": "<password>",
  "session": "<session ID>"
}
```

如果主伺服器不知道所提供的 3PID，則主伺服器必須回應 403 Forbidden。

##### Google ReCaptcha

| 類型                | 描述                                          |
|---------------------|----------------------------------------------|
| `m.login.recaptcha` | 用戶完成 Google ReCaptcha 2.0 驗證挑戰。 |

要使用這種類型的身份驗證，用戶端應提交如下所示的身份驗證字典：

```json
{
  "type": "m.login.recaptcha",
  "response": "<captcha response>",
  "session": "<session ID>"
}
```

##### 單一登錄

| 類型          | 描述                                                                          |
|---------------|--------------------------------------------------------------------------------------|
| `m.login.sso` | 通過外部單一登錄提供商授權進行身份驗證。 |

希望使用單一登錄完成身份驗證的用戶端應使用[回退](#fallback)機制。更多信息請參見[用戶交互身份驗證中的單一登錄](#sso-during-user-interactive-authentication)。

##### 基於電子郵件的驗證 (身份伺服器/主伺服器)

| 類型                     | 描述                                                                                                      |
|--------------------------|-----------------------------------------------------------------------------------------------------------|
| `m.login.email.identity` | 通過身份伺服器或主伺服器（如果支持）授權電子郵件地址進行身份驗證。 |

在提交此驗證之前，用戶端應先與身份伺服器（或主伺服器）進行身份驗證。身份驗證後，應將會話資訊提交給主伺服器。

要使用這種類型的身份驗證，用戶端應提交如下所示的身份驗證字典：

```json
{
  "type": "m.login.email.identity",
  "threepid_creds": {
    "sid": "<identity server session id>",
    "client_secret": "<identity server client secret>",
    "id_server": "<url of identity server authed with, e.g. 'matrix.org:8090'>",
    "id_access_token": "<access token previously registered with the identity server>"
  },
  "session": "<session ID>"
}
```

請注意，如果 `/requestToken` 請求中未包含 `id_server`（因此也不包含 `id_access_token`），則 `id_server`（因此也不包含 `id_access_token`）是可選的。

##### 基於電話號碼/MSISDN的驗證 (身份伺服器/主伺服器)

| 類型             | 描述                                                                                                    |
|------------------|---------------------------------------------------------------------------------------------------------|
| `m.login.msisdn` | 通過身份伺服器或主伺服器（如果支持）授權電話號碼進行身份驗證。 |

在提交此驗證之前，用戶端應先與身份伺服器（或主伺服器）進行身份驗證。身份驗證後，應將會話資訊提交給主伺服器。

要使用這種類型的身份驗證，用戶端應提交如下所示的身份驗證字典：

```json
{
  "type": "m.login.msisdn",
  "threepid_creds": {
    "sid": "<identity server session id>",
    "client_secret": "<identity server client secret>",
    "id_server": "<url of identity server authed with, e.g. 'matrix.org:8090'>",
    "id_access_token": "<access token previously registered with the identity server>"
  },
  "session": "<session ID>"
}
```

請注意，如果 `/requestToken` 請求中未包含 `id_server`（因此也不包含 `id_access_token`），則 `id_server`（因此也不包含 `id_access_token`）是可選的。

##### 假身份驗證

| 類型             | 描述                                                            |
|------------------|----------------------------------------------------------------|
| `m.login.dummy`  | 假身份驗證總是成功且不需要額外的參數。 |

假身份驗證的目的是允許伺服器不需要任何形式的用戶交互身份驗證即可執行請求。它還可以用於區分流，其中一個流可能是另一個流的子集。例如，如果伺服器提供 `m.login.recaptcha` 和 `m.login.recaptcha, m.login.email.identity` 流，並且用戶端首先完成了 recaptcha 階段，則身份驗證將成功通過前一個流，即使用戶端打算隨後完成電子郵件驗證階段。伺服器可以改為發送 `m.login.recaptcha, m.login.dummy` 和 `m.login.recaptcha, m.login.email.identity` 流來解決這種歧義。

要使用這種類型的身份驗證，用戶端應提交僅包含類型和會話（如果提供）的身份驗證字典：

```json
{
  "type": "m.login.dummy",
  "session": "<session ID>"
}
```

##### 基於令牌的註冊

[Added-in v1.2]

| 類型                          | 描述                                                       |
|-------------------------------|------------------------------------------------------------|
| `m.login.registration_token`  | 使用預共享的令牌進行身份驗證來註冊帳戶。 |

{{% boxes/note %}}
`m.login.registration_token` 身份驗證類型僅在 [`/register`](#post_matrixclientv3register) 端點上有效。
{{% /boxes/note %}}

這種類型的身份驗證使主伺服器能夠允許有限的一組人註冊帳戶，而不是提供完全開放的註冊或完全關閉的註冊（由主伺服器管理員創建並分發帳戶）。

此身份驗證類型所需的令牌在 Matrix 外部共享，並使用[不透明標識符語法](/appendices#opaque-identifiers)作為不透明字符串，最大長度為64個字符。伺服器可以保留任意數量的令牌，且有效時間不限。這種情況可能是令牌限制為100次使用或僅在接下來的2小時內有效——令牌過期後，無法再用於創建帳戶。

要使用這種類型的身份驗證，用戶端應提交僅包含類型、令牌和會話的身份驗證字典：

```json
{
  "type": "m.login.registration_token",
  "token": "fBVFdqVE",
  "session": "<session ID>"
}
```

為了在使用令牌之前確定其是否有效，用戶端可以使用下面定義的 `/validity` API。該 API 無法保證令牌在使用時仍然有效，但可以避免用戶在註冊過程後期發現令牌已過期的情況。

{{% http-api spec="client-server" api="registration_tokens" %}}

##### 註冊時的服務條款

[Added-in v1.11]

| 類型                     | 描述                                                              |
|--------------------------|------------------------------------------------------------------|
| `m.login.terms`          | 身份驗證要求用戶接受一組政策文件。                               |

> [!NOTE]
> INFO: `m.login.terms` 身份驗證類型僅在 [`/register`](#post_matrixclientv3register) 端點上有效。

當主伺服器要求新用戶接受一組政策文件（例如服務條款和隱私政策）時，會使用這種類型的身份驗證。可能會有許多不同類型的文件，所有這些文件都是版本化的，並且以（可能）多種語言呈現。

當伺服器要求用戶接受一些條款時，會通過返回401回應來回應 `/register` 請求，其中回應主體包括 `flows` 列表中的 `m.login.terms`，以及 `params` 對象中的 `m.login.terms` 屬性，其結構如下所示 [定義-mloginterms-params](#definition-mloginterms-params)。

如果用戶端遇到無效參數，註冊應停止並向用戶顯示錯誤。

用戶端應向用戶展示一個復選框以接受每個政策，包括提供的 URL 鏈接。一旦用戶這樣做，用戶端應提交一個僅包含 `type` 和 `session` 的 `auth` 字典，如下所示，以表示所有政策都已被接受：

```json
{
  "type": "m.login.terms",
  "session": "<session ID>"
}
```

伺服器應追蹤在註冊期間向用戶呈現的文件版本（如果適用）。

**示例**

1. 用戶端可能會提交如下所示的註冊請求：

   ```
   POST /_matrix/client/v3/register
   ```
   ```json
   {
     "username": "cheeky_monkey",
     "password": "ilovebananas"
   }
   ```

2. 伺服器要求用戶在註冊前接受一些服務條款，因此返回以下回應：

   ```
   HTTP/1.1 401 Unauthorized
   Content-Type: application/json
   ```
   ```json
   {
     "flows": [
       { "stages": [ "m.login.terms" ] }
     ],
     "params": {
       "m.login.terms": {
         "policies": {
           "terms_of_service": {
             "version": "1.2",
             "en": {
                 "name": "Terms of Service",
                 "url": "https://example.org/somewhere/terms-1.2-en.html"
             },
             "fr": {
                 "name": "Conditions d'utilisation",
                 "url": "https://example.org/somewhere/terms-1.2-fr.html"
             }
           }
         }
       }
     },
     "session": "kasgjaelkgj"
   }
   ```

3. 用戶端向用戶展示文件列表，邀請他們接受這些政策。

4. 用戶端重複註冊請求，確認用戶已接受這些文件：
   ```
   POST /_matrix/client/v3/register
   ```
   ```json
   {
     "username": "cheeky_monkey",
     "password": "ilovebananas",
     "auth": {
       "type": "m.login.terms",
       "session": "kasgjaelkgj"
     }
   }
   ```

5. 所有身份驗證步驟均已完成，請求成功：
   ```
   HTTP/1.1 200 OK
   Content-Type: application/json
   ```
   ```json
   {
     "access_token": "abc123",
     "device_id": "GHTYAJCE",
     "user_id": "@cheeky_monkey:matrix.org"
   }
   ```

{{% definition path="api/client-server/definitions/m.login.terms_params" %}}

#### 後備機制

不能期望用戶端能夠知道如何處理每種登入類型。如果用戶端不知道如何處理給定的登入類型，它可以將使用者引導到具有後備頁面 URL 的 Web 瀏覽器，這將允許使用者在其 Web 瀏覽器中帶外完成該登入步驟。它應該打開的 URL 是：

    /_matrix/client/v3/auth/<auth type>/fallback/web?session=<session ID>

其中 `auth type` 是其嘗試的階段的類型名稱，`session ID` 是由主伺服器提供的會話 ID。

這必須返回一個可以執行此身份驗證階段的 HTML 頁面。當身份驗證完成時，該頁面必須使用以下 JavaScript：

```js
if (window.onAuthDone) {
    window.onAuthDone();
} else if (window.opener && window.opener.postMessage) {
    window.opener.postMessage("authDone", "*");
}
```

這允許用戶端安排在嵌入的瀏覽器中定義全局函數 `onAuthDone`，或使用 HTML5 [跨文檔消息傳遞](https://www.w3.org/TR/webmessaging/#web-messaging) API，來接收身份驗證階段已完成的通知。

一旦用戶端收到身份驗證階段已完成的通知，它應提交一個僅包含會話 ID 的 `auth` 字典：

```json
{
  "session": "<session ID>"
}
```

##### 示例

用戶端 Web 應用程序可能會使用以下 JavaScript 打開一個彈出窗口來處理未知的登入類型：

```js
/**
 * 參數:
 *     homeserverUrl: 主伺服器的基本 URL（例如 "https://matrix.org"）
 *
 *     apiEndpoint: 正在使用的 API 端點（例如 "/_matrix/client/v3/account/password"）
 *
 *     loginType: 正在嘗試的 loginType（例如 "m.login.recaptcha"）
 *
 *     sessionID: 在早期請求中由主伺服器提供的會話 ID
 *
 *     onComplete: 一個回調函數，將在請求結果中調用
 */
function unknownLoginType(homeserverUrl, apiEndpoint, loginType, sessionID, onComplete) {
    var popupWindow;

    var eventListener = function(ev) {
        // check it's the right message from the right place.
        if (ev.data !== "authDone" || ev.origin !== homeserverUrl) {
            return;
        }

        // close the popup
        popupWindow.close();
        window.removeEventListener("message", eventListener);

        // repeat the request
        var requestBody = {
            auth: {
                session: sessionID,
            },
        };

        request({
            method:'POST', url:apiEndpoint, json:requestBody,
        }, onComplete);
    };

    window.addEventListener("message", eventListener);

    var url = homeserverUrl +
        "/_matrix/client/v3/auth/" +
        encodeURIComponent(loginType) +
        "/fallback/web?session=" +
        encodeURIComponent(sessionID);

   popupWindow = window.open(url);
}
```

#### 身份標識類型

一些身份驗證機制使用用戶身份標識對象來識別用戶。用戶身份標識對象具有一個 `type` 字段來指示所使用的標識類型，並且根據類型，具有其他字段提供識別用戶所需的信息，如下所述。

本規範定義了以下標識類型：
- `m.id.user`
- `m.id.thirdparty`
- `m.id.phone`

##### Matrix 使用者 ID

| 類型           | 描述                                   |
|----------------|----------------------------------------|
| `m.id.user`    | 用戶通過其 Matrix ID 被識別。           |

客戶端可以使用用戶的 Matrix ID 識別用戶。這可以是完全合格的 Matrix 用戶 ID，或者只是用戶 ID 的 localpart。

```json
"identifier": {
  "type": "m.id.user",
  "user": "<user_id 或 user localpart>"
}
```

##### 第三方 ID

| 類型                | 描述                                                         |
|---------------------|--------------------------------------------------------------|
| `m.id.thirdparty`   | 用戶通過第三方標識符的標準化形式被識別。                     |

客戶端可以使用與用戶帳戶關聯的 3PID 識別用戶，其中 3PID 先前已使用 [`/account/3pid`](#get_matrixclientv3account3pid) API 關聯。請參閱 [3PID 類型](/appendices#3pid-types) 附錄以獲取第三方 ID 媒體的列表。

```json
"identifier": {
  "type": "m.id.thirdparty",
  "medium": "<第三方標識符的媒體>",
  "address": "<用戶的標準化第三方地址>"
}
```

##### 電話號碼

| 類型            | 描述                               |
|-----------------|------------------------------------|
| `m.id.phone`    | 用戶通過電話號碼被識別。            |

客戶端可以使用與用戶帳戶關聯的電話號碼識別用戶，其中電話號碼先前已使用 [`/account/3pid`](#get_matrixclientv3account3pid) API 關聯。電話號碼可以按用戶輸入的方式傳遞；主伺服器將負責將其標準化。如果客戶端希望將電話號碼標準化，那麼它可以使用 `m.id.thirdparty` 標識符類型，`medium` 為 `msisdn`。

```json
"identifier": {
  "type": "m.id.phone",
  "country": "<電話號碼所在的國家>",
  "phone": "<電話號碼>"
}
```

`country` 是電話號碼應該解析為來自哪個國家的兩個字母大寫 ISO-3166-1 alpha-2 國家代碼。

### 登入

客戶端可以使用 `/login` API 獲取訪問令牌。

注意，目前此端點 **不** 使用 [使用者互動身份驗證 API](#user-interactive-authentication-api)。

對於簡單的用戶名/密碼登入，客戶端應提交如下的 `/login` 請求：

```json
{
  "type": "m.login.password",
  "identifier": {
    "type": "m.id.user",
    "user": "<user_id 或 user localpart>"
  },
  "password": "<password>"
}
```

或者，客戶端可以使用與用戶帳戶在主伺服器上綁定的 3PID，而不是明確地給出 `user`，如下所示：

```json
{
  "type": "m.login.password",
  "identifier": {
    "medium": "<第三方標識符的媒體>",
    "address": "<用戶的標準化第三方地址>"
  },
  "password": "<password>"
}
```

如果主伺服器不知道提供的 3PID，主伺服器必須回應 `403 Forbidden`。

要使用登入令牌登入，客戶端應提交如下的 `/login` 請求：

```json
{
  "type": "m.login.token",
  "token": "<登入令牌>"
}
```

`token` 必須編碼用戶 ID，因為請求中沒有其他識別數據。如果令牌無效，主伺服器必須回應 `403 Forbidden` 並提供錯誤代碼 `M_FORBIDDEN`。

如果主伺服器宣傳 `m.login.sso` 為可行的流程，並且客戶端支持它，客戶端應該將用戶重定向到 `/redirect` 端點進行 [通過 SSO 客戶端登入](#client-login-via-sso)。身份驗證完成後，客戶端需要提交與 `m.login.token` 匹配的 `/login` 請求。

{{< added-in v="1.7" >}} 已經驗證的客戶端還可以使用主伺服器支持的 [`POST /login/get_token`](/client-server-api/#post_matrixclientv1loginget_token) 為其用戶 ID 生成一個令牌。

{{% http-api spec="client-server" api="login" %}}

{{% http-api spec="client-server" api="login_token" %}}

{{% http-api spec="client-server" api="refresh" %}}

{{% http-api spec="client-server" api="logout" %}}

#### 應用服務登入

{{% added-in v="1.2" %}}

應用服務可以通過提供有效的應用服務令牌和應用服務命名空間內的用戶來進行登入。

{{% boxes/note %}}
應用服務不需要在所有情況下以單個用戶的身份登入，因為它們可以使用應用服務令牌進行 [身份認證](/application-service-api#identity-assertion)。
然而，如果應用服務需要針對單個用戶的範圍令牌，那麼它們可以使用此 API。
{{% /boxes/note %}}

此請求必須通過 [應用服務 `as_token`](/application-service-api#registration) 進行身份驗證（請參閱 [客戶端身份驗證](#client-authentication) 瞭解如何提供令牌）。

要使用此登入類型，客戶端應提交如下的 `/login` 請求：

```json
{
  "type": "m.login.application_service",
  "identifier": {
    "type": "m.id.user",
    "user": "<user_id 或 user localpart>"
  }
}
```

如果訪問令牌無效、不對應於應用服務或用戶尚未註冊，則主伺服器將回應錯誤代碼 `M_FORBIDDEN`。

如果訪問令牌對應於應用服務，但用戶 ID 不在其命名空間內，則主伺服器將回應錯誤代碼 `M_EXCLUSIVE`。

#### 登入後備機制

如果客戶端不識別任何或所有登入流程，它可以使用後備登入 API：

    GET /_matrix/static/client/login/

這將返回一個可以執行整個登入過程的 HTML 和 JavaScript 頁面。該頁面將嘗試在登入成功完成後調用 JavaScript 函數 `window.onLogin`。

{{% added-in v="1.1" %}} 對於 `/login` 端點有效的非憑證參數可以作為查詢字符串參數提供在此處。在登入過程中，這些參數將被轉發到登入端點。例如：

    GET /_matrix/static/client/login/?device_id=GHTYAJCE

### 帳戶註冊與管理

{{% http-api spec="client-server" api="registration" %}}

#### 密碼管理說明

{{% boxes/warning %}}
客戶端應該強制執行提供的密碼具有足夠的複雜性。密碼應該包括一個小寫字母、一個大寫字母、一個數字和一個符號，且最少為8個字符。伺服器可以以錯誤代碼 `M_WEAK_PASSWORD` 拒絕弱密碼。
{{% /boxes/warning %}}

### 添加帳戶管理聯繫信息

主伺服器可以保存一些供管理使用的聯繫信息。這獨立於任何身份伺服器保存的信息，雖然在許多情況下可以代理（綁定）到身份伺服器。

{{% boxes/note %}}
本節涉及兩個術語：“添加”和“綁定”。當使用“添加”（或“刪除”）時，它指的是未綁定到身份伺服器的標識。因此，“綁定”（或“解除綁定”）指的是在身份伺服器中找到的標識。請注意，根據上下文，標識可以同時添加和綁定。
{{% /boxes/note %}}

{{% http-api spec="client-server" api="administrative_contact" %}}

### 當前帳戶信息

{{% http-api spec="client-server" api="whoami" %}}

#### 關於身份伺服器的說明

Matrix 中的身份伺服器存儲用戶的第三方標識（通常是電子郵件或電話號碼）和他們的用戶 ID 之間的綁定（關係）。一旦用戶選擇了一個身份伺服器，該身份伺服器應該由所有客戶端使用。

客戶端可以通過 `m.identity_server` 帳戶數據事件查看用戶選擇的身份伺服器，如下所述。在確認 `m.identity_server` 存在之前，客戶端應避免向任何身份伺服器發出請求。如果存在，客戶端應檢查事件內容中是否存在 `base_url` 屬性。如果存在 `base_url`，客戶端應使用該屬性中的身份伺服器作為用戶的身份伺服器。如果 `base_url` 丟失或帳戶數據事件不存在，客戶端應使用它通常使用的默認身份伺服器（如果適用）。當用戶的帳戶數據中缺少身份伺服器時，客戶端不應使用默認身份伺服器更新帳戶數據。

客戶端應監聽 `m.identity_server` 帳戶數據事件的變更並相應地更新其正在聯繫的身份伺服器。

如果客戶端提供了設置身份伺服器的方式，它必須相應地更新 `m.identity_server` 的值。`base_url` 為 `null` 時必須被視為用戶不希望使用身份伺服器，從而禁用所有相關功能。

客戶端應避免為缺少帳戶數據的用戶填充帳戶數據作為遷移步驟，除非用戶在客戶端中將身份伺服器設置為某個值。例如，沒有 `m.identity_server` 帳戶數據事件的用戶不應最終在其帳戶數據中獲得客戶端的默認身份伺服器，除非用戶首先訪問其帳戶設置來設置身份伺服器。

{{% event event="m.identity_server" %}}

## 能力協商

主伺服器可能不支持某些操作，客戶端必須能夠查詢主伺服器可以和不能提供的功能。例如，主伺服器可能不支持用戶更改其密碼，因為它被配置為對外部系統進行身份驗證。

通過此系統廣告的功能旨在廣告 API 中的可選功能，或者在某種程度上取決於用戶或服務器的狀態。此系統不應用於廣告不穩定或實驗性功能 - 這更適合通過 `/versions` 端點進行。

一些合理功能的示例包括：

- 服務器是否支持用戶存在。
- 服務器是否支持可選功能，例如用戶或房間目錄。
- 服務器對客戶端施加的速率限制或文件類型限制。

一些不應作為功能的示例包括：

- 服務器是否支持 `unstable` 規範中的功能。
- 媒體大小限制 - 這些由 [`/config`](#get_matrixmediav3config) API 處理。
- 與服務器通信的可選編碼或替代傳輸方式。

以 `m.` 為前綴的功能保留給 Matrix 規範中的定義，而其他值可以由使用 Java 包命名約定的服務器使用。Matrix 規範支持的功能在本節後面定義。

{{% http-api spec="client-server" api="capabilities" %}}

### `m.change_password` 功能

此功能具有單個標誌 `enabled`，用於指示用戶是否可以使用 `/account/password` API 來更改其密碼。如果未出現此標誌，客戶端應假設可以通過 API 更改密碼。如果存在，客戶端應尊重該功能的 `enabled` 標誌，並向用戶表明是否無法更改其密碼。

此功能的能力 API 回應示例如下：

```json
{
  "capabilities": {
    "m.change_password": {
      "enabled": false
    }
  }
}
```

### `m.room_versions` 功能

此功能描述了伺服器支援的默認和可用房間版本及其穩定性級別。客戶端應使用此功能來確定是否需要鼓勵用戶升級他們的房間。

此功能的能力 API 回應示例如下：

```json
{
  "capabilities": {
    "m.room_versions": {
      "default": "1",
      "available": {
        "1": "stable",
        "2": "stable",
        "3": "unstable",
        "custom-version": "unstable"
      }
    }
  }
}
```

此功能反映了[房間版本](/rooms)的相同限制，以描述哪些版本是穩定的，哪些是不穩定的。客戶端應假設 `default` 版本是 `stable`。任何未在 `available` 版本中明確標記為 `stable` 的版本都應被視為 `unstable`。例如，列為 `future-stable` 的版本應被視為 `unstable`。

`default` 版本是伺服器用來創建新房間的版本。當房間使用 `unstable` 版本時，客戶端應鼓勵具有足夠權限的用戶將其房間升級到 `default` 版本。

當此功能未列出時，客戶端應使用 `"1"` 作為默認和唯一穩定的 `available` 房間版本。

### `m.set_displayname` 功能

此功能具有單個標誌 `enabled`，用於表示用戶是否能夠通過配置檔端點更改自己的顯示名稱。禁用的情況可能包括從外部身份/目錄服務（如 LDAP）映射的用戶。

請注意，此功能與 `m.set_avatar_url` 功能相配合使用。

當未列出此功能時，客戶端應假設用戶可以更改其顯示名稱。

此功能的能力 API 回應示例如下：

```json
{
  "capabilities": {
    "m.set_displayname": {
      "enabled": false
    }
  }
}
```

### `m.set_avatar_url` 功能

此功能具有單個標誌 `enabled`，用於表示用戶是否能夠通過配置檔端點更改自己的頭像。禁用的情況可能包括從外部身份/目錄服務（如 LDAP）映射的用戶。

請注意，此功能與 `m.set_displayname` 功能相配合使用。

當未列出此功能時，客戶端應假設用戶可以更改其頭像。

此功能的能力 API 回應示例如下：

```json
{
  "capabilities": {
    "m.set_avatar_url": {
      "enabled": false
    }
  }
}
```

### `m.3pid_changes` 功能

此功能具有單個標誌 `enabled`，用於表示用戶是否能夠在其帳戶上添加、刪除或更改 3PID 關聯。請注意，這僅影響用戶使用[管理聯繫信息](#adding-account-administrative-contact-information) API 的能力，而不影響身份服務暴露的端點。禁用的情況可能包括從外部身份/目錄服務（如 LDAP）映射的用戶。

當未列出此功能時，客戶端應假設用戶可以修改其 3PID 關聯。

此功能的能力 API 回應示例如下：

```json
{
  "capabilities": {
    "m.3pid_changes": {
      "enabled": false
    }
  }
}
```

## Filtering

Filters can be created on the server and can be passed as a parameter to
APIs which return events. These filters alter the data returned from
those APIs. Not all APIs accept filters.

### Lazy-loading room members

Membership events often take significant resources for clients to track.
In an effort to reduce the number of resources used, clients can enable
"lazy-loading" for room members. By doing this, servers will attempt to
only send membership events which are relevant to the client.

It is important to understand that lazy-loading is not intended to be a
perfect optimisation, and that it may not be practical for the server to
calculate precisely which membership events are relevant to the client.
As a result, it is valid for the server to send redundant membership
events to the client to ease implementation, although such redundancy
should be minimised where possible to conserve bandwidth.

In terms of filters, lazy-loading is enabled by enabling
`lazy_load_members` on a `RoomEventFilter` (or a `StateFilter` in the
case of `/sync` only). When enabled, lazy-loading aware endpoints (see
below) will only include membership events for the `sender` of events
being included in the response. For example, if a client makes a `/sync`
request with lazy-loading enabled, the server will only return
membership events for the `sender` of events in the timeline, not all
members of a room.

When processing a sequence of events (e.g. by looping on `/sync` or
paginating `/messages`), it is common for blocks of events in the
sequence to share a similar set of senders. Rather than responses in the
sequence sending duplicate membership events for these senders to the
client, the server MAY assume that clients will remember membership
events they have already been sent, and choose to skip sending
membership events for members whose membership has not changed. These
are called 'redundant membership events'. Clients may request that
redundant membership events are always included in responses by setting
`include_redundant_members` to true in the filter.

The expected pattern for using lazy-loading is currently:

-   Client performs an initial /sync with lazy-loading enabled, and
    receives only the membership events which relate to the senders of
    the events it receives.
-   Clients which support display-name tab-completion or other
    operations which require rapid access to all members in a room
    should call /members for the currently selected room, with an `?at`
    parameter set to the /sync response's from token. The member list
    for the room is then maintained by the state in subsequent
    incremental /sync responses.
-   Clients which do not support tab-completion may instead pull in
    profiles for arbitrary users (e.g. read receipts, typing
    notifications) on demand by querying the room state or `/profile`.

The current endpoints which support lazy-loading room members are:

-   [`/sync`](/client-server-api/#get_matrixclientv3sync)
-   [`/rooms/<room_id>/messages`](/client-server-api/#get_matrixclientv3roomsroomidmessages)
-   [`/rooms/{roomId}/context/{eventId}`](/client-server-api/#get_matrixclientv3roomsroomidcontexteventid)

### API endpoints

{{% http-api spec="client-server" api="filter" %}}

## Events

The model of conversation history exposed by the client-server API can
be considered as a list of events. The server 'linearises' the
eventually-consistent event graph of events into an 'event stream' at
any given point in time:

    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]

### Types of room events

Room events are split into two categories:

* **State events**: These are events which update the metadata state of the room (e.g. room
topic, room membership etc). State is keyed by a tuple of event `type`
and a `state_key`. State in the room with the same key-tuple will be
overwritten.

* **Message events**: These are events which describe transient "once-off" activity in a room:
typically communication such as sending an instant message or setting up
a VoIP call.

This specification outlines several events, all with the event type
prefix `m.`. (See [Room Events](#room-events) for the m. event
specification.) However, applications may wish to add their own type of
event, and this can be achieved using the REST API detailed in the
following sections. If new events are added, the event `type` key SHOULD
follow the Java package naming convention, e.g.
`com.example.myapp.event`. This ensures event types are suitably
namespaced for each application and reduces the risk of clashes.

{{% boxes/note %}}
Events are not limited to the types defined in this specification. New
or custom event types can be created on a whim using the Java package
naming convention. For example, a `com.example.game.score` event can be
sent by clients and other clients would receive it through Matrix,
assuming the client has access to the `com.example` namespace.
{{% /boxes/note %}}

### Room event format

The "federation" format of a room event, which is used internally by homeservers
and between homeservers via the Server-Server API, depends on the ["room
version"](/rooms) in use by the room. See, for example, the definitions
in [room version 1](/rooms/v1#event-format) and [room version
3](/rooms/v3#event-format).

However, it is unusual that a Matrix client would encounter this event
format. Instead, homeservers are responsible for converting events into the
format shown below so that they can be easily parsed by clients.

{{% boxes/warning %}}
Event bodies are considered untrusted data. This means that any application using
Matrix must validate that the event body is of the expected shape/schema
before using the contents verbatim.

**It is not safe to assume that an event body will have all the expected
fields of the expected types.**

See [MSC2801](https://github.com/matrix-org/matrix-spec-proposals/pull/2801) for more
detail on why this assumption is unsafe.
{{% /boxes/warning %}}

{{% definition path="api/client-server/definitions/client_event" %}}

### Stripped state

Stripped state is a simplified view of the state of a room intended to help a
potential joiner identify the room. It consists of a limited set of state events
that are themselves simplified to reduce the amount of data required.

Stripped state events can only have the `sender`, `type`, `state_key` and
`content` properties present.

Stripped state typically appears in invites, knocks, and in other places where a
user *could* join the room under the conditions available (such as a
[`restricted` room](#restricted-rooms)).

Clients should only use stripped state events when they don't have
access to the proper state of the room. Once the state of the room is
available, all stripped state should be discarded. In cases where the
client has an archived state of the room (such as after being kicked)
and the client is receiving stripped state for the room, such as from an
invite or knock, then the stripped state should take precedence until
fresh state can be acquired from a join.

Stripped state should contain some or all of the following state events, which
should be represented as stripped state events when possible:

* [`m.room.create`](#mroomcreate)
* [`m.room.name`](#mroomname)
* [`m.room.avatar`](#mroomavatar)
* [`m.room.topic`](#mroomtopic)
* [`m.room.join_rules`](#mroomjoin_rules)
* [`m.room.canonical_alias`](#mroomcanonical_alias)
* [`m.room.encryption`](#mroomencryption)

{{% boxes/note %}}
Clients should inspect the list of stripped state events and not assume any
particular event is present. The server might include events not described
here as well.
{{% /boxes/note %}}

{{% boxes/rationale %}}
The name, avatar, topic, and aliases are presented as aesthetic information
about the room, allowing users to make decisions about whether or not they
want to join the room.

The join rules are given to help the client determine *why* it is able to
potentially join. For example, annotating the room decoration with iconography
consistent with the respective join rule for the room.

The create event can help identify what kind of room is being joined, as it
may be a Space or other kind of room. The client might choose to render the
invite in a different area of the application as a result.

Similar to join rules, the encryption information is given to help clients
decorate the room with appropriate iconography or messaging.
{{% /boxes/rationale %}}

{{% boxes/warning %}}
Although stripped state is usually generated and provided by the server, it
is still possible to be incorrect on the receiving end. The stripped state
events are not signed and could theoretically be modified, or outdated due to
updates not being sent.
{{% /boxes/warning %}}

{{% event-fields event_type="stripped_state" %}}

### Size limits

The complete event MUST NOT be larger than 65536 bytes, when formatted
with the [federation event format](#room-event-format), including any
signatures, and encoded as [Canonical JSON](/appendices#canonical-json).

There are additional restrictions on sizes per key:

-   `sender` MUST NOT exceed the size limit for [user IDs](/appendices/#user-identifiers).
-   `room_id` MUST NOT exceed the size limit for [room IDs](/appendices/#room-ids).
-   `state_key` MUST NOT exceed 255 bytes.
-   `type` MUST NOT exceed 255 bytes.
-   `event_id` MUST NOT exceed the size limit for [event IDs](/appendices/#event-ids).

Some event types have additional size restrictions which are specified
in the description of the event. Additional keys have no limit other
than that implied by the total 64 KiB limit on events.

### Room Events

{{% boxes/note %}}
This section is a work in progress.
{{% /boxes/note %}}

This specification outlines several standard event types, all of which
are prefixed with `m.`

{{% event event="m.room.canonical_alias" %}}

{{% event event="m.room.create" %}}

{{% event event="m.room.join_rules" %}}

{{% event event="m.room.member" %}}

{{% event event="m.room.power_levels" %}}

#### Historical events

Some events within the `m.` namespace might appear in rooms, however
they serve no significant meaning in this version of the specification.
They are:

-   `m.room.aliases`

Previous versions of the specification have more information on these
events.

### Syncing

To read events, the intended flow of operation is for clients to first
call the [`/sync`](/client-server-api/#get_matrixclientv3sync) API without a `since` parameter. This returns the
most recent message events for each room, as well as the state of the
room at the start of the returned timeline. The response also includes a
`next_batch` field, which should be used as the value of the `since`
parameter in the next call to `/sync`. Finally, the response includes,
for each room, a `prev_batch` field, which can be passed as a `start`
parameter to the [`/rooms/<room_id>/messages`](/client-server-api/#get_matrixclientv3roomsroomidmessages) API to retrieve earlier
messages.

For example, a `/sync` request might return a range of four events
`E2`, `E3`, `E4` and `E5` within a given room, omitting two prior events
`E0` and `E1`. This can be visualised as follows:

```
    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]
               ^                      ^
               |                      |
         prev_batch: '1-2-3'        next_batch: 'a-b-c'
```

Clients then receive new events by "long-polling" the homeserver via the
`/sync` API, passing the value of the `next_batch` field from the
response to the previous call as the `since` parameter. The client
should also pass a `timeout` parameter. The server will then hold open
the HTTP connection for a short period of time waiting for new events,
returning early if an event occurs. Only the `/sync` API (and the
deprecated `/events` API) support long-polling in this way.

Continuing the example above, an incremental sync might report
a single new event `E6`. The response can be visualised as:

```
    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]->[E6]
                                      ^     ^
                                      |     |
                                      |  next_batch: 'x-y-z'
                                    prev_batch: 'a-b-c'
```

Normally, all new events which are visible to the client will appear in
the response to the `/sync` API. However, if a large number of events
arrive between calls to `/sync`, a "limited" timeline is returned,
containing only the most recent message events. A state "delta" is also
returned, summarising any state changes in the omitted part of the
timeline. The client may therefore end up with "gaps" in its knowledge
of the message timeline. The client can fill these gaps using the
[`/rooms/<room_id>/messages`](/client-server-api/#get_matrixclientv3roomsroomidmessages) API.

Continuing our example, suppose we make a third `/sync` request asking for
events since the last sync, by passing the `next_batch` token `x-y-z` as
the `since` parameter. The server knows about four new events, `E7`, `E8`,
`E9` and `E10`, but decides this is too many to report at once. Instead,
the server sends a `limited` response containing `E8`, `E9` and `E10`but
omitting `E7`. This forms a gap, which we can see in the visualisation:

```
                                            | gap |
                                            | <-> |
    [E0]->[E1]->[E2]->[E3]->[E4]->[E5]->[E6]->[E7]->[E8]->[E9]->[E10]
                                            ^     ^                  ^
                                            |     |                  |
                                 since: 'x-y-z'   |                  |
                                       prev_batch: 'd-e-f'       next_batch: 'u-v-w'
```

The limited response includes a state delta which describes how the state
of the room changes over the gap. This delta explains how to build the state
prior to returned timeline (i.e. at `E7`) from the state the client knows
(i.e. at `E6`). To close the gap, the client should make a request to
[`/rooms/<room_id>/messages`](/client-server-api/#get_matrixclientv3roomsroomidmessages)
with the query parameters `from=x-y-z` and `to=d-e-f`.

{{% boxes/warning %}}
Events are ordered in this API according to the arrival time of the
event on the homeserver. This can conflict with other APIs which order
events based on their partial ordering in the event graph. This can
result in duplicate events being received (once per distinct API
called). Clients SHOULD de-duplicate events based on the event ID when
this happens.
{{% /boxes/warning %}}

{{% boxes/note %}}
The `/sync` API returns a `state` list which is separate from the
`timeline`. This `state` list allows clients to keep their model of the
room state in sync with that on the server. In the case of an initial
(`since`-less) sync, the `state` list represents the complete state of
the room at the **start** of the returned timeline (so in the case of a
recently-created room whose state fits entirely in the `timeline`, the
`state` list will be empty).

In the case of an incremental sync, the `state` list gives a delta
between the state of the room at the `since` parameter and that at the
start of the returned `timeline`. (It will therefore be empty unless the
timeline was `limited`.)

In both cases, it should be noted that the events returned in the
`state` list did **not** necessarily take place just before the returned
`timeline`, so clients should not display them to the user in the
timeline.
{{% /boxes/note %}}

{{% boxes/rationale %}}
An early design of this specification made the `state` list represent
the room state at the end of the returned timeline, instead of the
start. This was unsatisfactory because it led to duplication of events
between the `state` list and the `timeline`, but more importantly, it
made it difficult for clients to show the timeline correctly.

In particular, consider a returned timeline \[M0, S1, M2\], where M0 and
M2 are both messages sent by the same user, and S1 is a state event
where that user changes their displayname. If the `state` list
represents the room state at the end of the timeline, the client must
take a copy of the state dictionary, and *rewind* S1, in order to
correctly calculate the display name for M0.
{{% /boxes/rationale %}}

{{% http-api spec="client-server" api="sync" %}}

{{% http-api spec="client-server" api="old_sync" %}}

### Getting events for a room

There are several APIs provided to `GET` events for a room:

{{% http-api spec="client-server" api="rooms" %}}

{{% http-api spec="client-server" api="message_pagination" %}}

{{% http-api spec="client-server" api="room_event_by_timestamp" %}}

{{% http-api spec="client-server" api="room_initial_sync" %}}

### Sending events to a room

{{% boxes/note %}}
{{% added-in v="1.3" %}}

Servers might need to post-process some events if they
[relate to](#forming-relationships-between-events) another event. The event's
relationship type (`rel_type`) determines any restrictions which might apply,
such as the user only being able to send one event of a given type in relation
to another.
{{% /boxes/note %}}

{{% http-api spec="client-server" api="room_state" %}}

**Examples**

Valid requests look like:

```
PUT /rooms/!roomid:domain/state/m.example.event
{ "key" : "without a state key" }
```
```
PUT /rooms/!roomid:domain/state/m.another.example.event/foo
{ "key" : "with 'foo' as the state key" }
```

In contrast, these requests are invalid:

```
POST /rooms/!roomid:domain/state/m.example.event/
{ "key" : "cannot use POST here" }
```
```
PUT /rooms/!roomid:domain/state/m.another.example.event/foo/11
{ "key" : "txnIds are not supported" }
```

Care should be taken to avoid setting the wrong `state key`:

```
PUT /rooms/!roomid:domain/state/m.another.example.event/11
{ "key" : "with '11' as the state key, but was probably intended to be a txnId" }
```

The `state_key` is often used to store state about individual users, by
using the user ID as the `state_key` value. For example:

```
PUT /rooms/!roomid:domain/state/m.favorite.animal.event/%40my_user%3Aexample.org
{ "animal" : "cat", "reason": "fluffy" }
```

In some cases, there may be no need for a `state_key`, so it can be
omitted:

```
PUT /rooms/!roomid:domain/state/m.room.bgd.color
{ "color": "red", "hex": "#ff0000" }
```

{{% http-api spec="client-server" api="room_send" %}}

### Redactions

Since events are extensible it is possible for malicious users and/or
servers to add keys that are, for example offensive or illegal. Since
some events cannot be simply deleted, e.g. membership events, we instead
'redact' events. This involves removing all keys from an event that are
not required by the protocol. This stripped down event is thereafter
returned anytime a client or remote server requests it. Redacting an
event cannot be undone, allowing server owners to delete the offending
content from the databases. Servers should include a copy of the
`m.room.redaction` event under `unsigned` as `redacted_because`
when serving the redacted event to clients.

The exact algorithm to apply against an event is defined in the [room
version specification](/rooms), as are the criteria homeservers should
use when deciding whether to accept a redaction event from a remote
homeserver.

When a client receives an `m.room.redaction` event, it should change
the affected event in the same way a server does.

{{% boxes/note %}}
Redacted events can still affect the state of the room. When redacted,
state events behave as though their properties were simply not
specified, except those protected by the redaction algorithm. For
example, a redacted `join` event will still result in the user being
considered joined. Similarly, a redacted topic does not necessarily
cause the topic to revert to what it was prior to the event - it causes
the topic to be removed from the room.
{{% /boxes/note %}}

#### Events

{{% event event="m.room.redaction" %}}

#### Client behaviour

{{% http-api spec="client-server" api="redaction" %}}

### Forming relationships between events

{{% changed-in v="1.3" %}}

In some cases it is desirable to logically associate one event's contents with
another event's contents — for example, when replying to a message, editing an
event, or simply looking to add context for an event's purpose.

Events are related to each other in a parent/child structure, where any event can
become a parent by simply having a child event point at it. Parent events do not
define their children, instead relying on the children to describe their parent.

The relationship between a child and its parent event is described in the child
event's `content` as `m.relates_to` (defined below). A child event can point at
any other event, including another child event, to build the relationship so long
as both events are in the same room, however additional restrictions might be imposed
by the type of the relationship (the `rel_type`).

{{% boxes/note %}}
Child events can point at other child events, forming a chain of events. These chains
can naturally take the shape of a tree if two independent children point at a single
parent event, for example.
{{% /boxes/note %}}

To allow the server to aggregate and find child events for a parent, the `m.relates_to`
key of an event MUST be included in the cleartext portion of the event. It cannot be
exclusively recorded in the encrypted payload as the server cannot decrypt the event
for processing.

{{% boxes/warning %}}
If an encrypted event contains an `m.relates_to` in its payload, it should be
ignored and instead favour the cleartext `m.relates_to` copy (including when there
is no cleartext copy). This is to ensure the client's behaviour matches the server's
capability to handle relationships.
{{% /boxes/warning %}}

Relationships which don't match the schema, or which break the rules of a relationship,
are simply ignored. An example might be the parent and child being in different
rooms, or the relationship missing properties required by the schema below. Clients
handling such invalid relationships should show the events independently of each
other, optionally with an error message.

`m.relates_to` is defined as follows:

{{% definition path="api/client-server/definitions/m.relates_to" %}}

#### Relationship types

This specification describes the following relationship types:

* [Rich replies](#rich-replies) (**Note**: does not use `rel_type`).
* [Event replacements](#event-replacements).
* [Event annotations](#event-annotations-and-reactions).
* [Threads](#threading).
* [References](#reference-relations)

#### Aggregations of child events

{{% added-in v="1.3" %}}

Some child events can be "aggregated" by the server, depending on their
`rel_type`. This can allow a set of child events to be summarised to the client without
the client needing the child events themselves.

An example of this might be that a `rel_type` requires an extra `key` field which, when
appropriately specified, would mean that the client receives a total count for the number
of times that `key` was used by child events.

The actual aggregation format depends on the `rel_type`.

When an event is served to the client through the APIs listed below, a
`m.relations` property is included under `unsigned` if the event has child
events which can be aggregated and point at it. The `m.relations` property is
an object keyed by `rel_type` and value being the type-specific aggregated
format for that `rel_type`. This `m.relations` property is known as a "bundled
aggregation".

For example (unimportant fields not included):

```json
{
  "event_id": "$my_event",
  "unsigned": {
    "m.relations": {
      "org.example.possible_annotations": [
        {
          "key": "👍",
          "origin_server_ts": 1562763768320,
          "count": 3
        },
        {
          "key": "👎",
          "origin_server_ts": 1562763768320,
          "count": 1
        }
      ],
      "org.example.possible_thread": {
        "current_server_participated": true,
        "count": 7,
        "latest_event": {
          "event_id": "$another_event",
          "content": {
            "body": "Hello world"
          }
        }
      }
    }
  }
}
```

Note how the `org.example.possible_annotations` aggregation is an array, while in the
`org.example.possible_thread` aggregation where the server is summarising the state of
the relationship in a single object. Both are valid ways to aggregate: the format of an
aggregation depends on the `rel_type`.

{{% boxes/warning %}}
State events do not currently receive bundled aggregations. This is not
necessarily a deliberate design decision, and MSCs which aim to fix this are welcome.
{{% /boxes/warning %}}

The endpoints where the server *should* include bundled aggregations are:

* [`GET /rooms/{roomId}/messages`](#get_matrixclientv3roomsroomidmessages)
* [`GET /rooms/{roomId}/context/{eventId}`](#get_matrixclientv3roomsroomidcontexteventid)
* [`GET /rooms/{roomId}/event/{eventId}`](#get_matrixclientv3roomsroomideventeventid)
* [`GET /rooms/{roomId}/relations/{eventId}`](#get_matrixclientv1roomsroomidrelationseventid)
* [`GET /rooms/{roomId}/relations/{eventId}/{relType}`](#get_matrixclientv1roomsroomidrelationseventidreltype)
* [`GET /rooms/{roomId}/relations/{eventId}/{relType}/{eventType}`](#get_matrixclientv1roomsroomidrelationseventidreltypeeventtype)
* [`GET /sync`](#get_matrixclientv3sync) when the relevant section has a `limited` value
  of `true`.
* [`POST /search`](#post_matrixclientv3search) for any matching events under `room_events`.
* {{< added-in v="1.4" >}} [`GET /rooms/{roomId}/threads`](#get_matrixclientv1roomsroomidthreads)

{{% boxes/note %}}
The server is **not** required to return bundled aggregations on deprecated endpoints
such as `/initialSync`.
{{% /boxes/note %}}

While this functionality allows the client to see what was known to the server at the
time of handling, the client should continue to aggregate locally if it is aware of
the relationship type's behaviour. For example, a client might internally increment a `count`
in a parent event's aggregation data if it saw a new child event which referenced that parent.

The aggregation provided by the server only includes child events which were known at the
time the client would receive the aggregation. For example, in a single `/sync` response
with the parent and multiple child events the child events would have already been
included on the parent's `m.relations` field. Events received in future syncs would
need to be aggregated manually by the client.

{{% boxes/note %}}
Events from [ignored users](#ignoring-users) do not appear in the aggregation
from the server, however clients might still have events from ignored users cached. Like
with normal events, clients will need to de-aggregate child events sent by ignored users to
avoid them being considered in counts. Servers must additionally ensure they do not
consider child events from ignored users when preparing an aggregation for the client.
{{% /boxes/note %}}

When a parent event is redacted, the child events which pointed to that parent remain, however
when a child event is redacted then the relationship is broken. Therefore, the server needs
to de-aggregate or disassociate the event once the relationship is lost. Clients with local
aggregation or which handle redactions locally should do the same.

It is suggested that clients perform local echo on aggregations — for instance, aggregating
a new child event into a parent event optimistically until the server returns a failure or the client
gives up on sending the event, at which point the event should be de-aggregated and an
error or similar shown. The client should be cautious to not aggregate an event twice if
it has already optimistically aggregated the event. Clients are encouraged to take this
a step further to additionally track child events which target unsent/pending events,
likely using the transaction ID as a temporary event ID until a proper event ID is known.

{{% boxes/warning %}}
Due to history visibility restrictions, child events might not be visible to the user
if they are in a section of history the user cannot see. This means any aggregations which would
normally include those events will be lacking them and the client will not be able to
locally aggregate the events either — relating events of importance (such as votes) should
take into consideration history visibility.

Additionally, if the server is missing portions of the room history then it may not be
able to accurately aggregate the events.
{{% /boxes/warning %}}

#### Relationships API

{{% added-in v="1.3" %}}

To retrieve the child events for a parent from the server, the client can call the
following endpoint.

This endpoint is particularly useful if the client has lost context on the aggregation for
a parent event and needs to rebuild/verify it.

When using the `recurse` parameter, note that there is no way for a client to
control how far the server recurses. If the client decides that the server's
recursion level is insufficient, it could, for example, perform the recursion
itself, or disable whatever feature requires more recursion.

Filters specified via `event_type` or `rel_type` will be applied to all events
returned, whether direct or indirect relations. Events that would match the filter,
but whose only relation to the original given event is through a non-matching
intermediate event, will not be included. This means that supplying a `rel_type`
parameter of `m.thread` is not appropriate for fetching all events in a thread since
relations to the threaded events would be filtered out. For this purpose, clients should
omit the `rel_type` parameter and perform any necessary filtering on the client side.

{{% boxes/note %}}
Because replies do not use `rel_type`, they will not be accessible via this API.
{{% /boxes/note %}}

{{% http-api spec="client-server" api="relations" %}}

## Rooms

### Types

{{% added-in v="1.2" %}}

Optionally, rooms can have types to denote their intended function. A room
without a type does not necessarily mean it has a specific default function,
though commonly these rooms will be for conversational purposes.

Room types are best applied when a client might need to differentiate between
two different rooms, such as conversation-holding and data-holding. If a room
has a type, it is specified in the `type` key of an [`m.room.create`](#mroomcreate)
event. To specify a room's type, provide it as part of `creation_content` on
the create room request.

In this specification the following room types are specified:

* [`m.space`](#spaces)

Unspecified room types are permitted through the use of
[Namespaced Identifiers](/appendices/#common-namespaced-identifier-grammar).

### Creation

The homeserver will create an `m.room.create` event when a room is
created, which serves as the root of the event graph for this room. This
event also has a `creator` key which contains the user ID of the room
creator. It will also generate several other events in order to manage
permissions in this room. This includes:

-   `m.room.power_levels` : Sets the power levels of users and required power
    levels for various actions within the room such as sending events.

-   `m.room.join_rules` : Whether the room is "invite-only" or not.

See [Room Events](#room-events) for more information on these events. To
create a room, a client has to use the following API.

{{% http-api spec="client-server" api="create_room" %}}

### Room aliases

Servers may host aliases for rooms with human-friendly names. Aliases
take the form `#friendlyname:server.name`.

As room aliases are scoped to a particular homeserver domain name, it is
likely that a homeserver will reject attempts to maintain aliases on
other domain names. This specification does not provide a way for
homeservers to send update requests to other servers. However,
homeservers MUST handle `GET` requests to resolve aliases on other
servers; they should do this using the federation API if necessary.

Rooms do not store a list of all aliases present on a room, though
members of the room with relevant permissions may publish preferred
aliases through the `m.room.canonical_alias` state event. The aliases in
the state event should point to the room ID they are published within,
however room aliases can and do drift to other room IDs over time.
Clients SHOULD NOT treat the aliases as accurate. They SHOULD be checked
before they are used or shared with another user. If a room appears to
have a room alias of `#alias:example.com`, this SHOULD be checked to
make sure that the room's ID matches the `room_id` returned from the
request.

{{% http-api spec="client-server" api="directory" %}}

### Permissions

{{% boxes/note %}}
This section is a work in progress.
{{% /boxes/note %}}

Permissions for rooms are done via the concept of power levels - to do
any action in a room a user must have a suitable power level. Power
levels are stored as state events in a given room. The power levels
required for operations and the power levels for users are defined in
`m.room.power_levels`, where both a default and specific users' power
levels can be set. By default all users have a power level of 0, other
than the room creator whose power level defaults to 100. Users can grant
other users increased power levels up to their own power level. For
example, user A with a power level of 50 could increase the power level
of user B to a maximum of level 50. Power levels for users are tracked
per-room even if the user is not present in the room. The keys contained
in `m.room.power_levels` determine the levels required for certain
operations such as kicking, banning and sending state events. See
[m.room.power\_levels](#room-events) for more information.

Clients may wish to assign names to particular power levels. A suggested
mapping is as follows: - 0 User - 50 Moderator - 100 Admin

### 房間成員資格

用戶必須是房間的成員才能在該房間中發送和接收事件。用戶與房間的關係可以有以下幾種狀態：

-   無關（用戶不能在房間中發送或接收事件）
-   敲門（用戶請求參加房間，但尚未被允許）
-   邀請（用戶被邀請參加房間，但尚未參加）
-   加入（用戶可以在房間中發送和接收事件）
-   禁止（用戶不允許加入房間）

有一些例外情況允許未加入房間的成員在房間中發送事件：

- 希望拒絕邀請的用戶會發送 `m.room.member` 事件，`content.membership` 為 `leave`。他們必須先被邀請。

- 如果房間允許，用戶可以發送 `m.room.member` 事件，`content.membership` 為 `knock`，向房間敲門。這是用戶請求邀請的方式。

- 撤回之前的敲門請求，用戶會發送與拒絕邀請類似的 `leave` 事件。

有些房間要求用戶被邀請才能加入；其他房間則允許任何人加入。房間是否為“邀請制”房間由房間配置鍵 `m.room.join_rules` 決定。它可以有以下幾種值：

`public`
任何人都可以自由加入此房間，無需邀請。

`invite`
只有被邀請的人才能加入此房間。

`knock`
只有被邀請的人才能加入此房間，並允許任何人請求邀請加入。請注意，此加入規則僅在支持敲門功能的房間版本中可用。

{{% added-in v="1.2" %}} `restricted`
如果你被邀請或你是加入規則中列出的另一個房間的成員，你可以加入此房間。如果服務器無法驗證任何列出房間的成員資格，那麼你只能通過邀請加入。請注意，此規則預計僅在支持此功能的房間版本中有效。

The allowable state transitions of membership are:

![membership-flow-diagram](/diagrams/membership.png)

{{% http-api spec="client-server" api="list_joined_rooms" %}}

#### Joining rooms

{{% http-api spec="client-server" api="inviting" %}}

{{% http-api spec="client-server" api="joining" %}}

##### Knocking on rooms

{{% added-in v="1.1" %}}
{{% changed-in v="1.3" %}}

{{% boxes/note %}}
As of `v1.3`, it is possible to knock on a [restricted room](#restricted-rooms)
if the room supports and is using the `knock_restricted` join rule.

Note that `knock_restricted` is only expected to work in room versions
[which support it](/rooms/#feature-matrix).
{{% /boxes/note %}}

<!--
This section is here because it's most similar to being invited/joining a
room, though has added complexity which needs to be explained. Otherwise
this will have been just the API definition and nothing more (like invites).
-->

If the join rules allow, external users to the room can `/knock` on it to
request permission to join. Users with appropriate permissions within the
room can then approve (`/invite`) or deny (`/kick`, `/ban`, or otherwise
set membership to `leave`) the knock. Knocks can be retracted by calling
`/leave` or otherwise setting membership to `leave`.

Users who are currently in the room, already invited, or banned cannot
knock on the room.

To accept another user's knock, the user must have permission to invite
users to the room. To reject another user's knock, the user must have
permission to either kick or ban users (whichever is being performed).
Note that setting another user's membership to `leave` is kicking them.

The knocking homeserver should assume that an invite to the room means
that the knock was accepted, even if the invite is not explicitly related
to the knock.

Homeservers are permitted to automatically accept invites as a result of
knocks as they should be aware of the user's intent to join the room. If
the homeserver is not auto-accepting invites (or there was an unrecoverable
problem with accepting it), the invite is expected to be passed down normally
to the client to handle. Clients can expect to see the join event if the
server chose to auto-accept.

{{% http-api spec="client-server" api="knocking" %}}

##### Restricted rooms

{{% added-in v="1.2" %}}
{{% changed-in v="1.3" %}}

{{% boxes/note %}}
As of `v1.3`, it is possible to [knock](#knocking-on-rooms) on a restricted
room if the room supports and is using the `knock_restricted` join rule.

Note that `knock_restricted` is only expected to work in room versions
[which support it](/rooms/#feature-matrix).
{{% /boxes/note %}}

Restricted rooms are rooms with a `join_rule` of `restricted`. These rooms
are accompanied by "allow conditions" as described in the
[`m.room.join_rules`](#mroomjoin_rules) state event.

If the user has an invite to the room then the restrictions will not affect
them. They should be able to join by simply accepting the invite.

When joining without an invite, the server MUST verify that the requesting
user meets at least one of the conditions. If no conditions can be verified
or no conditions are satisfied, the user will not be able to join. When the
join is happening over federation, the remote server will check the conditions
before accepting the join. See the [Server-Server Spec](/server-server-api/#restricted-rooms)
for more information.

If the room is `restricted` but no valid conditions are presented then the
room is effectively invite only.

The user does not need to maintain the conditions in order to stay a member
of the room: the conditions are only checked/evaluated during the join process.

###### Conditions

Currently there is only one condition available: `m.room_membership`. This
condition requires the user trying to join the room to be a *joined* member
of another room (specifically, the `room_id` accompanying the condition). For
example, if `!restricted:example.org` wanted to allow joined members of
`!other:example.org` to join, `!restricted:example.org` would have the following
`content` for [`m.room.join_rules`](#mroomjoin_rules):

```json
{
  "join_rule": "restricted",
  "allow": [
    {
      "room_id": "!other:example.org",
      "type": "m.room_membership"
    }
  ]
}
```

#### Leaving rooms

A user can leave a room to stop receiving events for that room. A user
must have been invited to or have joined the room before they are
eligible to leave the room. Leaving a room to which the user has been
invited rejects the invite, and can retract a knock. Once a user leaves
a room, it will no longer appear in the response to the
[`/sync`](/client-server-api/#get_matrixclientv3sync) API unless it is
explicitly requested via a filter with the `include_leave` field set
to `true`.

Whether or not they actually joined the room, if the room is an
"invite-only" room the user will need to be re-invited before they can
re-join the room.

A user can also forget a room which they have left. Rooms which have
been forgotten will never appear the response to the [`/sync`](/client-server-api/#get_matrixclientv3sync) API,
until the user re-joins, is re-invited, or knocks.

A user may wish to force another user to leave a room. This can be done
by 'kicking' the other user. To do so, the user performing the kick MUST
have the required power level. Once a user has been kicked, the
behaviour is the same as if they had left of their own accord. In
particular, the user is free to re-join if the room is not
"invite-only".

{{% http-api spec="client-server" api="leaving" %}}

{{% http-api spec="client-server" api="kicking" %}}

##### Banning users in a room

A user may decide to ban another user in a room. 'Banning' forces the
target user to leave the room and prevents them from re-joining the
room. A banned user will not be treated as a joined user, and so will
not be able to send or receive events in the room. In order to ban
someone, the user performing the ban MUST have the required power level.
To ban a user, a request should be made to [`/rooms/<room_id>/ban`](/client-server-api/#post_matrixclientv3roomsroomidban)
with:

```json
{
  "user_id": "<user id to ban>",
  "reason": "string: <reason for the ban>"
}
````

Banning a user adjusts the banned member's membership state to `ban`.
Like with other membership changes, a user can directly adjust the
target member's state, by making a request to
`/rooms/<room id>/state/m.room.member/<user id>`:

```json
{
  "membership": "ban"
}
```

A user must be explicitly unbanned with a request to
[`/rooms/<room_id>/unban`](/client-server-api/#post_matrixclientv3roomsroomidunban) before they can re-join the room or be
re-invited.

{{% http-api spec="client-server" api="banning" %}}

### Listing rooms

{{% http-api spec="client-server" api="list_public_rooms" %}}

## User Data

### User Directory

{{% http-api spec="client-server" api="users" %}}

### Profiles

{{% http-api spec="client-server" api="profile" %}}

#### Events on Change of Profile Information

Because the profile display name and avatar information are likely to be
used in many places of a client's display, changes to these fields cause
an automatic propagation event to occur, informing likely-interested
parties of the new values. This change is conveyed using two separate
mechanisms:

-   an `m.room.member` event (with a `join` membership) is sent to every
    room the user is a member of, to update the `displayname` and
    `avatar_url`.
-   an `m.presence` presence status update is sent, again containing the
    new values of the `displayname` and `avatar_url` keys, in addition
    to the required `presence` key containing the current presence state
    of the user.

Both of these should be done automatically by the homeserver when a user
successfully changes their display name or avatar URL fields.

Additionally, when homeservers emit room membership events for their own
users, they should include the display name and avatar URL fields in
these events so that clients already have these details to hand, and do
not have to perform extra round trips to query it.

## Modules

Modules are parts of the Client-Server API which are not universal to
all endpoints. Modules are strictly defined within this specification
and should not be mistaken for experimental extensions or optional
features. A compliant server implementation MUST support all modules and
supporting specification (unless the implementation only targets clients
of certain profiles, in which case only the required modules for those
feature profiles MUST be implemented). A compliant client implementation
MUST support all the required modules and supporting specification for
the [Feature Profile](#feature-profiles) it targets.

### Feature Profiles

Matrix supports many different kinds of clients: from embedded IoT
devices to desktop clients. Not all clients can provide the same feature
sets as other clients e.g. due to lack of physical hardware such as not
having a screen. Clients can fall into one of several profiles and each
profile contains a set of features that the client MUST support. This
section details a set of "feature profiles". Clients are expected to
implement a profile in its entirety in order for it to be classified as
that profile.

#### Summary

| Module / Profile                                           | Web       | Mobile   | Desktop  | CLI      | Embedded |
|------------------------------------------------------------|-----------|----------|----------|----------|----------|
| [Content Repository](#content-repository)                  | Required  | Required | Required | Optional | Optional |
| [Direct Messaging](#direct-messaging)                      | Required  | Required | Required | Required | Optional |
| [Ignoring Users](#ignoring-users)                          | Required  | Required | Required | Optional | Optional |
| [Instant Messaging](#instant-messaging)                    | Required  | Required | Required | Required | Optional |
| [Presence](#presence)                                      | Required  | Required | Required | Required | Optional |
| [Push Notifications](#push-notifications)                  | Optional  | Required | Optional | Optional | Optional |
| [Receipts](#receipts)                                      | Required  | Required | Required | Required | Optional |
| [Room History Visibility](#room-history-visibility)        | Required  | Required | Required | Required | Optional |
| [Room Upgrades](#room-upgrades)                            | Required  | Required | Required | Required | Optional |
| [Third-party Invites](#third-party-invites)                | Optional  | Required | Optional | Optional | Optional |
| [Typing Notifications](#typing-notifications)              | Required  | Required | Required | Required | Optional |
| [User and Room Mentions](#user-and-room-mentions)          | Required  | Required | Required | Optional | Optional |
| [Voice over IP](#voice-over-ip)                            | Required  | Required | Required | Optional | Optional |
| [Client Config](#client-config)                            | Optional  | Optional | Optional | Optional | Optional |
| [Device Management](#device-management)                    | Optional  | Optional | Optional | Optional | Optional |
| [End-to-End Encryption](#end-to-end-encryption)            | Optional  | Optional | Optional | Optional | Optional |
| [Event Annotations and reactions](#event-annotations-and-reactions) | Optional  | Optional | Optional | Optional | Optional |
| [Event Context](#event-context)                            | Optional  | Optional | Optional | Optional | Optional |
| [Event Replacements](#event-replacements)                  | Optional  | Optional | Optional | Optional | Optional |
| [Fully read markers](#fully-read-markers)                  | Optional  | Optional | Optional | Optional | Optional |
| [Guest Access](#guest-access)                              | Optional  | Optional | Optional | Optional | Optional |
| [Moderation Policy Lists](#moderation-policy-lists)        | Optional  | Optional | Optional | Optional | Optional |
| [OpenID](#openid)                                          | Optional  | Optional | Optional | Optional | Optional |
| [Reference Relations](#reference-relations)                | Optional  | Optional | Optional | Optional | Optional |
| [Reporting Content](#reporting-content)                    | Optional  | Optional | Optional | Optional | Optional |
| [Rich replies](#rich-replies)                              | Optional  | Optional | Optional | Optional | Optional |
| [Room Previews](#room-previews)                            | Optional  | Optional | Optional | Optional | Optional |
| [Room Tagging](#room-tagging)                              | Optional  | Optional | Optional | Optional | Optional |
| [SSO Client Login/Authentication](#sso-client-loginauthentication) | Optional  | Optional | Optional | Optional | Optional |
| [Secrets](#secrets)                                        | Optional  | Optional | Optional | Optional | Optional |
| [Send-to-Device Messaging](#send-to-device-messaging)      | Optional  | Optional | Optional | Optional | Optional |
| [Server Access Control Lists (ACLs)](#server-access-control-lists-acls-for-rooms) | Optional  | Optional | Optional | Optional | Optional |
| [Server Administration](#server-administration)            | Optional  | Optional | Optional | Optional | Optional |
| [Server Notices](#server-notices)                          | Optional  | Optional | Optional | Optional | Optional |
| [Server Side Search](#server-side-search)                  | Optional  | Optional | Optional | Optional | Optional |
| [Spaces](#spaces)                                          | Optional  | Optional | Optional | Optional | Optional |
| [Sticker Messages](#sticker-messages)                      | Optional  | Optional | Optional | Optional | Optional |
| [Third-party Networks](#third-party-networks)              | Optional  | Optional | Optional | Optional | Optional |
| [Threading](#threading)                                    | Optional  | Optional | Optional | Optional | Optional |

*Please see each module for more details on what clients need to
implement.*

#### Clients

##### Stand-alone web (`Web`)

This is a web page which heavily uses Matrix for communication.
Single-page web apps would be classified as a stand-alone web client, as
would multi-page web apps which use Matrix on nearly every page.

##### Mobile (`Mobile`)

This is a Matrix client specifically designed for consumption on mobile
devices. This is typically a mobile app but need not be so provided the
feature set can be reached (e.g. if a mobile site could display push
notifications it could be classified as a mobile client).

##### Desktop (`Desktop`)

This is a native GUI application which can run in its own environment
outside a browser.

##### Command Line Interface (`CLI`)

This is a client which is used via a text-based terminal.

##### Embedded (`Embedded`)

This is a client which is embedded into another application or an
embedded device.

###### Application

This is a Matrix client which is embedded in another website, e.g. using
iframes. These embedded clients are typically for a single purpose
related to the website in question, and are not intended to be
fully-fledged communication apps.

###### Device

This is a client which is typically running on an embedded device such
as a kettle, fridge or car. These clients tend to perform a few
operations and run in a resource constrained environment. Like embedded
applications, they are not intended to be fully-fledged communication
systems.

{{% cs-module name="instant_messaging" %}}
{{% cs-module name="rich_replies" %}}
{{% cs-module name="voip_events" %}}
{{% cs-module name="typing_notifications" %}}
{{% cs-module name="receipts" %}}
{{% cs-module name="read_markers" %}}
{{% cs-module name="presence" %}}
{{% cs-module name="content_repo" %}}
{{% cs-module name="send_to_device" %}}
{{% cs-module name="device_management" %}}
{{% cs-module name="end_to_end_encryption" %}}
{{% cs-module name="secrets" %}}
{{% cs-module name="history_visibility" %}}
{{% cs-module name="push" %}}
{{% cs-module name="third_party_invites" %}}
{{% cs-module name="search" %}}
{{% cs-module name="guest_access" %}}
{{% cs-module name="room_previews" %}}
{{% cs-module name="tags" %}}
{{% cs-module name="account_data" %}}
{{% cs-module name="admin" %}}
{{% cs-module name="event_context" %}}
{{% cs-module name="sso_login" %}}
{{% cs-module name="dm" %}}
{{% cs-module name="ignore_users" %}}
{{% cs-module name="stickers" %}}
{{% cs-module name="report_content" %}}
{{% cs-module name="third_party_networks" %}}
{{% cs-module name="openid" %}}
{{% cs-module name="server_acls" %}}
{{% cs-module name="mentions" %}}
{{% cs-module name="room_upgrades" %}}
{{% cs-module name="server_notices" %}}
{{% cs-module name="moderation_policies" %}}
{{% cs-module name="spaces" %}}
{{% cs-module name="event_replacements" %}}
{{% cs-module name="event_annotations" %}}
{{% cs-module name="threading" %}}
{{% cs-module name="reference_relations" %}}


# 2. Server discovery

- [2. Server discovery](#2-server-discovery)
	- [2.1 Resolving server names](#21-resolving-server-names)
	- [2.2 Server implementation](#22-server-implementation)
	- [2.3 Retrieving server keys](#23-retrieving-server-keys)
		- [2.3.1 Publishing Keys](#231-publishing-keys)
		- [2.3.2 Querying Keys Through Another Server](#232-querying-keys-through-another-server)

## 2.1 Resolving server names

每個 Matrix 主伺服器的server-name是由hostname和port來去辨認，
如 [語法](/v1.11/appendices#server-name) 所述。
生效時，
代理伺服器名稱使用相同的語法。

伺服器名稱透過解析成IP位置和port來連接，
並透過各種條件來調整要發送的證書和 `Host` header。
整體過程如下：

1. 如果hostname是IP的話
   - 使用這個IP和port(預設8448)。
   - 伺服器提供該IP有效的證書。
   - `Host` header設定為server-name，包含port(如果有)

2. 如果hostname不是 IP，且有明確的寫port
   - 使用 CNAME、AAAA 或 A 記錄解析hostname為 IP 地址。
   - 請求將發送到解析出的 IP 地址和給定的端口，
   - 伺服器提供該hostname的證書
   - `Host` header返回server-name(包含port)

3. 如果hostname不是 IP，
   - 對 `https://<hostname>/.well-known/matrix/server` 發送常規的 HTTPS 請求，期待該節中定義的架構。
   - 應遵循 30x 重新定向，但應避免重新定向循環。
   - 對 `/.well-known` 端點的回應（成功或其他）請求伺服器應該對其進行緩存。
     - 請求伺服器應尊重目標伺服器回應中的緩存控制標頭(cache control headers)來指示，或在沒有標頭時使用合理的默認值(24小時)。
     - 伺服器應該設定回應的最大緩存時間，建議 48 小時。
     - 錯誤回應建議緩存最多一小時，，並鼓勵伺服器對重複的失敗進行指數回退(每一次錯誤以指數增加緩存的時間，減少發出請求的頻率)。
   - `/.well-known` 請求的架構在本節後面。
   - 如果回應無效（錯誤的 JSON、缺少屬性、非 200 回應等），則跳到第 4 步。
   - 如果回應有效，則解析 `m.server` 屬性為 `<delegated_hostname>[:<delegated_port>]`，並按以下步驟處理：
     1. 如果 `<delegated_hostname>` 是 IP 字面量，
   則應使用該 IP 地址和 `<delegated_port>`，
   如果未提供端口則使用 8448。
   目標伺服器必須提供該 IP 地址的有效 TLS 證書。
   請求必須包含 IP 地址的 `Host` 標頭，
   包括端口（如果提供）。

     2. 如果 `<delegated_hostname>` 不是 IP 字面量，
   並且提供 `<delegated_port>`，
   則通過查找 `<delegated_hostname>` 的 CNAME、AAAA 或 A 記錄來發現 IP 地址。
   使用解析出的 IP 地址和 `<delegated_port>`。
   請求必須包含 `<delegated_hostname>:<delegated_port>` 的 `Host` 標頭。
   目標伺服器必須提供 `<delegated_hostname>` 的有效證書。
   **[v1.8 添加]** 如果 `<delegated_hostname>` 不是 IP 字面量，
   並且未提供 `<delegated_port>`，
   則查找 `_matrix-fed._tcp.<delegated_hostname>` 的 SRV 記錄。
   這可能會導致另一個主機名（使用 AAAA 或 A 記錄解析）和端口。
   請求應發送到解析出的 IP 地址和端口，
   `Host` 標頭包含 `<delegated_hostname>`。
   目標伺服器必須提供 `<delegated_hostname>` 的有效證書。

     3. **[已棄用]** 如果 `<delegated_hostname>` 不是 IP 字面量，
   未提供 `<delegated_port>`，
   並且未找到 `_matrix-fed._tcp.<delegated_hostname>` 的 SRV 記錄，
   則查找 `_matrix._tcp.<delegated_hostname>` 的 SRV 記錄。
   這可能會導致另一個主機名（使用 AAAA 或 A 記錄解析）和端口。
   請求應發送到解析出的 IP 地址和端口，
   `Host` 標頭包含 `<delegated_hostname>`。
   目標伺服器必須提供 `<delegated_hostname>` 的有效證書。

     4. 如果未找到 SRV 記錄，
  則使用 CNAME、AAAA 或 A 記錄解析 IP 地址。
  然後使用解析出的 IP 地址和 8448 端口發送請求，
  `Host` 標頭包含 `<delegated_hostname>`。
  目標伺服器必須提供 `<delegated_hostname>` 的有效證書。

1. **[v1.8 添加]** 如果 `/.well-known` 請求導致錯誤回應，
則通過解析 `_matrix-fed._tcp.<hostname>` 的 SRV 記錄找到伺服器。
這可能會導致主機名（使用 AAAA 或 A 記錄解析）和端口。
請求發送到解析出的 IP 地址和端口，
`Host` 標頭包含 `<hostname>`。
目標伺服器必須提供 `<hostname>` 的有效證書。

1. **[已棄用]** 如果 `/.well-known` 請求導致錯誤回應，
並且未找到 `_matrix-fed._tcp.<hostname>` 的 SRV 記錄，
則通過解析 `_matrix._tcp.<hostname>` 的 SRV 記錄找到伺服器。
這可能會導致主機名（使用 AAAA 或 A 記錄解析）和端口。
請求發送到解析出的 IP 地址和端口，
`Host` 標頭包含 `<hostname>`。
目標伺服器必須提供 `<hostname>` 的有效證書。

1. 如果 `/.well-known` 請求返回錯誤回應，
並且未找到 SRV 記錄，
則使用 CNAME、AAAA 和 A 記錄解析 IP 地址。
請求發送到解析出的 IP 地址，
使用 8448 端口和 `Host` 標頭包含 `<hostname>`。
目標伺服器必須提供 `<hostname>` 的有效證書。

> **info:**
>
> 我們要求 `<hostname>` 而不是 `<delegated_hostname>` 用於 SRV 委派的原因是：
>
> 1. DNS 是不安全的（並非所有域名都有 DNSSEC），
> 因此委派的目標必須通過 TLS 證明它是 `<hostname>` 的有效委派。
>
> 2. 與 [RFC6125](https://datatracker.ietf.org/doc/html/rfc6125#section-6.2.1) 中的建議及使用 SRV 記錄的其他應用程序（如 [XMPP](https://datatracker.ietf.org/doc/html/rfc6120#section-13.7.2.1)）保持一致。
>
> ---
> **info:**
>
> 注意，
> SRV 記錄的目標不能是 CNAME，
> 如 [RFC2782](https://www.rfc-editor.org/rfc/rfc2782.html) 所規定：
> > 名稱不能是別名（按 RFC 1034 或 RFC 2181 的定義）
> ---
> **info:**
>
> 步驟 3.4 和 5 已被棄用，
因為它們使用了 IANA 未註冊的服務名稱。
它們可能會在未來的規範版本中被移除。
伺服器管理員被鼓勵使用 `.well-known` 而不是任何形式的 SRV 記錄。
>
> IANA 對 8448 端口和 `matrix-fed` 的註冊可在[這裡](https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml?search=matrix-fed)找到。

<!-- markdownlint-disable -->
<h1>GET <a>/.well-known/matrix/server</a></h1> 
<!-- markdownlint-enable -->

獲取用於 Matrix 主伺服器之間通訊的委派伺服器的信息。
伺服器應遵循 30x 重新定向，
仔細避免重新定向循環，
並使用正常的 X.509 證書驗證。

| 速率限制： | 否 |
| --- | --- |
| 需要認證： | 否 |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

無請求參數或請求主體。

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 委派伺服器信息。
 該回應的 `Content-Type`應為 `application/json`，

但解析回應的伺服器應假設主體是 JSON，

無論類型為何。
解析 JSON 失敗或提供的數據無效不應導致發現失敗 - 請參考伺服器發現過程以了解如何繼續。
 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 Responses</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `m.server` | `string` | 用於委派伺服器-伺服器通訊的伺服器名稱，
帶有可選端口。
委派伺服器名稱使用與[附錄中的伺服器名稱](/v1.11/appendices/#server-name)相同的語法。
 |
<!-- markdownlint-enable -->

```json
{
  "m.server": "delegated.example.com:1234"
}
```

---
整理

1. **伺服器名稱**
   - 每個 Matrix 主伺服器由主機名和可選的端口組成的伺服器名稱標識。可應用時，委派的伺服器名稱使用相同的語法。
   
2. **名稱解析流程**
   - **IP 字面量**：使用該 IP 地址和給定的端口號（默認 8448）。目標伺服器必須提供有效的 IP 地址證書，`Host` 標頭設置為伺服器名稱。
   - **非 IP 字面量且包含端口**：使用 CNAME、AAAA 或 A 記錄解析主機名。請求發送到解析出的 IP 地址和端口，`Host` 標頭使用原始伺服器名稱（帶端口）。
   - **非 IP 字面量且不包含端口**：發送 HTTPS 請求到 `https://<hostname>/.well-known/matrix/server`，遵循 30x 重定向，並緩存回應。有效回應解析 `m.server` 屬性並進一步處理。
   
3. **處理委派伺服器**
   - **IP 字面量**：使用 IP 地址和 `<delegated_port>`（默認 8448）。目標伺服器提供有效的 IP 地址證書，請求必須包含 IP 地址的 `Host` 標頭。
   - **非 IP 字面量且包含端口**：查找 `<delegated_hostname>` 的 CNAME、AAAA 或 A 記錄。使用解析出的 IP 地址和 `<delegated_port>`，`Host` 標頭設置為 `<delegated_hostname>:<delegated_port>`。
   - **非 IP 字面量且不包含端口**：查找 `_matrix-fed._tcp.<delegated_hostname>` 的 SRV 記錄。請求發送到解析出的 IP 地址和端口，`Host` 標頭設置為 `<delegated_hostname>`。
   - **已棄用步驟**：查找 `_matrix._tcp.<delegated_hostname>` 的 SRV 記錄，請求發送到解析出的 IP 地址和端口，`Host` 標頭設置為 `<delegated_hostname>`。
   - **無 SRV 記錄**：使用 CNAME、AAAA 或 A 記錄解析 IP 地址，請求發送到解析出的 IP 地址和 8448 端口，`Host` 標頭設置為 `<delegated_hostname>`。

4. **處理錯誤回應**
   - 查找 `_matrix-fed._tcp.<hostname>` 的 SRV 記錄，請求發送到解析出的 IP 地址和端口，`Host` 標頭設置為 `<hostname>`。
   - **已棄用步驟**：查找 `_matrix._tcp.<hostname>` 的 SRV 記錄，請求發送到解析出的 IP 地址和端口，`Host` 標頭設置為 `<hostname>`。
   - **無 SRV 記錄**：使用 CNAME、AAAA 和 A 記錄解析 IP 地址，請求發送到解析出的 IP 地址和 8448 端口，`Host` 標頭設置為 `<hostname>`。

5. **附加資訊**
   - 使用 `<hostname>` 而不是 `<delegated_hostname>` 作為 SRV 委派的原因：
     - DNS 不安全，需要通過 TLS 驗證。
     - 與 RFC6125 和其他使用 SRV 記錄的應用（如 XMPP）保持一致。
   - SRV 記錄的目標不能是 CNAME。
   - 步驟 3.4 和 5 已被棄用，因為使用了未註冊的服務名稱。未來版本可能移除，伺服器管理員被鼓勵使用 `.well-known`。

這樣的整理可以幫助快速了解伺服器名稱解析和處理流程的重點內容。

---

## 2.2 Server implementation

<!-- markdownlint-disable -->
<h1>GET <a>/\_matrix/federation/v1/version</a></h1> 
<!-- markdownlint-enable -->

---

Get the implementation name and version of this homeserver.

| Rate-limited: | No |
| --- | --- |
| Requires authentication: | No |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

No request parameters or request body.

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| Status | Description |
| --- | --- |
| `200` | The implementation name and version of this homeserver. |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| Name | Type | Description |
| --- | --- | --- |
| `server` | `[Server](#get_matrixfederationv1version_response-200_server)` |  |

Server
| Name | Type | Description |
| --- | --- | --- |
| `name` | `string` | Arbitrary name that identify this implementation. |
| `version` | `string` | Version of this implementation. The version format depends on the implementation. |

```json

{
  "server": {
    "name": "My_Homeserver_Implementation",
    "version": "ArbitraryVersionNumber"
  }
}

```

## 2.3 Retrieving server keys

 There was once a “version 1” of the key exchange. It has been removed
 from the specification due to lack of significance. It may be reviewed
 [from
 the historical
 draft](https://github.com/matrix-org/matrix-doc/blob/51faf8ed2e4a63d4cfd6d23183698ed169956cc0/specification/server_server_api.rst#232version-1).

Each homeserver publishes its public keys under
 `/_matrix/key/v2/server`. Homeservers query for keys by either
 getting `/_matrix/key/v2/server` directly or by querying an
 intermediate notary server using a
 `/_matrix/key/v2/query/{serverName}` API. Intermediate notary
 servers query the `/_matrix/key/v2/server` API on behalf of
 another server and sign the response with their own key. A server may
 query multiple notary servers to ensure that they all report the same
 public keys.

This approach is borrowed from the [Perspectives
 Project](https://web.archive.org/web/20170702024706/https://perspectives-project.org/),
 but modified to include the NACL keys and to use JSON instead of XML. It
 has the advantage of avoiding a single trust-root since each server is
 free to pick which notary servers they trust and can corroborate the
 keys returned by a given notary server by querying other servers.

### 2.3.1 Publishing Keys

Homeservers publish their signing keys in a JSON object at
 `/_matrix/key/v2/server`. The response contains a list of
 `verify_keys` that are valid for signing federation requests made by the
 homeserver and for signing events. It contains a list of
 `old_verify_keys` which are only valid for signing events.

<!-- markdownlint-disable -->
<h1>GET</h1> 
<!-- markdownlint-enable -->
/\_matrix/key/v2/server

---

Gets the homeserver’s published signing keys.
 The homeserver may have any number of active keys and may have a
 number of old keys.

Intermediate notary servers should cache a response for half of its
 lifetime to avoid serving a stale response. Originating servers should
 avoid returning responses that expire in less than an hour to avoid
 repeated requests for a certificate that is about to expire. Requesting
 servers should limit how frequently they query for certificates to
 avoid flooding a server with requests.

If the server fails to respond to this request, intermediate notary
 servers should continue to return the last response they received
 from the server so that the signatures of old events can still be
 checked.

| Rate-limited: | No |
| --- | --- |
| Requires authentication: | No |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

No request parameters or request body.

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| Status | Description |
| --- | --- |
| `200` | The homeserver’s keys |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

Server Keys
| Name | Type | Description |
| --- | --- | --- |
| `old_verify_keys` | `{string: [Old Verify Key](#get_matrixkeyv2server_response-200_old-verify-key)}` | The public keys that the server used to use and when it stopped using them. The object’s key is the algorithm and version combined (`ed25519` being the  algorithm and `0ldK3y` being the version in the example below). Together,  this forms the Key ID. The version must have characters matching the regular  expression `[a-zA-Z0-9_]`. |
| `server_name` | `string` | **Required:** DNS name of the homeserver. |
| `signatures` | `{string: {string: string}}` | Digital signatures for this object signed using the `verify_keys`. The signature is calculated using the process described at [Signing JSON](/v1.11/appendices/#signing-json). |
| `valid_until_ts` | `integer` | POSIX timestamp in milliseconds when the list of valid keys should be refreshed.  This field MUST be ignored in room versions 1, 2, 3, and 4. Keys used beyond this  timestamp MUST be considered invalid, depending on the  [room version specification](/v1.11/rooms).   Servers MUST use the lesser of this field and 7 days into the future when  determining if a key is valid. This is to avoid a situation where an attacker  publishes a key which is valid for a significant amount of time without a way  for the homeserver owner to revoke it. |
| `verify_keys` | `{string: [Verify Key](#get_matrixkeyv2server_response-200_verify-key)}` | **Required:**  Public keys of the homeserver for verifying digital signatures. The object’s key is the algorithm and version combined (`ed25519` being the  algorithm and `abc123` being the version in the example below). Together,  this forms the Key ID. The version must have characters matching the regular  expression `[a-zA-Z0-9_]`. |

Old Verify Key
| Name | Type | Description |
| --- | --- | --- |
| `expired_ts` | `integer` | **Required:** POSIX timestamp in milliseconds for when this key expired. |
| `key` | `string` | **Required:** The [Unpadded  base64](/v1.11/appendices/#unpadded-base64) encoded key. |

Verify Key
| Name | Type | Description |
| --- | --- | --- |
| `key` | `string` | **Required:** The [Unpadded  base64](/v1.11/appendices/#unpadded-base64) encoded key. |

```
{
  "old_verify_keys": {
    "ed25519:0ldk3y": {
      "expired_ts": 1532645052628,
      "key": "VGhpcyBzaG91bGQgYmUgeW91ciBvbGQga2V5J3MgZWQyNTUxOSBwYXlsb2FkLg"
    }
  },
  "server_name": "example.org",
  "signatures": {
    "example.org": {
      "ed25519:auto2": "VGhpcyBzaG91bGQgYWN0dWFsbHkgYmUgYSBzaWduYXR1cmU"
    }
  },
  "valid_until_ts": 1652262000000,
  "verify_keys": {
    "ed25519:abc123": {
      "key": "VGhpcyBzaG91bGQgYmUgYSByZWFsIGVkMjU1MTkgcGF5bG9hZA"
    }
  }
}

```

### 2.3.2 Querying Keys Through Another Server

Servers may query another server’s keys through a notary server. The
 notary server may be another homeserver. The notary server will retrieve
 keys from the queried servers through use of the
 `/_matrix/key/v2/server` API. The notary server will
 additionally sign the response from the queried server before returning
 the results.

Notary servers can return keys for servers that are offline or having
 issues serving their own keys by using cached responses. Keys can be
 queried from multiple servers to mitigate against DNS spoofing.

<!-- markdownlint-disable -->
<h1>POST <a>/\_matrix/key/v2/query</a></h1> 
<!-- markdownlint-enable -->

---

Query for keys from multiple servers in a batch format. The receiving (notary)
 server must sign the keys returned by the queried servers.

| Rate-limited: | No |
| --- | --- |
| Requires authentication: | No |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

#<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable --> body

| Name | Type | Description |
| --- | --- | --- |
| `server_keys` | `{string: {string: [Query Criteria](#post_matrixkeyv2query_request_query-criteria)}}` | **Required:**  The query criteria. The outer `string` key on the object is the  server name (eg: `matrix.org`). The inner `string` key is the  Key ID to query for the particular server. If no key IDs are given  to be queried, the notary server should query for all keys. If no  servers are given, the notary server must return an empty `server_keys`  array in the response. The notary server may return multiple keys regardless of the Key IDs  given. |

Query Criteria
| Name | Type | Description |
| --- | --- | --- |
| `minimum_valid_until_ts` | `integer` | A millisecond POSIX timestamp in milliseconds indicating when  the returned certificates will need to be valid until to be  useful to the requesting server. If not supplied, the current time as determined by the notary  server is used. |

#<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable --> body example

```
{
  "server_keys": {
    "example.org": {
      "ed25519:abc123": {
        "minimum_valid_until_ts": 1234567890
      }
    }
  }
}

```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| Status | Description |
| --- | --- |
| `200` | The keys for the queried servers, signed by the notary server. Servers which  are offline and have no cached keys will not be included in the result. This  may result in an empty array. |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| Name | Type | Description |
| --- | --- | --- |
| `server_keys` | `[[Server Keys](#post_matrixkeyv2query_response-200_server-keys)]` | The queried server’s keys, signed by the notary server. |

Server Keys
| Name | Type | Description |
| --- | --- | --- |
| `old_verify_keys` | `{string: [Old Verify Key](#post_matrixkeyv2query_response-200_old-verify-key)}` | The public keys that the server used to use and when it stopped using them. The object’s key is the algorithm and version combined (`ed25519` being the  algorithm and `0ldK3y` being the version in the example below). Together,  this forms the Key ID. The version must have characters matching the regular  expression `[a-zA-Z0-9_]`. |
| `server_name` | `string` | **Required:** DNS name of the homeserver. |
| `signatures` | `{string: {string: string}}` | Digital signatures for this object signed using the `verify_keys`. The signature is calculated using the process described at [Signing JSON](/v1.11/appendices/#signing-json). |
| `valid_until_ts` | `integer` | POSIX timestamp in milliseconds when the list of valid keys should be refreshed.  This field MUST be ignored in room versions 1, 2, 3, and 4. Keys used beyond this  timestamp MUST be considered invalid, depending on the  [room version specification](/v1.11/rooms).   Servers MUST use the lesser of this field and 7 days into the future when  determining if a key is valid. This is to avoid a situation where an attacker  publishes a key which is valid for a significant amount of time without a way  for the homeserver owner to revoke it. |
| `verify_keys` | `{string: [Verify Key](#post_matrixkeyv2query_response-200_verify-key)}` | **Required:**  Public keys of the homeserver for verifying digital signatures. The object’s key is the algorithm and version combined (`ed25519` being the  algorithm and `abc123` being the version in the example below). Together,  this forms the Key ID. The version must have characters matching the regular  expression `[a-zA-Z0-9_]`. |

Old Verify Key
| Name | Type | Description |
| --- | --- | --- |
| `expired_ts` | `integer` | **Required:** POSIX timestamp in milliseconds for when this key expired. |
| `key` | `string` | **Required:** The [Unpadded  base64](/v1.11/appendices/#unpadded-base64) encoded key. |

Verify Key
| Name | Type | Description |
| --- | --- | --- |
| `key` | `string` | **Required:** The [Unpadded  base64](/v1.11/appendices/#unpadded-base64) encoded key. |

```
{
  "server_keys": [
    {
      "old_verify_keys": {
        "ed25519:0ldk3y": {
          "expired_ts": 1532645052628,
          "key": "VGhpcyBzaG91bGQgYmUgeW91ciBvbGQga2V5J3MgZWQyNTUxOSBwYXlsb2FkLg"
        }
      },
      "server_name": "example.org",
      "signatures": {
        "example.org": {
          "ed25519:abc123": "VGhpcyBzaG91bGQgYWN0dWFsbHkgYmUgYSBzaWduYXR1cmU"
        },
        "notary.server.com": {
          "ed25519:010203": "VGhpcyBpcyBhbm90aGVyIHNpZ25hdHVyZQ"
        }
      },
      "valid_until_ts": 1652262000000,
      "verify_keys": {
        "ed25519:abc123": {
          "key": "VGhpcyBzaG91bGQgYmUgYSByZWFsIGVkMjU1MTkgcGF5bG9hZA"
        }
      }
    }
  ]
}

```

<!-- markdownlint-disable -->
<h1>GET</h1> 
<!-- markdownlint-enable -->
/\_matrix/key/v2/query/{serverName}

---

Query for another server’s keys. The receiving (notary) server must
 sign the keys returned by the queried server.

| Rate-limited: | No |
| --- | --- |
| Requires authentication: | No |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

#<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable --> parameters

path parameters
| Name | Type | Description |
| --- | --- | --- |
| `serverName` | `string` | **Required:** The server’s DNS name to query |

query parameters
| Name | Type | Description |
| --- | --- | --- |
| `minimum_valid_until_ts` | `integer` | A millisecond POSIX timestamp in milliseconds indicating when the returned  certificates will need to be valid until to be useful to the requesting server. If not supplied, the current time as determined by the notary server is used. |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| Status | Description |
| --- | --- |
| `200` | The keys for the server, or an empty array if the server could not be reached  and no cached keys were available. |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| Name | Type | Description |
| --- | --- | --- |
| `server_keys` | `[[Server Keys](#get_matrixkeyv2queryservername_response-200_server-keys)]` | The queried server’s keys, signed by the notary server. |

Server Keys
| Name | Type | Description |
| --- | --- | --- |
| `old_verify_keys` | `{string: [Old Verify Key](#get_matrixkeyv2queryservername_response-200_old-verify-key)}` | The public keys that the server used to use and when it stopped using them. The object’s key is the algorithm and version combined (`ed25519` being the  algorithm and `0ldK3y` being the version in the example below). Together,  this forms the Key ID. The version must have characters matching the regular  expression `[a-zA-Z0-9_]`. |
| `server_name` | `string` | **Required:** DNS name of the homeserver. |
| `signatures` | `{string: {string: string}}` | Digital signatures for this object signed using the `verify_keys`. The signature is calculated using the process described at [Signing JSON](/v1.11/appendices/#signing-json). |
| `valid_until_ts` | `integer` | POSIX timestamp in milliseconds when the list of valid keys should be refreshed.  This field MUST be ignored in room versions 1, 2, 3, and 4. Keys used beyond this  timestamp MUST be considered invalid, depending on the  [room version specification](/v1.11/rooms).   Servers MUST use the lesser of this field and 7 days into the future when  determining if a key is valid. This is to avoid a situation where an attacker  publishes a key which is valid for a significant amount of time without a way  for the homeserver owner to revoke it. |
| `verify_keys` | `{string: [Verify Key](#get_matrixkeyv2queryservername_response-200_verify-key)}` | **Required:**  Public keys of the homeserver for verifying digital signatures. The object’s key is the algorithm and version combined (`ed25519` being the  algorithm and `abc123` being the version in the example below). Together,  this forms the Key ID. The version must have characters matching the regular  expression `[a-zA-Z0-9_]`. |

Old Verify Key
| Name | Type | Description |
| --- | --- | --- |
| `expired_ts` | `integer` | **Required:** POSIX timestamp in milliseconds for when this key expired. |
| `key` | `string` | **Required:** The [Unpadded  base64](/v1.11/appendices/#unpadded-base64) encoded key. |

Verify Key
| Name | Type | Description |
| --- | --- | --- |
| `key` | `string` | **Required:** The [Unpadded  base64](/v1.11/appendices/#unpadded-base64) encoded key. |

```
{
  "server_keys": [
    {
      "old_verify_keys": {
        "ed25519:0ldk3y": {
          "expired_ts": 1532645052628,
          "key": "VGhpcyBzaG91bGQgYmUgeW91ciBvbGQga2V5J3MgZWQyNTUxOSBwYXlsb2FkLg"
        }
      },
      "server_name": "example.org",
      "signatures": {
        "example.org": {
          "ed25519:abc123": "VGhpcyBzaG91bGQgYWN0dWFsbHkgYmUgYSBzaWduYXR1cmU"
        },
        "notary.server.com": {
          "ed25519:010203": "VGhpcyBpcyBhbm90aGVyIHNpZ25hdHVyZQ"
        }
      },
      "valid_until_ts": 1652262000000,
      "verify_keys": {
        "ed25519:abc123": {
          "key": "VGhpcyBzaG91bGQgYmUgYSByZWFsIGVkMjU1MTkgcGF5bG9hZA"
        }
      }
    }
  ]
}

```

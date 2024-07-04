
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

     1. 如果 `<delegated_hostname>` 是 IP，
        - 使用該 IP 地址和 `<delegated_port>`(預設port為8448)
        - 目標伺服器必須提供該 IP 地址的有效 TLS 證書。
        - 請求必須包含 IP 地址的 `Host` 標頭，包括端口（如果提供）。

     2. 如果 `<delegated_hostname>` 不是 IP，並且提供 `<delegated_port>`，
        - 查找 `<delegated_hostname>` 的 CNAME、AAAA 或 A 記錄來發現 IP 地址。
        - 使用解析出的 IP 地址和 `<delegated_port>`。
        - 請求必須包含 `<delegated_hostname>:<delegated_port>` 的 `Host` 標頭。
        - 目標伺服器必須提供 `<delegated_hostname>` 的有效證書。

     3. **[v1.8 添加]** 如果 `<delegated_hostname>` 不是 IP，且未提供 `<delegated_port>`，
        - 查找 `_matrix-fed._tcp.<delegated_hostname>` 的 SRV 記錄。
        - 可能會得到另一個主機名（使用 AAAA 或 A 記錄解析）和端口。
        - 請求應發送到解析出的 IP 地址和端口，
        - `Host` 標頭包含 `<delegated_hostname>`。
        - 目標伺服器必須提供 `<delegated_hostname>` 的有效證書。

     4. ~~**[已棄用]** 如果 `<delegated_hostname>` 不是 IP，未提供 `<delegated_port>`，並且未找到 `_matrix-fed._tcp.<delegated_hostname>` 的 SRV 記錄，~~
        - ~~查找 `_matrix._tcp.<delegated_hostname>` 的 SRV 記錄。~~
        - ~~可能得到另一個主機名（使用 AAAA 或 A 記錄解析）和端口。~~
        - ~~請求應發送到解析出的 IP 地址和端口，~~
        - ~~`Host` 標頭包含 `<delegated_hostname>`。~~
        - ~~目標伺服器必須提供 `<delegated_hostname>` 的有效證書。~~

     5. 如果未找到 SRV 記錄，
        - 則使用 CNAME、AAAA 或 A 記錄解析 IP 地址。
        - 使用解析出的 IP 地址和 8448 端口發送請求，
        - `Host` 標頭包含 `<delegated_hostname>`。
        - 目標伺服器必須提供 `<delegated_hostname>` 的有效證書。

4. **[v1.8 添加]** 如果 `/.well-known` 請求導致錯誤回應，
   - 解析 `_matrix-fed._tcp.<hostname>` 的 SRV 記錄找到伺服器。
   - 可能會得到主機名（使用 AAAA 或 A 記錄解析）和端口。
   - 請求發送到解析出的 IP 地址和端口，
   - `Host` 標頭包含 `<hostname>`。
   - 目標伺服器必須提供 `<hostname>` 的有效證書。

5. ~~**[已棄用]** 如果 `/.well-known` 請求導致錯誤回應，
並且未找到 `_matrix-fed._tcp.<hostname>` 的 SRV 記錄，
則通過解析 `_matrix._tcp.<hostname>` 的 SRV 記錄找到伺服器。
這可能會導致主機名（使用 AAAA 或 A 記錄解析）和端口。
請求發送到解析出的 IP 地址和端口，
`Host` 標頭包含 `<hostname>`。
目標伺服器必須提供 `<hostname>` 的有效證書。~~

6. 如果 `/.well-known` 請求返回錯誤回應，並且未找到 SRV 記錄，
   - 使用 CNAME、AAAA 和 A 記錄解析 IP 地址。
   - 請求發送到解析出的 IP 地址，使用 8448 端口和 `Host` 標頭包含 `<hostname>`。
   - 目標伺服器必須提供 `<hostname>` 的有效證書。

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

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

無請求參數或請求主體。

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
| `m.server` | `string` | 用於委派伺服器-伺服器通訊的伺服器名稱，帶有可選端口。委派伺服器名稱使用與[附錄中的伺服器名稱](/v1.11/appendices/#server-name)相同的語法。
 |
<!-- markdownlint-enable -->

```json
{
  "m.server": "delegated.example.com:1234"
}
```

## 2.2 Server implementation

<!-- markdownlint-disable -->
<h1>GET <a>/\_matrix/federation/v1/version</a></h1> 
<!-- markdownlint-enable -->

獲取此主伺服器的執行名稱和版本。

| 速率限制： | 否 |
| --- | --- |
| 需要認證： | 否 |

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

無請求參數或請求主體。

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 此主伺服器的實現名稱和版本。 |

<!-- markdownlint-disable -->
<h3>200 Responses</h3> 
<!-- markdownlint-enable -->

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `server` | `[Server](#get_matrixfederationv1version_response-200_server)` |  |

Server
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `name` | `string` | 辨識此施行的任意名稱。 |
| `version` | `string` | 此施行的版本。版本格式取決於施行。 |

```json
{
  "server": {
    "name": "My_Homeserver_Implementation",
    "version": "ArbitraryVersionNumber"
  }
}
```

## 2.3 Retrieving server keys

曾經有一個“版本 1”的密鑰交換規範，由於意義不大，已從規範中移除。
可以從[歷史草稿](https://github.com/matrix-org/matrix-doc/blob/51faf8ed2e4a63d4cfd6d23183698ed169956cc0/specification/server_server_api.rst#232version-1)中查看。

每個主伺服器在 `/_matrix/key/v2/server` 下發布其公鑰。
主伺服器通過直接獲取 `/_matrix/key/v2/server`
或通過使用 `/_matrix/key/v2/query/{serverName}` API 查詢中間公證伺服器來查詢密鑰。
中間公證伺服器代表另一個伺服器查詢 `/_matrix/key/v2/server` API，
並用自己的密鑰簽署回應。
伺服器可以查詢多個公證伺服器，
以確保它們報告相同的公鑰。

這種方法借鑒自 [Perspectives Project](https://web.archive.org/web/20170702024706/https://perspectives-project.org/)，
但經過修改以包含 NACL 密鑰並使用 JSON 而不是 XML。
這種方法的優點是避免了單一信任根，
因為每個伺服器可以自由選擇信任的公證伺服器，
並且可以通過查詢其他伺服器來核實給定公證伺服器返回的密鑰。

### 2.3.1 Publishing Keys

Matrix 主伺服器在 `/_matrix/key/v2/server` 路徑下發布其簽名密鑰。
回應包含一個 `verify_keys` 列表，
這些密鑰對於簽名主伺服器發出的聯邦請求和事件是有效的。
此外，還包含一個 `old_verify_keys` 列表，
這些密鑰僅對簽名事件有效。

<!-- markdownlint-disable -->
<h1>GET <a>/_matrix/key/v2/server</a></h1> 
<!-- markdownlint-enable -->

獲取主伺服器發布的簽名密鑰。
主伺服器可以有任意數量的有效密鑰和舊密鑰。

中間公證伺服器應緩存回應的一半壽命，
以避免提供過期的回應。
發起伺服器應避免返回壽命少於一小時的回應，
以避免重複請求即將過期的證書。
請求伺服器應限制查詢證書的頻率，
以避免請求泛濫伺服器。

如果伺服器無法回應此請求，
中間公證伺服器應繼續返回從伺服器接收到的最後回應，
以便仍然可以檢查舊事件的簽名。

| 速率限制： | 否 |
| --- | --- |
| 需要認證： | 否 |

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

無請求參數或請求主體。

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 主伺服器的密鑰 |

<!-- markdownlint-disable -->
<h3>200 Responses</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
伺服器密鑰
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `old_verify_keys` | `{string: [Old Verify Key](#get_matrixkeyv2server_response-200_old-verify-key)}` | 伺服器以前使用的公鑰以及停止使用的時間。對象的key是算法和版本的組合（`ed25519` 是算法，`0ldK3y` 是版本）。這形成了密鑰 ID。版本必須包含匹配正則表達式 `[a-zA-Z0-9_]` 的字符。 |
| `server_name` | `string` | **必填：** 主伺服器的 DNS 名稱。 |
| `signatures` | `{string: {string: string}}` | 使用 `verify_keys` 簽署此對象的數字簽名。簽名過程描述在 [簽署 JSON](/v1.11/appendices/#signing-json)。 |
| `valid_until_ts` | `integer` | POSIX 毫秒時間戳，表示應刷新有效密鑰的時間。此字段在房間版本 1、2、3 和 4 中必須被忽略。超過此時間戳使用的密鑰必須被視為無效，具體取決於 [房間版本規範](/v1.11/rooms)。伺服器在確定密鑰是否有效時必須使用此字段和未來 7 天中的較小者。這是為了避免攻擊者發布有效時間過長且無法被主伺服器所有者撤銷的密鑰。 |
| `verify_keys` | `{string: [Verify Key](#get_matrixkeyv2server_response-200_verify-key)}` | **必填：** 用於驗證數字簽名的主伺服器公鑰。對象的key是算法和版本的組合（`ed25519` 是算法，`abc123` 是版本）。這形成了密鑰 ID。版本必須包含匹配正則表達式 `[a-zA-Z0-9_]` 的字符。 |
<!-- markdownlint-enable -->

old_verify_keys
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `expired_ts` | `integer` | **必填：** 此密鑰過期的 POSIX 毫秒時間戳。 |
| `key` | `string` | **必填：** [Unpadded base64](/v1.11/appendices/#unpadded-base64) 編碼的密鑰。 |

verify_keys
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `key` | `string` | **必填：** [Unpadded base64](/v1.11/appendices/#unpadded-base64) 編碼的密鑰。 |

```json
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

伺服器可以通過公證伺服器查詢另一個伺服器的密鑰。
公證伺服器可能是另一個主伺服器。
公證伺服器將使用 `/_matrix/key/v2/server` API 從被查詢伺服器檢索密鑰。
公證伺服器在返回結果之前，
還會對被查詢伺服器的回應進行簽名。

公證伺服器可以通過使用緩存的回應來返回離線或服務有問題的伺服器的密鑰。
可以從多個伺服器查詢密鑰，
以減少 DNS 欺騙的風險。

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

---
---

<!-- markdownlint-disable -->
<h1>POST <a>/\_matrix/key/v2/query</a></h1> 
<!-- markdownlint-enable -->

---

批量格式查詢多個伺服器的密鑰。接收（公證）伺服器必須對被查詢伺服器返回的密鑰進行簽名。

| 速率限制： | 否 |
| --- | --- |
| 需要認證： | 否 |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

Request body

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `server_keys` | `{string: {string: [Query Criteria](#post_matrixkeyv2query_request_query-criteria)}}` | **必填：** 查詢條件。對象的外部 `string` 鍵是伺服器名稱（例如：`matrix.org`）。內部 `string` 鍵是特定伺服器要查詢的密鑰 ID。如果沒有提供要查詢的密鑰 ID，公證伺服器應查詢所有密鑰。如果沒有提供伺服器，公證伺服器必須在回應中返回空的 `server_keys` 數組。無論給定的密鑰 ID 為何，公證伺服器都可以返回多個密鑰。 |
<!-- markdownlint-enable -->

查詢條件
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `minimum_valid_until_ts` | `integer` | 請求伺服器所需的密鑰有效期至的毫秒 POSIX 時間戳。如果未提供，則使用公證伺服器確定的當前時間。 |
<!-- markdownlint-enable -->

Request body example

```json
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

| 狀態 | 描述 |
| --- | --- |
| `200` | 被查詢伺服器的密鑰，由公證伺服器簽名。無法返回離線且無緩存密鑰的伺服器，可能導致返回空數組。 |

<!-- markdownlint-disable -->
<h3>200 Responses</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `server_keys` | `[[Server Keys](#post_matrixkeyv2query_response-200_server-keys)]` | 被查詢伺服器的密鑰，由公證伺服器簽名。 |
<!-- markdownlint-enable -->

伺服器密鑰
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `old_verify_keys` | `{string: [Old Verify Key](#post_matrixkeyv2query_response-200_old-verify-key)}` | 伺服器以前使用的公鑰以及停止使用的時間。對象的 key 是算法和版本的組合（`ed25519` 是算法，`0ldK3y` 是版本）。這形成了密鑰 ID。版本必須包含匹配正則表達式 `[a-zA-Z0-9_]` 的字符。 |
| `server_name` | `string` | **必填：** 主伺服器的 DNS 名稱。 |
| `signatures` | `{string: {string: string}}` | 使用 `verify_keys` 簽署此對象的數字簽名。簽名過程描述在 [簽署 JSON](/v1.11/appendices/#signing-json)。 |
| `valid_until_ts` | `integer` | POSIX 毫秒時間戳，表示應刷新有效密鑰的時間。此字段在房間版本 1、2、3 和 4 中必須被忽略。超過此時間戳使用的密鑰必須被視為無效，具體取決於 [房間版本規範](/v1.11/rooms)。伺服器在確定密鑰是否有效時必須使用此字段和未來 7 天中的較小者。這是為了避免攻擊者發布有效時間過長且無法被主伺服器所有者撤銷的密鑰。 |
| `verify_keys` | `{string: [Verify Key](#post_matrixkeyv2query_response-200_verify-key)}` | **必填：** 用於驗證數字簽名的主伺服器公鑰。對象的 key 是算法和版本的組合（`ed25519` 是算法，`abc123` 是版本）。這形成了密鑰 ID。版本必須包含匹配正則表達式 `[a-zA-Z0-9_]` 的字符。 |
<!-- markdownlint-enable -->

`old_verify_keys`
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `expired_ts` | `integer` | **必填：** 此密鑰過期的 POSIX 毫秒時間戳。 |
| `key` | `string` | **必填：** [Unpadded base64](/v1.11/appendices/#unpadded-base64) 編碼的密鑰。 |
<!-- markdownlint-enable -->

`verify_keys`
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `key` | `string` | **必填：** [Unpadded base64](/v1.11/appendices/#unpadded-base64) 編碼的密鑰。 |
<!-- markdownlint-enable -->

```json
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

\*\*補充
驗證時是將verify_keys當作驗證公鑰
"signatures": {
  "example.org": {
    "ed25519:abc123": "VGhpcyBzaG91bGQgYWN0dWFsbHkgYmUgYSBzaWduYXR1cmU"
  },
}
當作代驗證的資訊
同時可能會傳來其他公證伺服器保存的公鑰
就要先獲取其公鑰
在針對此公鑰和資料去驗證

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

---
---

<!-- markdownlint-disable -->
<h1>GET <a>/_matrix/key/v2/query/{serverName}</a></h1> 
<!-- markdownlint-enable -->

查詢另一個伺服器的密鑰。接收（公證）伺服器必須對被查詢伺服器返回的密鑰進行簽名。

| 速率限制： | 否 |
| --- | --- |
| 需要認證： | 否 |

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

Request parameters

path parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `serverName` | `string` | **必填：** 要查詢的伺服器的 DNS 名稱 |

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `minimum_valid_until_ts` | `integer` | 請求伺服器所需的密鑰有效期至的毫秒 POSIX 時間戳。如果未提供，則使用公證伺服器確定的當前時間。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 伺服器的密鑰，或者如果伺服器無法聯繫且沒有可用的緩存密鑰，則返回空數組。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `server_keys` | `[[Server Keys](#get_matrixkeyv2queryservername_response-200_server-keys)]` | 被查詢伺服器的密鑰，由公證伺服器簽名。 |
<!-- markdownlint-enable -->

伺服器密鑰
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `old_verify_keys` | `{string: [Old Verify Key](#get_matrixkeyv2queryservername_response-200_old-verify-key)}` | 伺服器以前使用的公鑰以及停止使用的時間。對象的 key 是算法和版本的組合（`ed25519` 是算法，`0ldK3y` 是版本）。這形成了密鑰 ID。版本必須包含匹配正則表達式 `[a-zA-Z0-9_]` 的字符。 |
| `server_name` | `string` | **必填：** 主伺服器的 DNS 名稱。 |
| `signatures` | `{string: {string: string}}` | 使用 `verify_keys` 簽署此對象的數字簽名。簽名過程描述在 [簽署 JSON](/v1.11/appendices/#signing-json)。 |
| `valid_until_ts` | `integer` | POSIX 毫秒時間戳，表示應刷新有效密鑰的時間。此字段在房間版本 1、2、3 和 4 中必須被忽略。超過此時間戳使用的密鑰必須被視為無效，具體取決於 [房間版本規範](/v1.11/rooms)。伺服器在確定密鑰是否有效時必須使用此字段和未來 7 天中的較小者。這是為了避免攻擊者發布有效時間過長且無法被主伺服器所有者撤銷的密鑰。 |
| `verify_keys` | `{string: [Verify Key](#get_matrixkeyv2queryservername_response-200_verify-key)}` | **必填：** 用於驗證數字簽名的主伺服器公鑰。對象的 key 是算法和版本的組合（`ed25519` 是算法，`abc123` 是版本）。這形成了密鑰 ID。版本必須包含匹配正則表達式 `[a-zA-Z0-9_]` 的字符。 |
<!-- markdownlint-enable -->

舊驗證密鑰
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `expired_ts` | `integer` | **必填：** 此密鑰過期的 POSIX 毫秒時間戳。 |
| `key` | `string` | **必填：** [Unpadded base64](/v1.11/appendices/#unpadded-base64) 編碼的密鑰。 |

驗證密鑰
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `key` | `string` | **必填：** [Unpadded base64](/v1.11/appendices/#unpadded-base64) 編碼的密鑰。 |

```json
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

稍微總結下這段，

- 如果查詢的是別人的伺服器:
  - 在signatures內附上透過他們金鑰簽名過的公鑰，
  - 在signatures內附上透過我們金鑰簽名過的公鑰
  - 如果有其他信任的公證伺服器也可以一併附上
  - 最後在verify_keys內附上**自己**伺服器簽名的公鑰
  - 其他伺服器產生的公鑰必須另外向其他伺服器請求簽名公鑰
- 如果查詢的是自己的伺服器:
  - 一切都一樣，只是自己要另外找別的公證伺服器就是

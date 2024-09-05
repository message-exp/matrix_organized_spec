# Querying for information

1. 查詢是從家庭服務器 (homeserver) 獲取資源信息的方式,如用戶或房間信息。
2. 主要有三種查詢端點:
   a) 通用查詢端點: `/\_matrix/federation/v1/query/{queryType}`
   b) 目錄查詢端點: `/\_matrix/federation/v1/query/directory`
   c) 個人資料查詢端點: `/\_matrix/federation/v1/query/profile`
3. 目錄查詢 (/query/directory):
   - 用於獲取房間別名對應的房間 ID 和所在的家庭服務器列表
   - 參數: room_alias (必須)
   - 返回: room_id 和 servers 列表
4. 個人資料查詢 (/query/profile):
   - 用於獲取用戶的個人資料信息,如顯示名稱或頭像
   - 參數: user_id (必須), field (可選,指定要查詢的字段)
   - 返回: displayname 和/或 avatar_url
5. 所有查詢都需要身份驗證,但不受速率限制。
6. 服務器可能會緩存查詢結果以減少請求頻率。
7. 查詢應只針對目標服務器所屬的資源(如用戶 ID 或房間別名中的域名)。
8. 查詢可能返回 200 (成功) 或 404 (未找到) 狀態碼。
9. 錯誤響應包含 errcode 和 error 描述。

查詢（Queries）是一種從 homeserver 獲取資源資訊的方式，例如使用者或房間。這些端點通常與 client-server API 上的客戶端請求結合使用，以完成調用。

可以進行多種類型的查詢。首先介紹代表所有查詢的通用端點，接著描述更具體的查詢。

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/query/directory</a></h1> 
<!-- markdownlint-enable -->

執行查詢以獲取給定房間別名的對應房間 ID 和房間內駐 homeserver 列表。
homeserver 應僅查詢屬於目標伺服器的房間別名（通過別名中的 DNS 名稱識別）。

伺服器可能希望對此查詢的響應進行緩存，以避免過於頻繁地請求資訊。

| 是否有速率限制: | 否 |
| --- | --- |
| 是否需要身份驗證: | 是 |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

query parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `room_alias` | `string` | **必填項:** 要查詢的房間別名。 |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 對應的房間 ID 和已知的駐留 homeserver 列表。 |
| `404` | 找不到房間別名。 |

<!-- markdownlint-disable -->
<h3>200 response</h3>
<!-- markdownlint-enable -->

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `room_id` | `string` | **必填項:** 與查詢的房間別名對應的房間 ID。 |
| `servers` | `[string]` | **必填項:** 可能包含該房間的伺服器名稱數組。此列表可能包括或不包括回應查詢的伺服器。 |

```json
{
  "room_id": "!roomid1234:example.org",
  "servers": [
    "example.org",
    "example.com",
    "another.example.com:8449"
  ]
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3>
<!-- markdownlint-enable -->

Error
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必填項:** 錯誤代碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Room alias not found."
}
```

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/query/profile</a></h1> 
<!-- markdownlint-enable -->

---

執行查詢以獲取給定使用者的個人資料資訊，如顯示名稱或頭像。homeserver 應僅查詢屬於目標伺服器的使用者個人資料（根據使用者 ID 中的 DNS 名稱識別）。

伺服器可能希望對此查詢的響應進行緩存，以避免過於頻繁地請求資訊。

| 是否有速率限制: | 否 |
| --- | --- |
| 是否需要身份驗證: | 是 |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

query parameters
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `field` | `string` | 查詢的欄位。如果指定，伺服器將只在響應中返回該欄位。如果未指定，伺服器將返回該使用者的完整個人資料。可選之一: `[displayname, avatar_url]`。 |
| `user_id` | `string` | **必填項:** 要查詢的使用者 ID。必須是接收 homeserver 的本地使用者。 |
<!-- markdownlint-enable -->

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 該使用者的個人資料。如果請求中指定了 `field`，則只應包含匹配的欄位。如果未指定 `field`，響應應包括使用者個人資料中可以公開的欄位，如顯示名稱和頭像。如果使用者未設置特定欄位，伺服器應從響應體中排除該欄位或將其值設為 `null`。 |
| `404` | 該使用者不存在或沒有個人資料。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `avatar_url` | `string` | 使用者頭像的 URL。如果使用者未設置頭像，則可能被省略。 |
| `displayname` | `string` | 使用者的顯示名稱。如果使用者未設置顯示名稱，則可能被省略。 |

```json
{
  "avatar_url": "mxc://matrix.org/MyC00lAvatar",
  "displayname": "John Doe"
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3> 
<!-- markdownlint-enable -->

Error
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **必填項:** 錯誤代碼。 |
| `error` | `string` | 可讀的錯誤訊息。 |

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "User does not exist."
}
```

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/query/{queryType}</a></h1> 
<!-- markdownlint-enable -->

在接收的 homeserver 上執行單個查詢請求。查詢字串參數取決於進行的查詢類型。已知的查詢類型將作為該定義的擴展，指定為其自己的端點。

| 是否有速率限制: | 否 |
| --- | --- |
| 是否需要身份驗證: | 是 |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

path parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `queryType` | `string` | **必填項:** 要進行的查詢類型。 |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 查詢的響應。架構依據進行的查詢而變化。 |

# Third-party invites

- 當用戶使用第三方識別符（如電子郵件或電話號碼）邀請其他用戶時，此過程涉及身份服務 API。
- 若第三方識別符已綁定至 Matrix ID，身份伺服器將返回該 ID。
- 如果未綁定 Matrix ID，邀請將存於身份伺服器，待綁定後再發送邀請。
- 身份伺服器會暫存未綁定 Matrix ID 的第三方識別符邀請，並在綁定後發送 POST 請求。
- 邀請的家庭伺服器將創建包含特殊 `third_party_invite` 的 `m.room.member` 邀請事件。
- 如果邀請的家庭伺服器在邀請發出的房間中，則可直接身份驗證並發送邀請。
- 如果不在該房間，需請求該房間的家庭伺服器進行身份驗證。
- PUT /_matrix/federation/v1/3pid/onbind
  - 這主要是身份伺服器確認好已綁定後會回傳的api
  - 通知home server目前這個邀請需要的身份已綁定
- PUT /_matrix/federation/v1/exchange_third_party_invite/{roomId}
  - 確認綁定好後會透過此api提供部分member事件的內容以利之後正式邀請
- 當家庭伺服器收到帶有 `third_party_invite` 的 `m.room.member` 邀請事件時，確認房間已存在。
- 從房間狀態事件中檢索匹配 `third_party_invite` 中 `token` 的 `m.room.third_party_invite` 事件。
- 使用事件提供的公鑰來驗證 `third_party_invite` 對象中的簽名。
- 確保 `signed` 對象中包含的 Matrix ID 和令牌是由相關的身份伺服器正確簽名的。

更多關於第三方邀請的信息可以在[客戶端-伺服器 API](/v1.11/client-server-api)的第三方邀請模組中找到。

當用戶想邀請另一個用戶進入房間但不知道要邀請的 Matrix ID 時，他們可以使用第三方識別符（例如電子郵件或電話號碼）來邀請。

這些識別符及其與 Matrix ID 的綁定由實現[身份服務 API](/v1.11/identity-service-api)的身份伺服器進行驗證。

## Cases where an association exists for a third-party identifier

If the third-party identifier is already bound to a Matrix ID, a lookup
 request on the identity server will return it. The invite is then
 processed by the inviting homeserver as a standard `m.room.member`
 invite event. This is the simplest case.

如果第三方識別符已經綁定到一個 Matrix ID，對身份伺服器進行查詢請求將返回該 ID。隨後，邀請由邀請方的家庭伺服器作為標準的 `m.room.member` 邀請事件進行處理。這是最簡單的情況。

## Cases where an association doesn’t exist for a third-party identifier

如果第三方識別符未綁定任何 Matrix ID，
邀請方的家庭伺服器將請求身份伺服器為該識別符存儲邀請，
並將其發送給將其綁定到 Matrix ID 的人。
它還將在房間內發送一個 `m.room.third_party_invite` 事件，
以指定顯示名稱、令牌和身份伺服器作為邀請存儲請求的響應提供的公鑰。

> 如果沒有綁定matrix id的話，
> 身份伺服器會先暫存一個邀請，
> 等綁定之後再提供邀請

當有待處理邀請的第三方識別符被綁定到 Matrix ID 時，
身份伺服器將向該 ID 的家庭伺服器發送一個 POST 請求，
如身份服務 API 的[邀請存儲]()部分所述。

以下流程適用於身份伺服器發送的每個邀請：

邀請的家庭伺服器將創建一個包含特殊 `third_party_invite` 部分的 `m.room.member` 邀請事件，
該部分包含由身份伺服器提供的令牌和簽名對象。

如果邀請的家庭伺服器在發出邀請的房間中，
它可以對事件進行身份驗證並發送它。

但是，
如果邀請的家庭伺服器不在發出邀請的房間中，
它將需要請求該房間的家庭伺服器對事件進行身份驗證。

1. **第三方識別符未綁定到任何 Matrix ID：**
   - 邀請方的家庭伺服器請求身份伺服器為該識別符存儲邀請。
   - 邀請方的家庭伺服器在房間內發送 `m.room.third_party_invite` 事件，包括顯示名稱、令牌和公鑰。

2. **第三方識別符被綁定到 Matrix ID：**
   - 身份伺服器向該 Matrix ID 的家庭伺服器發送 POST 請求（參考身份服務 API 的邀請存儲部分）。
   - 每個邀請的處理流程如下：

     1. **創建邀請事件：**
        - 邀請的家庭伺服器創建一個 `m.room.member` 邀請事件，包含 `third_party_invite` 部分，內含身份伺服器提供的令牌和簽名對象。
     2. **身份驗證和發送：**
        - 如果邀請的家庭伺服器在邀請發出的房間中，則可以直接對事件進行身份驗證並發送。
        - 如果不在，則需要請求房間的家庭伺服器對事件進行身份驗證。

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v1/3pid/onbind</a></h1> 
<!-- markdownlint-enable -->

此 API 用於身份伺服器通知家庭伺服器其用戶之一已成功綁定第三方識別符，包括身份伺服器已知的任何待處理的房間邀請。

| 速率限制: | No |
| --- | --- |
| 需要認證: | No |

---

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `address` | `string` | **Required:** 第三方識別符本身。例如，電子郵件地址。 |
| `invites` | `[Third-party Invite]` | **Required:** 第三方識別符收到的待處理邀請列表。 |
| `medium` | `string` | **Required:** 第三方識別符的類型。目前只有“email”是一個可能的值。 |
| `mxid` | `string` | **Required:** 現在綁定到第三方識別符的用戶。 |
<!-- markdownlint-enable -->

Third-party Invite
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `address` | `string` | **Required:** 收到邀請的第三方識別符。 |
| `medium` | `string` | **Required:** 第三方邀請的類型。目前只使用“email”。 |
| `mxid` | `string` | **Required:** 現在綁定的用戶 ID。 |
| `room_id` | `string` | **Required:** 邀請有效的房間 ID。 |
| `sender` | `string` | **Required:** 發送邀請的用戶 ID。 |
| `signed` | `[Identity Server Signatures]` | **Required:** 使用長期私鑰的身份伺服器簽名。 |
<!-- markdownlint-enable -->

Identity Server Signatures
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `mxid` | `string` | **Required:** 已綁定到第三方識別符的用戶 ID。 |
| `signatures` | `{string: [Identity Server Domain Signature]}` | **Required:** 身份伺服器的簽名。`string` 鍵是身份伺服器的域名，例如 vector.im |
| `token` | `string` | **Required:** 一個令牌。 |
<!-- markdownlint-enable -->

Identity Server Domain Signature
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `ed25519:0` | `string` | **Required:** 簽名。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "address": "alice@example.com",
  "invites": [
    {
      "address": "alice@example.com",
      "medium": "email",
      "mxid": "@alice:matrix.org",
      "room_id": "!somewhere:example.org",
      "sender": "@bob:matrix.org",
      "signed": {
        "mxid": "@alice:matrix.org",
        "signatures": {
          "vector.im": {
            "ed25519:0": "SomeSignatureGoesHere"
          }
        },
        "token": "Hello World"
      }
    }
  ],
  "medium": "email",
  "mxid": "@alice:matrix.org"
}
```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 家庭伺服器已處理通知。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

```json
{}
```

> 這個api主要是通知home server目前這個邀請需要的身份已綁定

<!-- markdownlint-disable -->
<h1>PUT<a>/_matrix/federation/v1/exchange_third_party_invite/{roomId}</a></h1> 
<!-- markdownlint-enable -->

接收伺服器將驗證請求正文中提供的部分 `m.room.member` 事件。
如果有效，
接收伺服器將按照[邀請到房間](/v1.11/server-server-api/12-Inviting-to-a-room.md)部分發出邀請，然後返回此請求的響應。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request parameters</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要交換第三方邀請的房間 ID |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Event Content]` | **Required:** 事件內容 |
| `room_id` | `string` | **Required:** 事件所屬的房間 ID。必須與路徑中給出的 ID 匹配。 |
| `sender` | `string` | **Required:** 發送原始 `m.room.third_party_invite` 事件的用戶 ID。 |
| `state_key` | `string` | **Required:** 被邀請的用戶 ID |
| `type` | `string` | **Required:** 事件類型。必須是 `m.room.member` |
<!-- markdownlint-enable -->

Event Content
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `membership` | `string` | **Required:** 成員狀態。必須是 `invite` |
| `third_party_invite` | `[Third-party Invite]` | **Required:** 第三方邀請 |
<!-- markdownlint-enable -->

Third-party Invite
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `display_name` | `string` | **Required:** 一個可以顯示以代表用戶的名稱，而不是他們的第三方識別符。 |
| `signed` | `[Invite Signatures]` | **Required:** 一個已簽名的內容塊，伺服器可以用來驗證事件。 |
<!-- markdownlint-enable -->

Invite Signatures
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `mxid` | `string` | **Required:** 被邀請的 Matrix 用戶 ID |
| `signatures` | `{string: {string: string}}` | **Required:** 此事件的伺服器簽名。簽名是使用[簽名 JSON]()過程計算的。 |
| `token` | `string` | **Required:** 用來驗證事件的令牌 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>Request body example</h3> 
<!-- markdownlint-enable -->

```json
{
  "content": {
    "membership": "invite",
    "third_party_invite": {
      "display_name": "alice",
      "signed": {
        "mxid": "@alice:localhost",
        "signatures": {
          "magic.forest": {
            "ed25519:3": "fQpGIW1Snz+pwLZu6sTy2aHy/DYWWTspTJRPyNp0PKkymfIsNffysMl6ObMMFdIJhk6g6pwlIqZ54rxo8SLmAg"
          }
        },
        "token": "abc123"
      }
    }
  },
  "room_id": "!abc123:matrix.org",
  "sender": "@joe:matrix.org",
  "state_key": "@someone:example.org",
  "type": "m.room.member"
}
```

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 狀態 | 描述 |
| --- | --- |
| `200` | 邀請已成功發出。 |
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

```json
{}
```

### 驗證邀請

當家庭伺服器接收到包含 `third_party_invite` 對象的房間 `m.room.member` 邀請事件時，
如果該房間已存在於伺服器中，
則必須驗證最初邀請進入房間的第三方識別符與聲稱與其綁定的 Matrix ID 之間的關聯已被驗證，
而不必依賴第三方伺服器。

為此，
它將從房間的狀態事件中提取 `m.room.third_party_invite` 事件，
其 state key 與 `third_party_invite` 對象中 `token` 鍵的值相匹配，
以提取最初由存儲邀請的身份伺服器提供的公鑰。

然後，
它將使用這些鍵來驗證 `third_party_invite` 對象中 `signed` 對象（在 `m.room.member` 事件的內容中）是否由同一身份伺服器簽署。

由於這個 `signed` 對象只能在第三方識別符與 Matrix ID 綁定時由身份伺服器發出的 POST 請求中傳遞，
並且包含被邀請用戶的 Matrix ID 和存儲邀請時提供的令牌，
因此這種驗證將證明 `m.room.member` 邀請事件來自擁有被邀請的第三方識別符的用戶。

1. **查找邀請事件**：
    - 首先，從房間的狀態事件中查找 `m.room.third_party_invite` 事件。
    這個事件的 `state_key` 應該與 `m.room.member` 事件中的 `third_party_invite` 對象的 `token` 鍵的值相匹配。

2. **提取公鑰**：
    - 一旦找到匹配的 `m.room.third_party_invite` 事件，
    伺服器將提取這個事件中包含的公鑰。
    這些公鑰是最初由身份伺服器提供的，
    當時身份伺服器存儲了這個邀請。

3. **驗證簽名**：
    - 接下來，伺服器將使用提取的公鑰來驗證 `third_party_invite` 對象中的 `signed` 對象是否由身份伺服器簽署。
    這個 `signed` 對象包含邀請用戶的 Matrix ID 和令牌。

4. **確認邀請的合法性**：
    - 如果簽名驗證成功，這證明 `m.room.member` 邀請事件確實是針對擁有該第三方識別符的用戶發出的，
    從而確認了邀請的合法性。

簡單來說，這個過程確保了第三方識別符（如電子郵件地址）與其對應的 Matrix ID 之間的關聯是正確且被驗證過的，從而防止任何偽造的邀請事件。

- 當家庭伺服器收到帶有 `third_party_invite` 的 `m.room.member` 邀請事件時，確認房間已存在。
- 從房間狀態事件中檢索匹配 `third_party_invite` 中 `token` 的 `m.room.third_party_invite` 事件。
- 使用事件提供的公鑰來驗證 `third_party_invite` 對象中的簽名。
- 確保 `signed` 對象中包含的 Matrix ID 和令牌是由相關的身份伺服器正確簽名的。

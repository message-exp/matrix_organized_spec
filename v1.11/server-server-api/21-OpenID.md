# OpenID


第三方服務可以使用由 Client-Server API 先前生成的存取權杖交換用戶資訊。這有助於驗證用戶的身份，而不需完全授權對其帳號的存取。

由 OpenID API 生成的存取權杖只能用於 OpenID API，不能用於其他用途。

<!-- markdownlint-disable -->
<h1>GET<a>/_matrix/federation/v1/openid/userinfo</a></h1> 
<!-- markdownlint-enable -->

---

該 API 會使用 OpenID 存取權杖來獲取生成該權杖的用戶資訊。目前僅公開擁有者的 Matrix 用戶 ID。

| Rate-limited | Requires authentication |
| --- | --- |
| No  | No  |

---

<!-- markdownlint-disable -->
<h2>Request parameters</h2>
<!-- markdownlint-enable -->

#### query parameters

| Name           | Type     | Description                                                                     |
| -------------- | -------- | ------------------------------------------------------------------------------- |
| `access_token` | `string` | **Required:** 用於獲取擁有者資訊的 OpenID 存取權杖。|

---

<!-- markdownlint-disable -->
<h2>Responses</h2>
<!-- markdownlint-enable -->

| Status | Description |
| ------ | ----------- |
| `200`  | 生成 OpenID 存取權杖的用戶資訊。 |
| `401`  | 權杖無效或已過期。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| Name | Type     | Description                                        |
| ---- | -------- | -------------------------------------------------- |
| `sub` | `string` | **Required:** 生成權杖的 Matrix 用戶 ID。 |

```json
{
  "sub": "@alice:example.com"
}
```

<h3>401 response</h3>

Error

| Name      | Type     | Description                         |
| --------- | -------- | ----------------------------------- |
| `errcode` | `string` | **Required:** 錯誤代碼。              |
| `error`   | `string` | 可讀取的錯誤訊息。                   |

```json
{
  "errcode": "M_UNKNOWN_TOKEN",
  "error": "Access token unknown or expired"
}
```

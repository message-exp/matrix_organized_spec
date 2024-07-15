# Application-Server API

1. [註冊服務 (Registration)](./1_1_registration.md)

2. [家用伺服器 到 應用程式服務API (Homeserver -> Application Service API)](./1_2_homeserver_to_AS_API.md)

3. [客戶端-伺服器 API 擴充 (Client-Server API Extensions)](./1_3_client_server_api_extensions.md)

4. [引用第三方網路的資訊 (Referencing messages from a third-party network)](./1_4_ref_from_third_party_network.md)

---
## 前言

Matrix的 [客戶端-伺服器端 API(client-server API)](v1.11\client-server-api\_index.zh-tw.md) 和[伺服器端-伺服器端 API(server-server API)](v1.11\server-server-api\_index.md) 提供了實現 **一致的自包含聯邦消息傳遞結構** (a consistent self-contained federated messaging fabric) 的方法。

但是，它們對於實現 Matrix 中的自定義伺服器端行為，如閘道(gateways)、過濾器(filters)、可擴展掛鉤(extensible hooks)等 的支持有限。

應用服務 API（Application Server API，簡稱**AS API**）定義了一個標準 API，允許實現這些可擴展功能，而不受基礎家庭服務器實現的限制。
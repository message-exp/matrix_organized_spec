### 第三方網絡

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/third_party_networks.md)

應用服務可以通過橋接提供對第三方網絡的訪問。這允許 Matrix 使用者與其他通信平台上的使用者進行通信，消息由應用服務來回傳遞。單個應用服務可以橋接多個第三方網絡，以及這些網絡內的許多個別位置。單個第三方網絡位置可以橋接到多個 Matrix 房間。

#### 第三方查詢

客戶端可能希望提供豐富的界面來加入第三方位置並與第三方使用者連接。第三方查詢提供了此類界面所需的信息。

{{% http-api spec="client-server" api="third_party_lookup" %}}

### 訪客訪問

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/guest_access.md)

有時候，客戶端希望能夠與房間互動，而無需在主伺服器上完全註冊賬戶或加入房間。本模組規定了這些客戶端應該如何與伺服器互動，以便作為訪客參與房間。

訪客用戶使用普通的[註冊端點](#post_matrixclientv3register)從主伺服器檢索訪問令牌，指定 `kind` 參數為 `guest`。然後，他們可以像其他用戶一樣與客戶端-伺服器 API 互動，但只能訪問 API 的一個子集，如下面的客戶端行為小節所述。主伺服器可以選擇完全不允許其本地用戶進行這種訪問，但對其他主伺服器的用戶是否為訪客沒有信息。

訪客用戶還可以通過普通的 `register` 流程升級他們的賬戶，但需要指定額外的 POST 參數 `guest_access_token`，其中包含訪客的訪問令牌。他們還需要將 `username` 參數指定為其用戶名的本地部分，這在其他情況下是可選的。

本模組沒有完全考慮聯邦；它依賴於個別主伺服器正確遵守本模組中規定的規則，而不是允許所有主伺服器相互強制執行規則。

#### 事件

```
{{% event event="m.room.guest_access" %}}
```

#### 客戶端行為

以下 API 端點允許訪客賬戶訪問以檢索事件：

* [GET /rooms/{roomId}/state](#get_matrixclientv3roomsroomidstate)
* [GET /rooms/{roomId}/context/{eventId}](#get_matrixclientv3roomsroomidcontexteventid)
* [GET /rooms/{roomId}/event/{eventId}](#get_matrixclientv3roomsroomideventeventid)
* [GET /rooms/{roomId}/state/{eventType}/{stateKey}](#get_matrixclientv3roomsroomidstateeventtypestatekey)
* [GET /rooms/{roomId}/messages](#get_matrixclientv3roomsroomidmessages)
* {{< added-in v="1.1" >}} [GET /rooms/{roomId}/members](#get_matrixclientv3roomsroomidmembers)
* [GET /rooms/{roomId}/initialSync](#get_matrixclientv3roomsroomidinitialsync)
* [GET /sync](#get_matrixclientv3sync)
* [GET /events](#get_matrixclientv3events) 用於房間預覽。

以下 API 端點允許訪客賬戶訪問以發送事件：

* [POST /rooms/{roomId}/join](#post_matrixclientv3roomsroomidjoin)
* [POST /rooms/{roomId}/leave](#post_matrixclientv3roomsroomidleave)
* [PUT /rooms/{roomId}/send/{eventType}/{txnId}](#put_matrixclientv3roomsroomidsendeventtypetxnid)

    * {{< changed-in v="1.2" >}} 訪客現在可以發送*任何*事件類型，而不僅僅是 `m.room.message` 事件。

* {{< added-in v="1.2" >}} [PUT /rooms/{roomId}/state/{eventType}/{stateKey}](#put_matrixclientv3roomsroomidstateeventtypestatekey)
* [PUT /sendToDevice/{eventType}/{txnId}](#put_matrixclientv3sendtodeviceeventtypetxnid)

以下 API 端點允許訪客賬戶訪問以進行自己的賬戶維護：

* [PUT /profile/{userId}/displayname](#put_matrixclientv3profileuseriddisplayname)
* [GET /devices](#get_matrixclientv3devices)
* [GET /devices/{deviceId}](#get_matrixclientv3devicesdeviceid)
* [PUT /devices/{deviceId}](#put_matrixclientv3devicesdeviceid)
* {{< added-in v="1.2" >}} [GET /account/whoami](#get_matrixclientv3accountwhoami)

以下 API 端點允許訪客賬戶訪問以進行端到端加密：

* [POST /keys/upload](#post_matrixclientv3keysupload)
* [POST /keys/query](#post_matrixclientv3keysquery)
* [POST /keys/claim](#post_matrixclientv3keysclaim)

#### 伺服器行為

伺服器必須只允許訪客用戶加入房間，如果房間中存在 `m.room.guest_access` 狀態事件，並且其 `guest_access` 值為 `can_join`。如果 `m.room.guest_access` 事件被更改為不再符合這種情況，伺服器必須將這些用戶的 `m.room.member` 狀態設置為 `leave`。

#### 安全考慮

每個主伺服器自行管理其訪客賬戶，賬戶是否為訪客賬戶的信息不會在伺服器之間傳遞。因此，任何參與房間的伺服器都被信任能夠正確執行本節中概述的權限。

主伺服器可能想要為訪客註冊啟用諸如驗證碼之類的保護措施，以防止垃圾郵件、拒絕服務和類似攻擊。

主伺服器可能想要對訪客賬戶設置更嚴格的速率限制，特別是對於發送狀態事件。
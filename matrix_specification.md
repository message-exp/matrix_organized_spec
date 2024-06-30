# Matrix Specification

<!-- markdownlint-disable -->
<p style="font-size:14px; color:gray;">translate with GPT-4o</p>
<!-- markdownlint-enable -->

Matrix 定義了一套用於去中心化通訊的開放 API，
適用於在全球開放的伺服器聯邦中安全地發布、持久化和訂閱數據[1]，
且無需單一控制點。
其應用包括即時訊息傳遞 (IM)、VoIP (網路語音) 、物聯網 (IoT) 通訊，
以及連接現有的通訊孤島——為新型開放實時通訊生態系統提供基礎。

[1] 我真不知道怎麼翻比較好

要提議對 Matrix 規範進行更改，請參閱[Matrix 規範更改提案的說明](/v1.11/proposals)。

<!-- markdownlint-disable -->
- [Matrix Specification](#matrix-specification)
  - [1. Matrix APIs](#1-matrix-apis)
  - [2. Introduction to the Matrix APIs](#2-introduction-to-the-matrix-apis)
    - [2.1 Spec Change Proposals](#21-spec-change-proposals)
  - [3. Architecture](#3-architecture)
    - [3.1 Users](#31-users)
    - [3.2 Devices](#32-devices)
    - [3.3 Events](#33-events)
    - [3.4 Event Graphs](#34-event-graphs)
    - [3.5 Room structure](#35-room-structure)
      - [3.5.1 Room Aliases](#351-room-aliases)
    - [3.6 Identity](#36-identity)
    - [3.7 Profiles](#37-profiles)
    - [3.8 Private User Data](#38-private-user-data)
  - [4. Common concepts](#4-common-concepts)
    - [4.1 Namespacing](#41-namespacing)
    - [4.2 Timestamps](#42-timestamps)
  - [5. Specification Versions](#5-specification-versions)
    - [5.1 Endpoint versioning](#51-endpoint-versioning)
    - [5.2 Deprecation policy](#52-deprecation-policy)
    - [5.3 Legacy versioning](#53-legacy-versioning)
  - [6. License](#6-license)
<!-- markdownlint-enable -->

## 1. Matrix APIs

這個規範由以下部分組成：

- [Client-Server API](/v1.11/client-server-api)
- [Server-Server API](/v1.11/server-server-api)
- [Application Service API](/v1.11/application-service-api)
- [Identity Service API](/v1.11/identity-service-api)
- [Push Gateway API](/v1.11/push-gateway-api)
- [Room Versions](/v1.11/rooms)
- [Appendices](/v1.11/appendices)

此外，這個介紹頁面包含理解特定API所需的關鍵基礎訊息，包括[整體架構](#3-architecture)部分。

[Matrix API Viewer](https://matrix.org/docs/api/) 對於瀏覽Client-Server API非常有用。

## 2. Introduction to the Matrix APIs

Matrix 是一組開放的 API，
用於開放聯邦的即時通訊（IM）、IP 語音（VoIP）和物聯網（IoT）通訊，
旨在創建和支持一個新的全球實時通訊生態系統。
其目的是為全球網路提供一個開放的去中心化 pubsub 層，
用於安全地持久化和發布/訂閱 JSON 對象。
這個規範是標準化 Matrix 生態系統中各組件相互通訊所用 API 的持續結果。

> pubsub layer 是一種訊息傳遞模式，發布者將訊息發布到主題上，訂閱者訂閱主題以接收訊息，實現系統間的解耦合和靈活通訊。

Matrix 試圖遵循的原則包括：

- 務實的網絡友好 API（例如，基於 REST 的 JSON）
- 保持簡單愚蠢原則
  - 提供一個簡單的架構，並且第三方依賴最少。
- 完全開放：
  - 完全開放的聯邦 - 任何人都應該能夠參與全球 Matrix 網絡
  - 完全開放的標準 - 公開記錄的標準，無知識產權或專利許可的障礙
  - 完全開放的源代碼參考實現 - 自由許可的示例實現，無知識產權或專利許可的障礙
- 賦予終端用戶權力
  - 用戶應能夠選擇他們使用的伺服器和客戶端
  - 用戶應能夠控制其通訊的隱私程度
  - 用戶應確切知道他們的數據儲存位置
- 完全去中心化 - 對話或整個網絡沒有單一控制點
- 從歷史中學習以避免重蹈覆轍
  - 盡量取 XMPP、SIP、IRC、SMTP、IMAP 和 NNTP (總之就是各種通訊協議)的最佳方面，同時避免其缺陷

Matrix 提供的功能包括：

- 創建和管理完全分佈式的聊天室，沒有單一的控制點或故障點
- 在全球開放的聯邦伺服器和服務網絡中，實現房間狀態的最終一致性和加密安全同步
- 在房間內發送和接收可擴展的訊息，並可選擇端到端加密
- 可擴展的用戶管理（邀請、加入、離開、踢出、禁止），通過基於權限級別的用戶特權系統進行調解
- 可擴展的房間狀態管理（房間命名、別名、主題、禁止）
- 可擴展的用戶資料管理（頭像、顯示名稱等）
- 管理用戶帳號（註冊、登錄、登出）
- 使用第三方 ID（3PIDs），如電子郵件地址、電話號碼、Facebook 帳號，來驗證、識別和發現 Matrix 上的用戶
- 可信的身份伺服器聯邦，用於：
  - 發佈用戶公鑰進行公鑰基礎設施（PKI）
  - 將 3PIDs 映射到 Matrix ID

Matrix 的最終目標是成為一個普遍的訊息層，
用於在一組人、設備和服務之間同步任意數據，
無論是即時訊息、VoIP 通話設置，
還是任何其他需要在 A 到 B 之間可靠和持久推送的對象，
以可互操作和聯邦的方式進行。

### 2.1 Spec Change Proposals

要提議對 Matrix 規範進行更改，請參見[對 Matrix 規範更改的提案](/v1.11/proposals)。

## 3. Architecture

Matrix 定義了一組 API，
用於在兼容的客戶端、伺服器和服務之間同步稱為“事件”的可擴展 JSON 對象。
客戶端通常是訊息/VoIP 應用或 IoT 設備/hubs，通過使用“Client-Server API”與其“主伺服器”同步通訊歷史來進行通訊。
每個主伺服器儲存其所有客戶端的通訊歷史和帳號訊息，
並通過與其他主伺服器及其客戶端同步通訊歷史來與更廣泛的 Matrix 生態系統共享數據。

客戶端通常通過在虛擬“房間”的上下文中發出事件來進行通訊。
房間數據在所有參與特定房間的主伺服器之間複製。
因此，沒有單一的主伺服器擁有或控制特定的房間。
主伺服器將通訊歷史建模為事件的部分有序圖，
稱為房間的“事件圖”，
該圖通過“Server-Server API”在參與的伺服器之間進行最終一致性同步。
這種在不同實體運行的主伺服器之間同步共享對話歷史的過程稱為“聯邦”。
Matrix 在 CAP 定理中優化了可用性和分區屬性，
但以犧牲一致性為代價。

例如，為了讓客戶端 A 向客戶端 B 發送訊息，
客戶端 A 使用 Client-Server API 在其主伺服器（HS）上執行所需 JSON 事件的 HTTP PUT 操作。
A 的主伺服器將此事件附加到其房間事件圖的副本中，
並在圖的上下文中簽署訊息以保證完整性。
A 的主伺服器然後使用 Server-Server API 執行 HTTP PUT 操作將訊息複製到 B 的主伺服器。
B 的主伺服器驗證請求，驗證事件的簽名，授權事件的內容，
然後將其添加到房間事件圖的副本中。
客戶端 B 然後通過長時間保持的 GET 請求從其主伺服器接收訊息。

數據在客戶端之間的流動方式：

```text
    { Matrix 客戶端 A }                             { Matrix 客戶端 B }
        ^          |                                    ^          |
        |  events  |  Client-Server API                 |  events  |
        |          V                                    |          V
    +------------------+                            +------------------+
    |                  |---------( HTTPS )--------->|                  |
    |   home server    |                            |   home server    |
    |                  |<--------( HTTPS )----------|                  |
    +------------------+      Server-Server API     +------------------+
                               歷史同步（聯邦）
```

```text
結論: 主要的架構是以用戶和其主伺服器進行交互，並以"房間"作為通訊的一個單位(類似discord的頻道?)，不同主伺服器之間互相複製房間的上下文來同步一個房間的內容，換言之一個房間可能不會被一個主伺服器控制。
```

### 3.1 Users

每個客戶端都與一個使用者帳號相關聯，
該帳號在 Matrix 中使用唯一的「使用者 ID」進行識別。
這個 ID 以分配帳號的主伺服器為命名空間，形式如下：

```text
@localpart:domain
```

有關使用者 ID 結構的詳細信息，請參見附錄中的[「識別符語法」](/v1.11/appendices#identifier-grammar)。

### 3.2 Devices

Matrix 規範對「設備」一詞有特定的含義。
作為使用者，我可能有多個設備：桌面客戶端、一堆網頁瀏覽器、一台 Android 設備、一部 iPhone 等。
這些設備大致對應於物理世界中的實際設備，
但你可能在一個物理設備上有多個瀏覽器，
或者在一個移動設備上有多個 Matrix 客戶端應用，
這些每個都會被視為一個獨立的設備。

設備主要用於管理端到端加密所使用的密鑰（每個設備獲得自己的一份解密密鑰），
但它們也幫助使用者管理存取權限——例如，撤銷特定設備的存取權限。

當使用者首次使用客戶端時，
它會註冊為一個新設備。
設備的持久性可能取決於客戶端的類型。
網頁客戶端可能會在登出時刪除所有狀態，
並在每次登入時創建一個新設備，
以確保密鑰不會洩露給新使用者。
在移動客戶端中，如果登入會話過期，
可能允許重用設備，只要使用者相同。

設備由 `device_id` 識別，在給定使用者的範圍內是唯一的。

使用者可以為設備指定一個易讀的顯示名稱，以幫助他們管理設備。

### 3.3 Events

所有在 Matrix 上交換的數據都表達為一個「事件」。
通常，每個客戶端的動作（例如發送消息）與一個事件完全對應。
每個事件都有一個 `type`，用於區分不同類型的數據。
`type` 值必須按照 Java 的[包命名規範](https://en.wikipedia.org/wiki/Java_package#Package_naming_conventions)在全球唯一命名，
例如 `com.example.myapp.event`。
頂級命名空間 `m.` 保留給 Matrix 規範中定義的事件——
例如，`m.room.message` 是即時消息的事件類型。
事件通常在「房間」的上下文中發送。

而事件主體本身是被視為不受信任的數據。
這意味著任何使用 Matrix 的應用程式在直接使用內容之前，
必須驗證事件主體是否符合預期的結構/模式。

**假設事件主體具有所有預期類型的所有預期欄位是不安全的。**

有關為什麼這種假設不安全的更多細節，
請參見 [MSC2801](https://github.com/matrix-org/matrix-spec-proposals/blob/main/proposals/2801-untrusted-event-data.md)。

### 3.4 Event Graphs

在房間上下文中交換的事件儲存在一個稱為「事件圖」的有向無環圖（DAG）中。
這個圖的部分排序給出了房間內事件的時間順序。
圖中的每個事件都有一個或多個「父」事件的列表，
這些父事件指的是從創建事件的主伺服器的角度來看沒有時間繼承者的任何前置事件。

通常，一個事件有一個父事件：即發送時房間中的最新消息。
然而，當主伺服器之間發送消息時，可能會合法地競爭，
導致單個事件有多個繼承者。
接下來添加到圖中的事件因此會有多個父事件。

當然，每個事件圖都有一個沒有父事件的根事件。

為了排序和便於比較圖中事件的時間順序，
主伺服器在每個事件上維護一個 `depth` 詮釋資料欄位。
事件的 `depth` 是一個正整數，必須嚴格大於其任何父事件的深度。
根事件應具有深度 1。
因此，如果一個事件在另一個事件之前，那麼它的深度必須嚴格小於後者的深度。

### 3.5 Room structure

房間是一個概念性的位置，
使用者可以在此發送和接收事件。
事件被發送到房間，並且所有具有足夠訪問權限的房間參與者都會接收到該事件。
房間在內部通過「房間 ID」唯一標識，格式如下：

```text
!opaque_id:domain
```

每個房間只有一個房間 ID。
儘管房間 ID 包含一個域名，但這僅用於全局命名空間，
房間並不駐留在指定的域名上。

有關房間 ID 結構的詳細信息，請參見附錄中的[「識別符語法」](/v1.11/appendices#identifier-grammar)。

下圖展示了一個 `m.room.message` 事件被發送到房間 `!qporfwt:matrix.org` 的概念性示意圖：

```text
{ @alice:matrix.org }                             { @bob:example.org }
        |                                                 ^
        |                                                 |
[HTTP POST]                                  [HTTP GET]
Room ID: !qporfwt:matrix.org                 Room ID: !qporfwt:matrix.org
Event type: m.room.message                   Event type: m.room.message
Content: { JSON object }                     Content: { JSON object }
        |                                                 |
        V                                                 |
+------------------+                          +------------------+
|   home server    |                          |   home server    |
|   matrix.org     |                          |   example.org    |
+------------------+                          +------------------+
        |                                                 ^
        |         [HTTP PUT]                              |
        |         Room ID: !qporfwt:matrix.org            |
        |         Event type: m.room.message              |
        |         Content: { JSON object }                |
        `-------> 指向前一條消息的指針       ---------------`
                  matrix.org 的 PKI 簽名
                  交易層詮釋資料
                  PKI 授權標頭

              ....................................
             |           Shared Data              |
             | State:                             |
             |   Room ID: !qporfwt:matrix.org     |
             |   Servers: matrix.org, example.org |
             |   Members:                         |
             |    - @alice:matrix.org             |
             |    - @bob:example.org              |
             | Messages:                          |
             |   - @alice:matrix.org              |
             |     Content: { JSON object }       |
             |....................................|

```

> PKI（公開密鑰基礎設施）是一種框架，用於管理和分發數字證書和公開密鑰，確保網絡通信中的身份驗證、數據加密和數據完整性。
> PKI 主要包括數字證書、證書頒發機構（CA）、註冊機構（RA）、密鑰對、證書存取目錄和證書撤銷列表（CRL）。通過這些組成部分，PKI 提供身份驗證、數據加密、數據完整性和數字簽名等功能，為網絡通信提供安全保障。

聯邦在多個主伺服器之間維護每個房間的共享數據結構。數據分為「消息事件」和「狀態事件」。

**消息事件**：
這些事件描述房間中的短暫「一次性」活動，例如即時消息、VoIP 通話設置、文件傳輸等。它們通常描述通信活動。

**狀態事件**：
這些事件描述與房間相關的持久信息（「狀態」）的更新，
例如房間的名稱、主題、成員資格、參與的伺服器等。
狀態被建模為每個房間的鍵/值對查找表，
每個鍵是 `state_key` 和 `event type` 的組合。
每個狀態事件更新給定鍵的值。

在特定時間點的房間狀態是通過考慮圖中給定事件之前及包含該事件的所有事件來計算的。
如果事件描述相同的狀態，則應用合併衝突算法。
狀態解析算法是可傳遞的，不依賴於伺服器狀態，
因為它必須在無論伺服器或事件接收順序如何的情況下，
一致地選擇相同的事件。
事件由原始伺服器簽名（簽名包括父關係、類型、深度和有效負載哈希），
並通過聯邦推送到房間中參與的伺服器，
目前使用全網拓撲。
伺服器也可以通過聯邦從其他參與房間的伺服器請求事件的回填。

事件不限於本規範中定義的類型。
可以隨意使用 Java 包命名規範創建新的或自定義的事件類型。
例如，客戶端可以發送 `com.example.game.score` 事件，
並且其他客戶端會通過 Matrix 接收到它，
前提是客戶端具有 `com.example` 命名空間的訪問權。

#### 3.5.1 Room Aliases

每個房間也可以有多個「房間別名」，其格式如下：

```text
#room_alias:domain
```

有關房間別名結構的詳細信息，
請參見附錄中的[「識別符語法」](/v1.11/appendices#identifier-grammar)。

房間別名「指向」一個房間 ID，
並且是房間被公開和發現時的人類可讀標籤。
通過訪問指定的域名，
可以獲取別名指向的房間 ID。
請注意，
房間別名到房間 ID 的映射並不是固定的，
隨時間可能會指向不同的房間 ID。
因此，客戶端應該在解析房間別名後獲取一次房間 ID，
然後在後續請求中使用該 ID。

在解析房間別名時，
伺服器還會回應一個包含房間中伺服器列表的響應，
這些伺服器可以用於加入房間。

```text
HTTP GET
#matrix:example.org      !aaabaa:matrix.org
       |                    ^
       |                    |
_______V____________________|____
|          example.org           |
| Mappings:                      |
| #matrix >> !aaabaa:matrix.org  |
| #golf   >> !wfeiofh:sport.com  |
| #bike   >> !4rguxf:matrix.org  |
|________________________________|
```

### 3.6 Identity

在 Matrix 中，
用戶通過他們的 Matrix 使用者 ID 進行識別。
然而，也可以使用現有的第三方 ID 命名空間來識別 Matrix 用戶。
Matrix 的「身份」描述了使用者 ID 以及與其帳號**連結**的任何其他現有第三方命名空間的 ID。
Matrix 用戶可以**連結**電子郵件地址、社交網絡帳號和電話號碼等第三方 ID（3PIDs）到他們的使用者 ID。
連結 3PIDs 會創建一個從 3PID 到使用者 ID 的映射。
這個映射可以被 Matrix 用戶用來發現他們聯絡人的使用者 ID。
為了確保 3PID 到使用者 ID 的映射是真實的，
使用了一個全球聯邦的受信任「身份伺服器」（IS）集群來驗證 3PID 並持久化和複製映射。

雖然客戶端應用程式不需要使用身份伺服器就可以成為 Matrix 生態系統的一部分，
但沒有身份伺服器的話，
客戶端將無法使用 3PIDs 查找使用者 ID。

### 3.7 Profiles

使用者可以發布與其帳號相關的任意鍵/值數據，
例如可讀的顯示名稱、個人資料照片 URL、聯絡信息（電子郵件地址、電話號碼、網站 URL 等）。

### 3.8 Private User Data

使用者也可以在其帳號中儲存任意私有的 key/value 數據，
例如客戶端偏好設定或缺乏專用 API 的伺服器配置設定。
這個 API 與管理個人資料數據的方式是對稱的。

## 4. Common concepts

在所有 Matrix API 中，有些概念是通用的。這裡對這些概念進行了說明。

### 4.1 Namespacing

命名空間有助於防止多個應用程式和規範本身之間的衝突。
當使用命名空間時，
規範使用 m. 前綴來表示該欄位由規範控制。
在實際使用中的自定義或非規範的命名空間必須使用 Java 包命名規範以防止衝突。

例如，規範中定義的事件類型在特別的 m. 前綴下命名空間化，
然而任何客戶端都可以發送自定義的事件類型，
例如 com.example.game.score（假設客戶端有權使用 com.example 命名空間），
而不需要將事件放入 m. 命名空間。

### 4.2 Timestamps

除非另有說明，
時間戳是從 Unix 紀元（1970-01-01 00:00:00 UTC）起經過的毫秒數，
不計閏秒，
因此每一天精確地為 86,400,000 毫秒。

這意味著時間戳在閏秒期間可能會重複。
大多數程式語言原生地提供這種格式的時間戳，
例如 [ECMAScript](https://tc39.es/ecma262/multipage/numbers-and-dates.html#sec-time-values-and-time-range)。
在整個規範中，這種時間戳可能被稱為 POSIX、[Unix](https://en.wikipedia.org/wiki/Unix_time) 或僅僅稱為「毫秒時間」。

## 5. Specification Versions

整個 Matrix 以單一規範號釋出，
格式為 `vX.Y`。

- 更改 `X` 代表一次重大或實質性入侵的變更。
何時確切地增量此數字由規範核心團隊決定，
但這通常用於諸如放棄 JSON、改變簽名算法，
或當大量 `Y` 變更值得一次主要版本增加時。
- 更改 `Y` 代表向後相容或「受管理的」向後相容的變更，
通常以功能形式出現。

此外，規範版本後面加上 `-` 可以附加任意元資料。
例如，`v1.1-alpha`。
這種用法沒有嚴格規範，
但意在用於規範的預發布版本。

需要注意的是，
雖然 `v1.2` 意味著與 `v1.1` 向後相容，
但未來版本不保證與 `v1.1` 完全向後相容。
例如，如果 `/test` 在 `v1.1` 中引入並在 `v1.2` 中棄用，
那麼它可以在 `v1.3` 中被移除。
更多信息請參見下面的[棄用政策](#52-deprecation-policy)。

### 5.1 Endpoint versioning

規範中的所有 API 端點都是單獨版本化的。
這意味著 `/v3/sync`（例如）可以被棄用而轉向 `/v4/sync`，
而不會影響 `/v3/profile`。
支持 `/v4/sync` 的伺服器會繼續像往常一樣提供 `/v3/profile` 服務。

當 MSC（Matrix Spec Change）提議對某個端點進行重大變更時，
它應該同時棄用現有的端點。
對於一些端點，
這可能是隱含的，
例如引入 `/v4/sync`（棄用 `/v3/sync`），
然而對於更細微的情況，
MSC 應該明確地棄用該端點。

### 5.2 Deprecation policy

MSC（Matrix Spec Change）是從穩定狀態（預設）轉換到棄用狀態所需的過程。
一旦某個功能被棄用足夠長的時間（通常為一個版本），
就可以通過另一個 MSC 將其從規範中移除。

Matrix 的實現必須實現規範中被棄用的功能，
但當該功能被移除後，
實現可以選擇不再支持（如果他們不宣告支持包含該被棄用功能的版本）。
例如，如果 `/test` 在 `v1.2` 中被棄用並在 `v1.3` 中移除，
那麼一個宣告支持 `v1.2` 的實現必須實現 `/test`，
即使該實現也宣告支持 `v1.3`。
如果該實現**只**宣告支持 `v1.3`，
那麼它不需要實現 `/test`。

### 5.3 Legacy versioning

在此系統之前，
Matrix 的不同 API 是單獨版本化的。
這在新的規範版本化方法中不再可能。

歷史上，
API 的版本編號為 `rX.Y.Z`，
其中 `X` 大致代表重大變更，
`Y` 代表向後相容的變更，
`Z` 代表 API 的修補或無關緊要的變更。

Matrix 的 `v1.0` 版本於 2019 年 6 月 10 日發布，包含以下 API 版本：

| API/規範 | 版本 |
| --- | --- |
| Client-Server API | r0.5.0 |
| Server-Server API | r0.1.2 |
| Application Service API | r0.1.1 |
| Identity Service API | r0.1.1 |
| Push Gateway API | r0.1.0 |
| Room Version | v5 |

## 6. License

The Matrix specification is licensed under the [Apache
 License, Version
 2.0](http://www.apache.org/licenses/LICENSE-2.0).

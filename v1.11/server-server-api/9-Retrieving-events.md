# Retrieving events

In some circumstances, a homeserver may be missing a particular event or
 information about the room which cannot be easily determined from
 backfilling. These APIs provide homeservers with the option of getting
 events and the state of the room at a given point in the timeline.

在某些情況下，homeserver 可能會缺少特定事件或房間資訊，這些資訊無法通過回填輕易確定。
這些 API 為 homeserver 提供了在時間線中的給定點獲取事件和房間狀態的選項。

<!-- markdownlint-disable -->
<h1>GET <a>/\_matrix/federation/v1/event/{eventId}</a></h1> 
<!-- markdownlint-enable -->

檢索單個事件。

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

path parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `eventId` | `string` | **Required:** 要獲取的事件 ID。 |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 包含請求事件的單個 PDU 的交易。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

Transaction
<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `origin` | `string` | **Required:** 發送此交易的 homeserver 的 `server_name`。 |
| `origin_server_ts` | `integer` | **Required:** 此交易開始時在發起 homeserver 上的 POSIX 毫秒時間戳。 |
| `pdus` | `[PDU]` | **Required:** 單個 PDU。注意，根據房間版本的不同，事件格式也不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

```json
{
  "origin": "matrix.org",
  "origin_server_ts": 1234567890,
  "pdus": [
    {
      "content": {
        "see_room_version_spec": "事件格式會根據房間版本改變。"
      },
      "room_id": "!somewhere:example.org",
      "type": "m.room.minimal_pdu"
    }
  ]
}
```

<!-- markdownlint-disable -->
<h1>GET <a>/\_matrix/federation/v1/state/{roomId}</a> </h1> 
<!-- markdownlint-enable -->

---

檢索房間在給定事件時的狀態快照。

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

path parameter
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要獲取狀態的房間 ID。 |

query parameter
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event_id` | `string` | **Required:** 房間中要檢索狀態的事件 ID。 |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 房間的完全解析狀態，在考慮請求事件引起的任何狀態變更之前。包括事件的授權鏈。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `auth_chain` | `[PDU]` | **Required:** 構成房間狀態的完整授權事件集合，及其授權事件的遞歸集合。注意，根據房間版本的不同，事件格式也不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。 |
| `pdus` | `[PDU]` | **Required:** 在給定事件時房間的完全解析狀態。注意，根據房間版本的不同，事件格式也不同 - 查看 [房間版本規範](/v1.11/rooms) 以獲取精確的事件格式。 |
<!-- markdownlint-enable -->

```json
{
  "auth_chain": [
    {
      "content": {
        "see_room_version_spec": "事件格式會根據房間版本改變。"
      },
      "room_id": "!somewhere:example.org",
      "type": "m.room.minimal_pdu"
    }
  ],
  "pdus": [
    {
      "content": {
        "see_room_version_spec": "事件格式會根據房間版本改變。"
      },
      "room_id": "!somewhere:example.org",
      "type": "m.room.minimal_pdu"
    }
  ]
}
```

<!-- markdownlint-disable -->
<h1>GET <a>/\_matrix/federation/v1/state\_ids/{roomId}</a></h1> 
<!-- markdownlint-enable -->

以事件 ID 的形式檢索房間在給定事件時的狀態快照。這與調用 `/state/{roomId}` 的功能相同，但它只返回事件 ID，而不是完整的事件。

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

path parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要獲取狀態的房間 ID。 |

query parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event_id` | `string` | **Required:** 房間中要檢索狀態的事件 ID。 |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 房間的完全解析狀態，在考慮請求事件引起的任何狀態變更之前。包括事件的授權鏈。 |
| `404` | 給定的 `event_id` 未找到或伺服器不知道該事件的狀態，無法返回有用的資訊。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `auth_chain_ids` | `[string]` | **Required:** 構成房間狀態的完整授權事件集合及其授權事件的遞歸集合。 |
| `pdu_ids` | `[string]` | **Required:** 在給定事件時房間的完全解析狀態。 |

```json
{
  "auth_chain_ids": [
    "$an_event:example.org"
  ],
  "pdu_ids": [
    "$an_event:example.org"
  ]
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3> 
<!-- markdownlint-enable -->

Error
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **Required:** 錯誤碼。 |
| `error` | `string` | 一個可讀的錯誤信息。 |

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Could not find event $Rqnc-F-dvnEYJTyHq_iKxU2bZ1CI92-kuZq3a5lr5Zg"
}
```

<!-- markdownlint-disable -->
<h1>GET<a>/\_matrix/federation/v1/timestamp\_to\_event/{roomId}</a></h1> 
<!-- markdownlint-enable -->

**在 `v1.6` 中新增**

根據 `dir` 參數指定的方向，獲取最接近給定時間戳的事件 ID。

這主要用於處理相應的[客戶端伺服器端點](/v1.11/client-server-api/#get_matrixclientv1roomsroomidtimestamp_to_event)，
當伺服器沒有全部房間歷史，
且沒有合適的事件接近請求的時間戳時。

決定何時向另一個 homeserver 請求更接近事件的啟發式方法由 homeserver 實現決定，
儘管這些啟發式方法可能基於最近的事件是否為前進/後退極限，
這表明它在潛在更接近事件的間隙旁邊。

一個好的啟發式方法是首先嘗試在房間中存在時間最長的伺服器，
因為它們最有可能擁有我們詢問的任何信息。

在本地 homeserver 收到回應後，
應使用 `origin_server_ts` 屬性來確定返回的事件是否比本地找到的最近事件更接近請求的時間戳。
如果是，則應嘗試通過 [`/event/{event_id}`](#get_matrixfederationv1eventeventid) 端點回填該事件，以便客戶端查詢。

| 速率限制: | No |
| --- | --- |
| 需要認證: | Yes |

---

<!-- markdownlint-disable -->
<h2>Request</h2> 
<!-- markdownlint-enable -->

<!-- markdownlint-disable -->
<h2>Request parameters</h2> 
<!-- markdownlint-enable -->

path parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `roomId` | `string` | **Required:** 要搜索的房間 ID。 |

query parameters
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `dir` | `string` | **Required:** 搜索的方向。`f` 表示向前，`b` 表示向後。之一: `[f, b]`。 |
| `ts` | `integer` | **Required:** 要搜索的時間戳，以 Unix 時代以來的毫秒數表示。 |

---

<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->

| 狀態 | 描述 |
| --- | --- |
| `200` | 找到了符合搜索參數的事件。 |
| `404` | 未找到事件。 |

<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `event_id` | `string` | **Required:** 找到的事件 ID。 |
| `origin_server_ts` | `integer` | **Required:** 事件的時間戳，以 Unix 時代以來的毫秒數表示。 |

```json
{
  "event_id": "$143273582443PhrSn:example.org",
  "origin_server_ts": 1432735824653
}
```

<!-- markdownlint-disable -->
<h3>404 response</h3> 
<!-- markdownlint-enable -->

Error
| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `errcode` | `string` | **Required:** 錯誤碼。 |
| `error` | `string` | 一個可讀的錯誤信息。 |

```json
{
  "errcode": "M_NOT_FOUND",
  "error": "Unable to find event from 1432684800000 in forward direction"
}
```

> 這個api主要是查詢某個時間戳之前/之後最接近的事件

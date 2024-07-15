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
<h1>GET</h1> 
<!-- markdownlint-enable -->
/\_matrix/federation/v1/state/{roomId}





---


Retrieves a snapshot of a room’s state at a given event.




| Rate-limited: | No |
| --- | --- |
| Requires authentication: | Yes |




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
| `roomId` | `string` | **Required:** The room ID to get state for. |




query parameters
| Name | Type | Description |
| --- | --- | --- |
| `event_id` | `string` | **Required:** An event ID in the room to retrieve the state at. |




---


<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->




| Status | Description |
| --- | --- |
| `200` | The fully resolved state for the room, prior to considering any state  changes induced by the requested event. Includes the authorization  chain for the events. |


<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->




| Name | Type | Description |
| --- | --- | --- |
| `auth_chain` | `[PDU]` | **Required:** The full set of authorization events that make up the state  of the room, and their authorization events, recursively. Note that  events have a different format depending on the room version -  check the [room version specification](/v1.11/rooms) for precise event formats. |
| `pdus` | `[PDU]` | **Required:** The fully resolved state of the room at the given event. Note  that  events have a different format depending on the room version -  check the [room version specification](/v1.11/rooms) for precise event formats. |




```
{
  "auth_chain": [
    {
      "content": {
        "see_room_version_spec": "The event format changes depending on the room version."
      },
      "room_id": "!somewhere:example.org",
      "type": "m.room.minimal_pdu"
    }
  ],
  "pdus": [
    {
      "content": {
        "see_room_version_spec": "The event format changes depending on the room version."
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
<h1>GET</h1> 
<!-- markdownlint-enable -->
/\_matrix/federation/v1/state\_ids/{roomId}





---


Retrieves a snapshot of a room’s state at a given event, in the form of
 event IDs. This performs the same function as calling `/state/{roomId}`,
 however this returns just the event IDs rather than the full events.




| Rate-limited: | No |
| --- | --- |
| Requires authentication: | Yes |




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
| `roomId` | `string` | **Required:** The room ID to get state for. |




query parameters
| Name | Type | Description |
| --- | --- | --- |
| `event_id` | `string` | **Required:** An event ID in the room to retrieve the state at. |




---


<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->




| Status | Description |
| --- | --- |
| `200` | The fully resolved state for the room, prior to considering any state  changes induced by the requested event. Includes the authorization  chain for the events. |
| `404` | The given `event_id` was not found or the server doesn’t know about the state at  that event to return anything useful. |


<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->




| Name | Type | Description |
| --- | --- | --- |
| `auth_chain_ids` | `[string]` | **Required:** The full set of authorization events that make up the state  of the room, and their authorization events, recursively. |
| `pdu_ids` | `[string]` | **Required:** The fully resolved state of the room at the given event. |




```
{
  "auth_chain_ids": [
    "$an_event:example.org"
  ],
  "pdu_ids": [
    "$an_event:example.org"
  ]
}

```


### 404 response




Error
| Name | Type | Description |
| --- | --- | --- |
| `errcode` | `string` | **Required:** An error code. |
| `error` | `string` | A human-readable error message. |




```
{
  "errcode": "M_NOT_FOUND",
  "error": "Could not find event $Rqnc-F-dvnEYJTyHq_iKxU2bZ1CI92-kuZq3a5lr5Zg"
}

```







<!-- markdownlint-disable -->
<h1>GET</h1> 
<!-- markdownlint-enable -->
/\_matrix/federation/v1/timestamp\_to\_event/{roomId}





---


**Added in `v1.6`**


Get the ID of the event closest to the given timestamp, in the
 direction specified by the `dir` parameter.


This is primarily used when handling the corresponding
 [client-server
 endpoint](/v1.11/client-server-api/#get_matrixclientv1roomsroomidtimestamp_to_event)
 when the server does not have all of the room history, and does not
 have an event suitably close to the requested timestamp.
 


The heuristics for deciding when to ask another homeserver for a closer
 event if your homeserver doesn’t have something close, are left up to
 the homeserver implementation, although the heuristics will probably be
 based on whether the closest event is a forward/backward extremity
 indicating it’s next to a gap of events which are potentially closer.


A good heuristic for which servers to try first is to sort by servers
 that have been in the room the longest because they’re most likely to
 have anything we ask about.


After the local homeserver receives the response, it should determine,
 using the `origin_server_ts` property, whether the returned event is
 closer to the requested timestamp than the closest event that it could
 find locally. If so, it should try to backfill this event via the
 [`/event/{event_id}`](#get_matrixfederationv1eventeventid) endpoint so
 that it is available to for a client to query.
 




| Rate-limited: | No |
| --- | --- |
| Requires authentication: | Yes |




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
| `roomId` | `string` | **Required:** The ID of the room to search |




query parameters
| Name | Type | Description |
| --- | --- | --- |
| `dir` | `string` | **Required:** The direction in which to search. `f` for forwards,  `b` for backwards.One of: `[f, b]`. |
| `ts` | `integer` | **Required:** The timestamp to search from, as given in milliseconds  since the Unix epoch. |




---


<!-- markdownlint-disable -->
<h2>Responses</h2> 
<!-- markdownlint-enable -->




| Status | Description |
| --- | --- |
| `200` | An event was found matching the search parameters. |
| `404` | No event was found. |


<!-- markdownlint-disable -->
<h3>200 response</h3> 
<!-- markdownlint-enable -->




| Name | Type | Description |
| --- | --- | --- |
| `event_id` | `string` | **Required:** The ID of the event found |
| `origin_server_ts` | `integer` | **Required:** The event’s timestamp, in milliseconds since the Unix epoch. |




```
{
  "event_id": "$143273582443PhrSn:example.org",
  "origin_server_ts": 1432735824653
}

```


### 404 response




Error
| Name | Type | Description |
| --- | --- | --- |
| `errcode` | `string` | **Required:** An error code. |
| `error` | `string` | A human-readable error message. |




```
{
  "errcode": "M_NOT_FOUND",
  "error": "Unable to find event from 1432684800000 in forward direction"
}

```

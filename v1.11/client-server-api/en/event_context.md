### Event Context

[![zh-tw](https://img.shields.io/badge/lang-zh--tw-blue.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/zh-tw/event_context.zh-tw.md)

This API returns a number of events that happened just before and after
the specified event. This allows clients to get the context surrounding
an event.

#### Client behaviour

There is a single HTTP API for retrieving event context, documented
below.

{{% http-api spec="client-server" api="event_context" %}}

#### Security considerations

The server must only return results that the user has permission to see.

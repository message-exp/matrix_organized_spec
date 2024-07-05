### OpenID

[![zh-tw](https://img.shields.io/badge/lang-zh--tw-blue.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/zh-tw/openid.zh-tw.md)

This module allows users to verify their identity with a third-party
service. The third-party service does need to be matrix-aware in that it
will need to know to resolve matrix homeservers to exchange the user's
token for identity information.

{{% http-api spec="client-server" api="openid" %}}

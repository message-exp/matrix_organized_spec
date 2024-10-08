### Third-party Networks

[![zh-tw](https://img.shields.io/badge/lang-zh--tw-blue.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/zh-tw/third_party_networks.zh-tw.md)

Application services can provide access to third-party networks via
bridging. This allows Matrix users to communicate with users on other
communication platforms, with messages ferried back and forth by the
application service. A single application service may bridge multiple
third-party networks, and many individual locations within those
networks. A single third-party network location may be bridged to
multiple Matrix rooms.

#### Third-party Lookups

A client may wish to provide a rich interface for joining third-party
locations and connecting with third-party users. Information necessary
for such an interface is provided by third-party lookups.

{{% http-api spec="client-server" api="third_party_lookup" %}}

### 用戶端設定

[![en](https://img.shields.io/badge/lang-en-purple.svg)](https://github.com/message-exp/matrix_organized_spec/tree/main/v1.11/client-server-api/en/account_data.md)

用戶端可以在其主伺服器上儲存其帳戶的自定義設定數據。這些帳戶數據將在不同裝置間同步，並可在特定裝置的多次安裝中保持。用戶只能查看自己帳戶的帳戶數據。

帳戶數據可能是全局的，或限定於特定房間。
這裡沒有繼承機制：如果房間的帳戶數據中缺少某個`type`的數據，不會fallback到相同`type`的全局帳戶數據。

#### 事件

用戶端通過[`/sync`](#get_matrixclientv3sync)響應的`account_data`部分接收帳戶數據作為事件。

這些事件也可以在`/events`響應中接收，或在`/sync`響應的房間的`account_data`部分接收。在`/events`中出現的`m.tag`事件將包含標籤所屬房間的`room_id`。

#### 用戶端行為

{{% http-api spec="client-server" api="account-data" %}}

#### 伺服器行為

對於伺服器管理的事件類型，伺服器必須使用405錯誤響應拒絕設置帳戶數據。
目前，這只包括[`m.fully_read`](#mfully_read)和[`m.push_rules`](#push-rules-events)。這適用於全局和特定房間的帳戶數據。

{{% boxes/note %}}
{{% changed-in v="1.10" %}} `m.push_rules`被添加到拒絕列表中。
{{% /boxes/note %}}

伺服器必須允許用戶端正常讀取上述事件類型。

# Device Management

- **用戶裝置資料的發布及同步**
  - 需要高效且即時地將用戶裝置的資料發布給其他用戶，並保持資料更新。
    - 對於端對端加密，這是可靠性的關鍵，讓用戶知道哪些裝置參與了聊天室。
    - 這也是裝置對裝置訊息傳遞所必須的。
    - 本節內容補充了客戶端-伺服器 API 中的[裝置管理模組](https://matrix.org/docs/spec/client_server/latest#device-management)。

- **Matrix 的裝置同步機制**
  - Matrix 使用自訂的發佈訂閱系統來同步用戶的裝置清單資訊，該資訊透過聯邦協議傳輸。
    - 當伺服器第一次想要查詢遠端用戶的裝置清單時，應透過遠端伺服器的 `/user/keys/query` API 來填充本地快取。
    - 隨後的更新則應透過 `m.device_list_update` EDU 來更新本地快取。
      - 每個 `m.device_list_update` EDU 描述了某一用戶一個裝置的增量變更，應該替換本地伺服器中該裝置的快取資料。
    - 當本地用戶的裝置清單發生變更時，伺服器必須向與該用戶共享房間的所有伺服器發送 `m.device_list_update` EDUs。
      - 如新增或刪除裝置、用戶加入含有其他伺服器的房間、裝置資訊如裝置名稱變更時，必須發送更新。

- **`m.device_list_update` EDU 的發送機制**
  - 伺服器以每個用戶為單位發送一系列 `m.device_list_update` EDU，每個更新都有唯一的 `stream_id`。
    - 更新中包含一個 `prev_id` 欄位，指向前一個 EDU，以便簡化集群伺服器的實現。
      - 集群伺服器可以同時發送多個 EDU，因此 `prev_id` 欄位應包括所有尚未被引用的 `m.device_list_update` EDUs。
      - 若伺服器按順序發送 EDU，則每個 EDU 中只應有一個 `prev_id`。
  - `m.device_list_update` EDU 形成一個簡單的有向非循環圖，展示伺服器在應用更新至本地裝置清單前需接收哪些 EDU。
    - 若伺服器接收到不識別的 `prev_id`，則應調用 `/user/keys/query` API 重新同步裝置清單，並恢復更新流程。

- **`GET /_matrix/federation/v1/user/devices/{userId}` API**
  - **用途**: 獲取用戶的所有裝置資訊。
  - **速率限制**: 無
  - **需要認證**: 是
  
  - **請求參數**
    - **路徑參數**
      - `userId`: 用戶的 ID，必須是接收伺服器的本地用戶。

  - **回應**
    - **狀態碼**
      - `200`: 成功返回用戶裝置清單。
    - **回應內容**
      - `devices`: 用戶的裝置清單，可能為空。
      - `master_key`: 用戶的主跨簽名密鑰。
      - `self_signing_key`: 用戶的自簽名密鑰。
      - `stream_id`: 用於描述裝置清單版本的唯一 ID。
      - `user_id`: 裝置清單所屬用戶的 ID。

  - **裝置資訊結構**
    - **User Device**
      - `device_display_name`: 裝置顯示名稱（可選）。
      - `device_id`: 裝置 ID（必須）。
      - `keys`: 裝置的身份密鑰（必須）。
  
    - **DeviceKeys**
      - `algorithms`: 該裝置支援的加密算法（必須）。
      - `device_id`: 裝置 ID（必須）。
      - `keys`: 公鑰（必須）。
      - `signatures`: 裝置密鑰的簽名（必須）。
      - `user_id`: 裝置所屬用戶的 ID（必須）。

    - **CrossSigningKey**
      - `keys`: 公鑰（必須）。
      - `signatures`: 密鑰的簽名。
      - `usage`: 密鑰用途（必須）。
      - `user_id`: 用戶 ID（必須）。

- **`m.device_list_update` EDU**
  - **新增於 v1.1**  
  - 這是一種 EDU，當用戶新增裝置或裝置獲得新簽名時，伺服器之間會推送該資訊，確保端對端加密能正確針對用戶的當前裝置。

  - **m.device_list_update 結構**
    - `content`: 裝置更新的描述（必須）。
    - `edu_type`: 值為 `m.device_list_update`（必須）。

  - **裝置更新資訊結構**
    - `deleted`: 裝置是否被刪除。
    - `device_display_name`: 裝置的顯示名稱（若無則不返回）。
    - `device_id`: 裝置的 ID（必須）。
    - `keys`: 更新的身份密鑰（可選）。
    - `prev_id`: 先前未被引用的 `m.device_list_update` EDU 的 stream_id。
    - `stream_id`: 該更新的唯一 ID（必須）。
    - `user_id`: 用戶 ID（必須）。

---

用戶裝置的詳細資訊必須有效率地發佈給其他用戶並保持更新。這對於可靠的端對端加密至關重要，因為這樣才能讓用戶知道哪些裝置參與了房間。這也是裝置對裝置消息傳遞所需的功能。本節旨在補充客戶端-伺服器 API 的[裝置管理模組](https://matrix.org/docs/spec/client_server/latest#device-management)。

Matrix 目前使用自訂的發佈/訂閱系統來同步用戶裝置清單的資訊，透過聯邦協議進行傳輸。當伺服器首次需要查詢遠端用戶的裝置清單時，應透過遠端伺服器的 `/user/keys/query` API 填充本地快取。不過，後續的快取更新應通過處理 `m.device_list_update` EDU 來完成。每個新的 `m.device_list_update` EDU 描述了一個用戶某裝置的增量變更，應替換本地伺服器中該裝置清單的現有條目。伺服器必須將 `m.device_list_update` EDU 發送給與本地用戶共享房間的所有伺服器，並且在用戶的裝置清單發生變更時發送（例如新增或刪除裝置，當用戶加入包含其他尚未接收該用戶裝置清單更新的伺服器的房間時，或者裝置資訊如可讀的裝置名稱發生變更時）。

伺服器依據用戶發送 `m.device_list_update` EDU，每個更新都有唯一的 `stream_id`。這些更新也包含一個指向最近期 EDU 的 `prev_id` 欄位。為了簡化集群伺服器的實現，這些伺服器可能同時發送多個 EDU，因此 `prev_id` 欄位應包含所有尚未被引用的 `m.device_list_update` EDU。如果伺服器按順序發送 EDU，則每個 EDU 中只應該有一個 `prev_id`。

這樣會形成一個簡單的有向非循環圖，展示伺服器需要接收哪些 EDU 才能將更新應用到本地的遠端用戶裝置清單中。如果伺服器接收到一個引用了不認識的 `prev_id` 的 EDU，則必須通過調用 `/user/keys/query API` 重新同步其裝置清單，並恢復更新過程。回應會包含一個 `stream_id`，用於與後續的 `m.device_list_update` EDU 進行關聯。

---

### `GET` `/\_matrix/federation/v1/user/devices/{userId}`

取得用戶的所有裝置資訊。

- **速率限制**: 否
- **需要認證**: 是

---

### 請求參數

#### 路徑參數

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `userId` | `string` | **必須**: 用於檢索裝置的用戶 ID，必須是接收主機伺服器的本地用戶。 |

---

### 回應

#### 狀態碼

| 狀態碼 | 描述 |
| --- | --- |
| `200` | 用戶的裝置清單。 |

#### 200 回應

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `devices` | `[[User Device](#get_matrixfederationv1userdevicesuserid_response-200_user-device)]` | **必須**: 用戶的裝置，可能為空。 |
| `master_key` | `[CrossSigningKey](#get_matrixfederationv1userdevicesuserid_response-200_crosssigningkey)` | 用戶的主跨簽名密鑰。 |
| `self_signing_key` | `[CrossSigningKey](#get_matrixfederationv1userdevicesuserid_response-200_crosssigningkey)` | 用戶的自簽名密鑰。 |
| `stream_id` | `integer` | **必須**: 用於描述返回的裝置清單版本的唯一 ID。這與 `m.device_list_update` EDU 中的 `stream_id` 相關聯，以便增量更新返回的裝置清單。 |
| `user_id` | `string` | **必須**: 代表請求裝置的用戶 ID。 |

#### 用戶裝置結構

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `device_display_name` | `string` | 裝置的顯示名稱（可選）。 |
| `device_id` | `string` | **必須**: 裝置 ID。 |
| `keys` | `[DeviceKeys](#get_matrixfederationv1userdevicesuserid_response-200_devicekeys)` | **必須**: 裝置的身份密鑰。 |

#### 裝置密鑰結構

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `algorithms` | `[string]` | **必須**: 裝置支援的加密算法。 |
| `device_id` | `string` | **必須**: 裝置 ID，必須與登入時使用的裝置 ID 匹配。 |
| `keys` | `{string: string}` | **必須**: 公共身份密鑰，屬性名稱應採用 `<algorithm>:<device_id>` 的格式，密鑰應按密鑰算法的規定進行編碼。 |
| `signatures` | `{[User ID](/v1.11/appendices#user-identifiers): {string: string}}` | **必須**: 裝置密鑰的簽名對象。用戶 ID 與 `<algorithm>:<device_id>` 的對應關係圖。簽名過程參見[JSON 簽名](https://matrix.org/docs/spec/client_server/latest#signing-json)。 |
| `user_id` | `string` | **必須**: 裝置所屬用戶的 ID，必須與登入時使用的用戶 ID 匹配。 |

#### 跨簽名密鑰結構

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `keys` | `{string: string}` | **必須**: 公鑰。對象必須只有一個屬性，名稱為 `<algorithm>:<unpadded_base64_public_key>`，值為無填充的 base64 公鑰。 |
| `signatures` | `Signatures` | 密鑰的簽名，簽名過程參見[JSON 簽名](https://matrix.org/docs/spec/client_server/latest#signing-json)。主密鑰可選，其他密鑰必須由用戶的主密鑰簽名。 |
| `usage` | `[string]` | **必須**: 密鑰的用途。 |
| `user_id` | `string` | **必須**: 密鑰所屬的用戶 ID。 |

---

### `m.device_list_update`

---

**新增於 `v1.1`**

一種 EDU，當用戶添加新裝置到其帳號時，伺服器會將詳情推送給彼此，這對於端對端加密正確針對用戶當前裝置組合是必須的。當現有裝置獲得新的跨簽名簽署時，該事件也會被發送。

#### `m.device_list_update` 結構

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `content` | `[Device List Update](#definition-mdevice_list_update_device-list-update)` | **必須**: 裝置詳情的描述。 |
| `edu_type` | `string` | **必須**: 字符串 `m.device_list_update`。可選 `[m.device_list_update]`。 |

#### 裝置更新資訊結構

| 名稱 | 類型 | 描述 |
| --- | --- | --- |
| `deleted` | `boolean` | 當伺服器宣布該裝置已刪除時，值為 `true`。 |
| `device_display_name` | `string` | 該裝置的可讀名稱。若裝置無名稱則缺省。 |
| `device_id` | `string` | **必須**: 裝置的 ID。 |
| `keys` | `[DeviceKeys](#definition-mdevice_list_update_devicekeys)` | 更新的身份密鑰（如果有的話），若裝置無 E2E 密鑰則缺省。 |
| `prev_id` | `[integer]` | 先前未被引用的 `m.device_list_update` EDU 的 stream_id，若接收伺服器不認識其中任何 `

prev_id`，則意味著 EDU 已遺失，伺服器應透過 `/user/keys/query` 獲取裝置清單的快照，以正確解釋後續的 `m.device_list_update` EDU。對於序列中的第一個 EDU，該欄位可能為空。 |
| `stream_id` | `integer` | **必須**: 該更新的唯一 ID，適用於給定的 `user_id`。 |
| `user_id` | `string` | **必須**: 裝置所有者的用戶 ID。 |
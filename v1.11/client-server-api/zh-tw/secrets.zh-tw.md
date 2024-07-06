### 秘密

{{% added-in v="1.1" %}}

用戶端可能有希望提供給其他授權用戶端的秘密資訊，但伺服器不應該能夠看到，所以資訊在通過伺服器時必須加密。這可以通過異步方式完成，在伺服器上存儲加密數據以供稍後檢索，或同步方式，互相發送訊息。

每個秘密都有一個識別符，用戶端在存儲、獲取、請求或共享秘密時使用此識別符來引用秘密。秘密是純字符串；結構化數據可以通過將其編碼為字符串來存儲。

#### 存儲

當秘密存儲在伺服器上時，它們存儲在用戶的[帳戶數據](#client-config)中，使用等同於秘密識別符的事件類型。秘密加密所用的密鑰由同樣存儲在用戶帳戶數據中的數據描述。用戶可以有多個密鑰，允許他們控制用戶端可以訪問哪些秘密集合，這取決於給予它們的密鑰。

##### 密鑰存儲

每個密鑰都有一個ID，密鑰的描述存儲在用戶的帳戶數據中，使用事件類型`m.secret_storage.key.[key ID]`。密鑰的帳戶數據內容將包括一個`algorithm`屬性，指示使用的加密算法，以及一個`name`屬性，這是一個人類可讀的名稱。密鑰描述還可能有一個`passphrase`屬性，用於從用戶輸入的密碼生成密鑰，如[從密碼派生密鑰](#deriving-keys-from-passphrases)中所述。

`KeyDescription`

| 參數       | 類型      | 描述
|------------|-----------|-------------------------------------------------------------------------------------------------------------------------------------|
| name       | string    | 可選。密鑰的名稱。如果未給出，用戶端可能使用通用名稱，如"未命名密鑰"，或如果密鑰被標記為默認密鑰，則使用"默認密鑰"（見下文）。 |
| algorithm  | string    | **必需。** 用於此密鑰的加密算法。目前，僅支持 `m.secret_storage.v1.aes-hmac-sha2`。   |
| passphrase | string    | 請參閱[從密碼派生密鑰](#deriving-keys-from-passphrases)部分以了解此屬性的描述。                   |

其他屬性取決於加密算法，下面會描述。

可以通過將用戶的帳戶數據設置為事件類型`m.secret_storage.default_key`，並將其`key`屬性設為密鑰的ID，來將密鑰標記為"默認"密鑰。默認密鑰將用於加密用戶希望在所有用戶端上可用的所有秘密。除非用戶另有指定，否則用戶端將嘗試使用默認密鑰來解密秘密。

希望通過不支持多個密鑰來為用戶呈現簡化界面的用戶端應使用默認密鑰（如果指定了一個）。如果未指定默認密鑰，用戶端可以表現得就像根本沒有密鑰存在一樣。當這樣的用戶端創建密鑰時，它應該將該密鑰標記為默認密鑰。

`DefaultKey`

| 參數       | 類型      | 描述
|------------|-----------|------------------------------------------|
| key        | string    | **必需。** 默認密鑰的ID。 |


###### `m.secret_storage.v1.aes-hmac-sha2`

為了允許用戶端檢查用戶是否正確輸入了密鑰，用於`m.secret_storage.v1.aes-hmac-sha2`算法的密鑰存儲時會帶有一些額外數據。

存儲密鑰時，用戶端應該：

1.  給定秘密存儲密鑰，通過執行HKDF生成64字節，使用SHA-256作為哈希，32字節的0作為鹽，空字符串作為資訊。前32字節用作AES密鑰，接下來的32字節用作MAC密鑰。

2.  生成16個隨機字節，將第63位設置為0（為了解決AES-CTR實現的差異），並將其用作AES初始化向量（IV）。

3.  使用上面生成的AES密鑰和IV，使用AES-CTR-256加密一條由32字節0組成的訊息。

4.  使用上面生成的MAC密鑰，將原始加密數據通過HMAC-SHA-256。

5.  使用[無填充base64](/appendices/#unpadded-base64)對步驟2中的IV和步驟4中的MAC進行編碼，並將結果分別存儲在`m.secret_storage.key.[key ID]`帳戶數據的`iv`和`mac`屬性中。（步驟3中的密文在通過MAC計算後被丟棄。）

用戶端可以重複此過程來檢查密鑰是否正確：如果密鑰正確，MAC應該匹配。但請注意，這些屬性是**可選的**。如果它們不存在，用戶端必須假設密鑰是有效的。

還要注意，雖然用戶端應該使用上面指定的無填充base64，但一些現有實現使用帶填充的標準[RFC4648兼容base64](https://datatracker.ietf.org/doc/html/rfc4648#section-4)，所以用戶端必須接受這兩種編碼。

因此，使用此算法的`m.secret_storage.key.[key ID]`帳戶數據對象的結構如下：

`AesHmacSha2KeyDescription`

| 參數        | 類型   | 描述                                                                                          |
|-------------|--------|------------------------------------------------------------------------------------------------------|
| name        | string | 可選。密鑰的名稱。                                                                       |
| algorithm   | string | **必需。** 用於此密鑰的加密算法：`m.secret_storage.v1.aes-hmac-sha2`。 |
| passphrase  | object | 請參閱[從密碼派生密鑰](#deriving-keys-from-passphrases)部分以了解此屬性的描述。 |
| iv          | string | 可選。用於驗證檢查的16字節初始化向量，以base64編碼。             |
| mac         | string | 可選。加密32字節0的結果的MAC，以base64編碼。                      |

例如，它可能看起來像這樣：

```json
{
  "name": "m.default",
  "algorithm": "m.secret_storage.v1.aes-hmac-sha2",
  "iv": "random+data",
  "mac": "mac+of+encrypted+zeros"
}
```

##### 秘密存儲

加密數據存儲在用戶的帳戶數據中，使用由使用該數據的功能定義的事件類型。帳戶數據將有一個`encrypted`屬性，這是一個從密鑰ID到對象的映射。給定密鑰的`m.secret_storage.key.[key ID]`數據中的算法定義了如何解釋其他屬性，儘管預期大多數加密方案都會有`ciphertext`和`mac`屬性，其中`ciphertext`屬性是無填充base64編碼的密文，而`mac`用於確保數據的完整性。

`Secret`

| 參數      | 類型             | 描述 |
|-----------|------------------|-------------|
| encrypted | {string: object} | **必需。** 從密鑰ID到加密數據的映射。加密數據的確切格式取決於密鑰算法。請參閱[m.secret_storage.v1.aes-hmac-sha2](#msecret_storagev1aes-hmac-sha2-1)部分中`AesHmacSha2EncryptedData`的定義。 |

示例：

某個秘密使用ID為`key_id_1`和`key_id_2`的密鑰加密：

`org.example.some.secret`:

```
{
  "encrypted": {
    "key_id_1": {
      "ciphertext": "base64+encoded+encrypted+data",
      "mac": "base64+encoded+mac",
      // ... 根據m.secret_storage.key.key_id_1中的algorithm屬性的其他屬性
    },
    "key_id_2": {
      // ...
    }
  }
}
```

而這些密鑰的密鑰描述將是：

`m.secret_storage.key.key_id_1`:

```
{
  "name": "Some key",
  "algorithm": "m.secret_storage.v1.aes-hmac-sha2",
  // ... 根據算法的其他屬性
}
```

`m.secret_storage.key.key_id_2`:

```
{
  "name": "Some other key",
  "algorithm": "m.secret_storage.v1.aes-hmac-sha2",
  // ... 根據算法的其他屬性
}
```

如果`key_id_1`是默認密鑰，那麼我們還有：

`m.secret_storage.default_key`:

```
{
  "key": "key_id_1"
}
```

###### `m.secret_storage.v1.aes-hmac-sha2`

使用`m.secret_storage.v1.aes-hmac-sha2`算法加密的秘密使用AES-CTR-256加密，並使用HMAC-SHA-256進行驗證。秘密的加密方式如下：

1.  給定秘密存儲密鑰，通過執行HKDF生成64字節，使用SHA-256作為哈希，32字節的0作為鹽，以秘密名稱作為資訊。前32字節用作AES密鑰，接下來的32字節用作MAC密鑰。

2.  生成16個隨機字節，將第63位設置為0（為了解決AES-CTR實現的差異），並將其用作AES初始化向量（IV）。

3.  使用上面生成的AES密鑰和IV，使用AES-CTR-256加密數據。

4.  使用上面生成的MAC密鑰，將原始加密數據通過HMAC-SHA-256。

5.  使用[無填充base64](/appendices/#unpadded-base64)對步驟2中的IV、步驟3中的密文和步驟4中的MAC進行編碼，並分別將它們存儲為帳戶數據對象中的`iv`、`ciphertext`和`mac`屬性。

    **注意**：一些現有實現使用帶填充的標準[RFC4648兼容base64](https://datatracker.ietf.org/doc/html/rfc4648#section-4)對這些屬性進行編碼，所以用戶端必須接受這兩種編碼。

因此，使用此算法加密的帳戶數據對象的`encrypted`屬性的結構如下：

`AesHmacSha2EncryptedData`

| 參數       | 類型    | 描述
|------------|---------|------------------------------------------------------------------------|
| iv         | string  |  **必需。** 16字節初始化向量，以base64編碼。  |
| ciphertext | string  |  **必需。** AES-CTR加密的數據，以base64編碼。          |
| mac        | string  |  **必需。** MAC，以base64編碼。                             |


例如，使用此算法加密的數據可能看起來像這樣：

```json
{
  "encrypted": {
      "key_id": {
        "iv": "16+bytes+base64",
        "ciphertext": "base64+encoded+encrypted+data",
        "mac": "base64+encoded+mac"
      }
  }
}
```

##### 密鑰表示

當用戶獲得`m.secret_storage.v1.aes-hmac-sha2`的原始密鑰時，應該將密鑰表示為使用常見[加密密鑰表示](/appendices/#cryptographic-key-representation)的字符串。

##### 從密碼派生密鑰

用戶可能希望使用選定的密碼而不是隨機生成的密鑰。在這種情況下，有關如何從密碼生成密鑰的資訊將存儲在`m.secret_storage.key.[key ID]`帳戶數據的`passphrase`屬性中。`passphrase`屬性有一個`algorithm`屬性，指示如何從密碼生成密鑰。`passphrase`屬性的其他屬性由指定的`algorithm`定義。

目前，唯一定義的算法是`m.pbkdf2`。對於`m.pbkdf2`算法，`passphrase`屬性具有以下屬性：

| 參數       | 類型    | 描述                                                            |
|------------|---------|------------------------------------------------------------------------|
| algorithm  | string  | **必需。** 必須是`m.pbkdf2`                                       |
| salt       | string  | **必需。** PBKDF2中使用的鹽。                                 |
| iterations | integer | **必需。** PBKDF2中使用的迭代次數。               |
| bits       | integer | 可選。為密鑰生成的位數。默認為256。 |

使用PBKDF2生成密鑰，使用SHA-512作為哈希，使用`salt`參數中給出的鹽，以及`iterations`參數中給出的迭代次數。

示例：

```
{

    "passphrase": {
        "algorithm": "m.pbkdf2",
        "salt": "MmMsAlty",
        "iterations": 100000,
        "bits": 256
    },
    ...
}
```

#### 共享

要從其他設備請求秘密，用戶端發送一個`m.secret.request`設備事件，其中`action`設置為`request`，`name`設置為秘密的識別符。願意共享秘密的設備將回覆一個使用olm加密的`m.secret.send`事件。當原始用戶端獲得秘密後，它向除了發送秘密的設備以外的所有設備發送一個`action`設置為`request_cancellation`的`m.secret.request`事件。用戶端應忽略從未向其發送`m.secret.request`事件的設備收到的`m.secret.send`事件。

用戶端必須確保它們只與允許查看秘密的其他設備共享秘密。例如，用戶端應只與用戶自己的已驗證設備共享秘密，並可能提示用戶確認共享秘密。

##### 事件定義

{{% event event="m.secret.request" %}}

{{% event event="m.secret.send" %}}

## 瀏覽器用戶端

- 主伺服器應該回應 pre-flight 請求，並向所有請求提供跨來源資源共用（CORS）標頭
- 伺服器**必須**預期客戶端會透過 OPTION 請求來接近它們，從而允許用戶端探索 CORS 標頭。  
  規範中所有 endpoint 都支援 OPTION 方法，但是使用 OPTION 請求時，伺服器**不得**執行 endpoint 定義的任何邏輯
- 當用戶端向伺服器發出請求時，伺服器應使用該路由的 CORS 標頭進行回應  
  伺服器針對所有請求傳回的建議 CORS 標頭：  
  ```
  Access-Control-Allow-Origin: *
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: X-Requested-With, Content-Type, Authorization
  ```

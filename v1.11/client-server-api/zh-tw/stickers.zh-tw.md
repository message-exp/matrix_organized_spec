### 貼圖

此模組允許用戶在房間或直接訊息會話中發送貼圖。

貼圖是特殊的圖像訊息，顯示時沒有控制元素（例如，沒有"下載"連結，或點擊時的燈箱視圖，這些通常會為 [m.image](#mimage) 事件顯示）。

貼圖旨在在訊息時間線中提供簡單的"反應"事件。Matrix 用戶端應提供某種機制來顯示貼紙的"正文"，例如在懸停時顯示工具提示，或在點擊貼紙圖像時顯示模態框。

#### 事件

貼圖事件在 `/sync` 中作為房間 `timeline` 部分的單個 `m.sticker` 事件接收。

{{% event event="m.sticker" %}}

#### 用戶端行為

支持此訊息類型的用戶端應直接在時間線中顯示事件 URL 中的圖像內容。

應在 `info` 物件中提供縮略圖圖像。這主要是作為不完全支持 `m.sticker` 事件類型的用戶端的後備。在大多數情況下，將縮略圖 URL 設置為與主事件內容相同的 URL 是可以的。

建議貼圖圖像內容的大小應為 512x512 像素或更小。圖像文件的尺寸應為 `info` 物件中指定的預期顯示大小的兩倍，以協助在更高 DPI 螢幕上渲染清晰的圖像。

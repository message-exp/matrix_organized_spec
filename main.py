from bs4 import BeautifulSoup
from markdownify import markdownify as md

# 讀取本地HTML文件

file_name = 'server-server-api.html'
with open(file_name, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 使用BeautifulSoup解析HTML
soup = BeautifulSoup(html_content, 'html.parser')

# 轉換HTML為Markdown，使用ATX風格的標題
markdown_content = md(str(soup), heading_style="ATX")

# 將Markdown內容寫入文件
with open('output_' + file_name + '.md', 'w', encoding='utf-8') as f:
    f.write(markdown_content)

print("HTML文件已成功轉換為Markdown並保存為output.md")

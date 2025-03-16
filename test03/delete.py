import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 配置 Chrome options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--window-size=1920,1080')
chrome_options.add_argument('--lang=zh-CN')

driver = webdriver.Chrome(options=chrome_options)
url = "https://www.baidu.com"

try:
    # 打开网页
    driver.get(url)

    # 等待页面加载
    time.sleep(2)  # 或使用显式等待

    # 获取 HTML 源代码
    html_source = driver.page_source

    # 保存 HTML 源代码到文件
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(html_source)

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    # 关闭浏览器
    driver.quit()

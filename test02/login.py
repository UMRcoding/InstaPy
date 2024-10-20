import pickle

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
import requests
from bs4 import BeautifulSoup
import re
import json
import os
from urllib.parse import urlparse
import pyotp
import pickle
from typing import BinaryIO

def get_totp_token(secret_key):
    totp = pyotp.TOTP(secret_key)
    print(f"当前的 2FA 验证码是: {totp.now()}")
    return totp.now()

def InstaScrap(username, password, url, TOTP_code):
    # 设置Chrome选项
    options = Options()
    # 设置代理服务器
    # host = "210.12.28.122"
    # port = "8120"

    # options.add_argument(f'--proxy-server=http://{host}:{port}')
    options.add_argument('--no-sandbox') # 禁用沙盒模式, 解决权限问题
    options.add_argument('--disable-dev-shm-usage') # 禁用共享文件, 避免共享内存空间不足
    # options.add_argument('--headless') # 启用无头模式
    options.add_experimental_option('excludeSwitches', ['enable-automation']) # 去掉自动化控制的提示，避免反爬机制的检测
    options.add_experimental_option('useAutomationExtension', False) # 禁用Chrome的自动化扩展，进一步减少网站检测到自动化控制的机会

    # 初始化Chrome WebDriver
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()

    # 打开 Instagram 登录页面
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    # 找到用户名和密码输入框
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(username)
    time.sleep(2)
    password_field.send_keys(password)

    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    time.sleep(10)
    login_button.click()
    time.sleep(10)

    # 使用 JavaScript 打开一个新标签页
    # driver.execute_script("window.open()")

    # 切换到新标签页
    # new_tab = driver.window_handles[-1]
    # driver.switch_to.window(new_tab)
    # time.sleep(10)

    # 理论上登录成功，立刻进入提供的 url
    # driver.get(url)

    # 获取当前窗口句柄
    # s_handle = driver.current_window_handle

    # 开始轮询
    while True:
        yurl = driver.current_url
        # 如果有挑战，开始两分钟的计时并持续轮询
        if "challenge" in yurl:
            start_time = time.time()
            while time.time() - start_time < 120:  # 两分钟的倒计时
                yurl = driver.current_url
                if "challenge" in yurl:
                    # 如果仍然是挑战页面，打印剩余时间
                    remaining_time = 120 - int(time.time() - start_time)
                    print(f"账号短期风控，请在两分钟内完成挑战验证，剩余时间: {remaining_time}秒")
                else:
                    # 如果挑战完成，且已成功跳转，退出挑战循环
                    break
                time.sleep(1)

        # 如果登录成功
        if yurl == "https://www.instagram.com/":
            print("登录成功！")
            # 保存会话信息到文件
            cookies = driver.get_cookies()
            with open('session.pkl', 'wb') as file:
                pickle.dump(cookies, file)
            print("会话信息已保存到 session.pkl 文件中。")
            break
        # 每隔一段时间检查一次
        time.sleep(5)

    driver.quit()

    # # 获取初始页面高度
    # initial_height = driver.execute_script("return document.body.scrollHeight")
    #
    # # 创建一个列表来存储页面 HTML 内容
    # soups = []
    #
    # while True:
    #     # 滚动到页面底部
    #     driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    #
    #     # 等待一会儿，允许新内容加载
    #     time.sleep(5)
    #
    #     # 获取页面 HTML
    #     html = driver.page_source
    #
    #     # 使用 BeautifulSoup 解析 HTML
    #     soups.append(BeautifulSoup(html, 'html.parser'))
    #
    #     # 获取当前页面高度
    #     current_height = driver.execute_script("return document.body.scrollHeight")
    #
    #     # 如果页面高度不再变化，退出循环
    #     if current_height == initial_height:
    #         break
    #     # 更新初始高度
    #     initial_height = current_height


    # # 用来存储帖子图片 URL 的列表
    # post_urls = []
    #
    # for soup in soups:
    #     # 查找所有符合特定类的图片元素
    #     elements = soup.find_all('a',
    #                              class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")
    #
    #     # 提取 href 属性并过滤以 "/p/" 或 "/reel/" 开头的 URL
    #     post_urls.extend([element['href'] for element in elements if element['href'].startswith(("/p/", "/reel/"))])
    #
    # # 将列表转换为集合以删除重复项
    # unique_post_urls = list(set(post_urls))
    #
    # print(f"处理前: {len(post_urls)}, 处理后:{len(unique_post_urls)}")
    # print(unique_post_urls)
    #
    # json_list = []
    #
    # # 定义要添加的查询参数
    # query_parameters = "__a=1&__d=dis"
    #
    # # 遍历所有 URL
    # for url in unique_post_urls:
    #     try:
    #         # 获取当前页面 URL
    #         modified_url = "https://www.instagram.com/" + url + "?" + query_parameters
    #         driver.get(modified_url)
    #         time.sleep(5)
    #
    #         # 找到包含 JSON 数据的 <pre> 标签
    #         WebDriverWait(driver, 20).until(
    #             EC.presence_of_element_located((By.XPATH, '//pre'))
    #         )
    #         pre_tag = driver.find_element(By.XPATH, '//pre')
    #
    #         # 从 <pre> 标签中提取 JSON 数据
    #         json_script = pre_tag.text
    #
    #         # 解析 JSON 数据
    #         json_parsed = json.loads(json_script)
    #
    #         # 将解析后的 JSON 添加到列表中
    #         json_list.append(json_parsed)
    #     except (NoSuchElementException, TimeoutException, json.JSONDecodeError) as e:
    #         print(f"处理 URL {url} 时发生错误: {e}")
    #
    # json_list
    # all_urls = []
    # all_dates = []
    #
    # for json_data in json_list:
    #     item_list = json_data.get('items', [])
    #     for item in item_list:
    #         date_taken = item.get('taken_at')
    #         carousel_media = item.get('carousel_media', [])
    #
    #         for media in carousel_media:
    #             image_url = media.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
    #             if image_url:
    #                 all_urls.append(image_url)
    #                 all_dates.append(date_taken)
    #
    #             video_versions = media.get('video_versions', [])
    #             if video_versions:
    #                 video_url = video_versions[0].get('url')
    #                 if video_url:
    #                     all_urls.append(video_url)
    #                     all_dates.append(date_taken)
    #
    #         image_url = item.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
    #         if image_url:
    #             all_urls.append(image_url)
    #             all_dates.append(date_taken)
    #
    #         video_versions = item.get('video_versions', [])
    #         if video_versions:
    #             video_url = video_versions[0].get('url')
    #             if video_url:
    #                 all_urls.append(video_url)
    #                 all_dates.append(date_taken)
    #
    # print(len(all_urls))
    # print(download_dir)
    # os.makedirs(download_dir, exist_ok=True)
    # image_dir = os.path.join(download_dir, "images")
    # video_dir = os.path.join(download_dir, "videos")
    # os.makedirs(image_dir, exist_ok=True)
    # os.makedirs(video_dir, exist_ok=True)
    #
    # image_counter = 1
    # video_counter = 1
    #
    # for index, url in enumerate(all_urls, 0):
    #     response = requests.get(url, stream=True)
    #     url_path = urlparse(url).path
    #     file_extension = os.path.splitext(url_path)[1]
    #
    #     if file_extension.lower() in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
    #         file_name = f"{all_dates[index]}-img-{image_counter}.png"
    #         destination_folder = image_dir
    #         image_counter += 1
    #     elif file_extension.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
    #         file_name = f"{all_dates[index]}-vid-{video_counter}.mp4"
    #         destination_folder = video_dir
    #         video_counter += 1
    #     else:
    #         file_name = f"{all_dates[index]}{file_extension}"
    #         destination_folder = download_dir
    #
    #     file_path = os.path.join(destination_folder, file_name)
    #
    #     with open(file_path, 'wb') as file:
    #         for chunk in response.iter_content(chunk_size=8192):
    #             if chunk:
    #                 file.write(chunk)
    #
    #     print(f"已下载: {file_path}")
    #
    # print(f"已下载 {len(all_urls)} 个文件到 {download_dir}")



username = "ethan1020304@gmail.com"
password = "GAg+pEAjBzjCG"
profile_url = "https://www.instagram.com/williamhanson/"
# "https://www.instagram.com/yifei_cc/"
# download_directory = r"C:\Users\EthanJobs\Desktop\InstaPy\test02\install"
secret_key = "U3CEHS4LAPNSVE2ZIW7H3YJYJ6QDCKBP"


TOTP_code = get_totp_token(secret_key)
InstaScrap(username, password, profile_url, TOTP_code)



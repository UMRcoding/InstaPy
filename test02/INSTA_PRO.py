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
import csv
import tkinter as tk

# 创建主窗口
root = tk.Tk()
root.title("Instagram Profile scraper")
root.geometry("600x500")
# 加载背景图片
background_image = tk.PhotoImage(file="F.png")

# 使用背景图片创建标签
background_label = tk.Label(root, image=background_image)
background_label.place(x=0, y=0, relwidth=1, relheight=1)

def InstaScrap(username,password,url,download_dir):
    driver = webdriver.Chrome()
    driver.maximize_window()

    # 打开 Instagram 登录页面
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(8)
    
    # 找到用户名和密码输入框
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    
    # 输入用户名和密码
    username_field.send_keys(username.get())
    time.sleep(5)
    password_field.send_keys(password.get())
    
    # 点击登录按钮
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    time.sleep(5)
    login_button.click()
    time.sleep(5)
    
    # 使用 JavaScript 打开一个新标签页
    driver.execute_script("window.open()")
    
    # 切换到新标签页
    new_tab = driver.window_handles[-1]  # Get the handle of the last opened tab
    driver.switch_to.window(new_tab)
    time.sleep(10)
    
    # 导航到提供的 URL
    driver.get(url.get())
    
    # 获取初始页面高度
    initial_height = driver.execute_script("return document.body.scrollHeight")
    
    # 创建一个列表来存储页面 HTML 内容
    soups = []
    
    while True:
        # 滚动到页面底部
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
        # 等待一会儿，允许新内容加载
        time.sleep(5)
        
        # 获取页面 HTML
        html = driver.page_source
        
        # 使用 BeautifulSoup 解析 HTML
        soups.append(BeautifulSoup(html, 'html.parser'))
    
        # 获取当前页面高度
        current_height = driver.execute_script("return document.body.scrollHeight")

        # 如果页面高度不再变化，退出循环
        if current_height == initial_height:
            break
        # 更新初始高度
        initial_height = current_height
    

    # 用来存储帖子图片 URL 的列表
    post_urls = []
    
    for soup in soups:
        # 查找所有符合特定类的图片元素
        elements = soup.find_all('a',class_="x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz _a6hd")
    
        # 提取 href 属性并过滤以 "/p/" 或 "/reel/" 开头的 URL
        post_urls.extend([element['href'] for element in elements if element['href'].startswith(("/p/", "/reel/"))])
        
    # 将列表转换为集合以删除重复项
    unique_post_urls = list(set(post_urls))

    print(f"处理前: {len(post_urls)}, 处理后:{len(unique_post_urls)}")
    print(unique_post_urls)
    
    json_list = []
    
    # 定义要添加的查询参数
    query_parameters = "__a=1&__d=dis"
    
    # 遍历所有 URL
    for url in unique_post_urls:
        try:
            # 获取当前页面 URL
            current_url = driver.current_url
    
            # 将查询参数附加到当前 URL
            modified_url = "https://www.instagram.com/" + url + "?" + query_parameters
            # 获取该 URL
            driver.get(modified_url)
            # 等待页面加载完成
            time.sleep(5)
            
            # 找到包含 JSON 数据的 <pre> 标签
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, '//pre'))
            )
            pre_tag = driver.find_element(By.XPATH,'//pre')
    
            # 从 <pre> 标签中提取 JSON 数据
            json_script = pre_tag.text
    
            # 解析 JSON 数据
            json_parsed = json.loads(json_script)
    
            # 将解析后的 JSON 添加到列表中
            json_list.append(json_parsed)
        except (NoSuchElementException, TimeoutException, json.JSONDecodeError) as e:
            print(f"处理 URL {url} 时发生错误: {e}")
    
    json_list
    
    # 用来存储 URL 和对应日期的列表
    all_urls = []
    all_dates = []
    
    # 遍历每个 JSON 数据
    for json_data in json_list:
        
        # 从 'items' 键中提取列表
        item_list = json_data.get('items', [])
        
        # 遍历 'items' 列表中的每个项目
        for item in item_list:
            
            # 提取项目的日期
            date_taken = item.get('taken_at')
    
            # 检查是否存在 'carousel_media'
            carousel_media = item.get('carousel_media', [])
            
            # 遍历 'carousel_media' 列表中的每个媒体
            for media in carousel_media:
                
                # 从媒体中提取图片 URL
                image_url = media.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
                
                if image_url:
                    # 将图片 URL 和对应日期添加到列表中
                    all_urls.append(image_url)
                    all_dates.append(date_taken)
                    print(f"轮播图片已添加")
                    
                # 从媒体中提取视频 URL
                video_versions = media.get('video_versions', [])
                if video_versions:
                    video_url = video_versions[0].get('url')
                    if video_url:
                        
                        # 将视频 URL 和对应日期添加到列表中
                        all_urls.append(video_url)
                        all_dates.append(date_taken)
                        print(f"轮播视频已添加")
    
            # 处理非轮播的单一图片
            image_url = item.get('image_versions2', {}).get('candidates', [{}])[0].get('url')
            if image_url:
                # 将图片 URL 和对应日期添加到列表中
                all_urls.append(image_url)
                all_dates.append(date_taken)
                print(f"单个图片已添加")
    
            # 检查是否存在 'video_versions' 键
            video_versions = item.get('video_versions', [])
            if video_versions:
                video_url = video_versions[0].get('url')
                if video_url:
                    all_urls.append(video_url)
                    all_dates.append(date_taken)
                    print(f"视频已添加")
                    
    # 打印或使用收集到的所有 URL
    print(len(all_urls))
                    
    print(download_dir)
    # 创建目录用于存储下载的文件
    os.makedirs(download_dir, exist_ok=True)
    # 为图片和视频创建子文件夹
    image_dir = os.path.join(download_dir, "images")
    video_dir = os.path.join(download_dir, "videos")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)
    
    # 初始化图片和视频计数器
    image_counter = 1
    video_counter = 1
    
    # 遍历所有的 URL 并下载媒体文件
    for index, url in enumerate(all_urls, 0):
        response = requests.get(url, stream=True)
    
        # 从 URL 中提取文件扩展名
        url_path = urlparse(url).path
        file_extension = os.path.splitext(url_path)[1]

        # 根据 URL 确定文件名
        if file_extension.lower() in {'.jpg', '.jpeg', '.png', '.gif','.webp'}:
            file_name = f"{all_dates[index]}-img-{image_counter}.png"
            destination_folder = image_dir
            image_counter += 1
        elif file_extension.lower() in {'.mp4', '.avi', '.mkv', '.mov'}:
            file_name = f"{all_dates[index]}-vid-{video_counter}.mp4"
            destination_folder = video_dir
            video_counter += 1
        else:
            # 其他文件类型默认保存到主下载目录
            file_name = f"{all_dates[index]}{file_extension}"
            destination_folder = download_dir
    
        # 将文件保存到对应文件夹
        file_path = os.path.join(destination_folder, file_name)
    
        # 将响应内容写入文件
        with open(file_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    
        print(f"已下载: {file_path}")

    # 打印下载完成的文件数和下载目录
    print(f"已下载 {len(all_urls)} 个文件到 {download_dir}")
        

# 创建标签
username_label = tk.Label(root, text="Insta username:", font=("Helvetica", 16), bg='pink')
me_label = tk.Label(root, text="By IMAD BOUZKRAOUI", font=("Helvetica", 13), bg='pink')
password_label = tk.Label(root, text="Password:", font=("Helvetica", 16), bg='pink')
url_label = tk.Label(root, text="Profile url:", font=("Helvetica", 16), bg='pink')
path_label = tk.Label(root, text="Path:", font=("Helvetica", 16), bg='pink')
# 创建输入字段
username_entry = tk.Entry(root, font=("Helvetica", 16))
password_entry = tk.Entry(root, font=("Helvetica", 16), show="*")  # Password entry, characters will be hidden
url_entry = tk.Entry(root, font=("Helvetica", 16))
direc = tk.Entry(root, font=("Helvetica", 16))
# 使用网格布局管理器放置标签和输入字段
username_label.grid(row=0, column=0, padx=(0,390), pady=10, sticky='e')
username_entry.grid(row=1, column=0, padx=(200,50), pady=10,sticky='nsew')
me_label.grid(row=0, column=0, padx=(250,1), pady=10, sticky='ne')
password_label.grid(row=2, column=0, padx=(0,390), pady=10, sticky='e')
password_entry.grid(row=3, column=0, padx=(200,50) ,pady=10,sticky='nsew')
url_label.grid(row=4, column=0, padx=(0,390), pady=10, sticky='e')
url_entry.grid(row=5, column=0, padx=(200,50), pady=10,sticky='nsew')
path_label.grid(row=6, column=0, padx=(0,390), pady=10, sticky='e')
direc.grid(row=7, column=0, padx=(200,50), pady=10,sticky='nsew')

# 显示/隐藏密码的功能
def show_password():
    if password_entry.cget("show") == "*":
        password_entry.config(show="")
        show_password_button.config(text="Hide Password")
    else:
        password_entry.config(show="*")
        show_password_button.config(text="Show Password")

# 创建显示/隐藏密码的按钮
show_password_button = tk.Button(root, text="Show Password", command=show_password)
show_password_button.grid(row=2, columnspan=2, padx=(200,50), pady=10,sticky='se')

# 提交按钮的功能
def submit():
    dirc=direc.get()
    print(dirc)
    InstaScrap(username_entry,password_entry,url_entry,dirc)
    

# 创建提交按钮
submit_button = tk.Button(root, text="START", bg='hotpink', font=("Helvetica", 16), command=submit)
submit_button.grid(row=8, columnspan=2, padx=(200,50), pady=40,sticky='nsew')

# 禁止调整窗口大小
root.resizable(False, False)

# 运行 Tkinter 事件循环
root.mainloop()

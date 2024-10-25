from time import sleep

from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyotp
from threading import Lock
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


app = Flask(__name__)
lock = Lock()

def get_totp_token(secret_key):
    totp = pyotp.TOTP(secret_key)
    print(f"2FA：{totp.now()}")
    return totp.now()

def setup_driver():
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("--incognito")
    options.add_argument("--headless")  # 无头模式
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

def login_facebook(driver, username, password, secret_key):
    print("登录 facebook 网页")
    driver.get("https://www.facebook.com/login")
    time.sleep(10)

    try:
        print("处理 Cookie 弹窗中")
        accept_button = driver.find_element(By.XPATH, "//button[text()='允许所有Cookie']")
        accept_button.click()
        time.sleep(3)
    except Exception as e:
        print("未找到 Cookie 允许按钮，也许不需要确认")

    print("输入用户名和密码中")
    username_field = driver.find_element(By.NAME, "email")
    username_field.send_keys(username)
    time.sleep(1)

    password_field = driver.find_element(By.NAME, "pass")
    password_field.send_keys(password)
    time.sleep(1)

    print("点击第一页登录按钮")
    login_button = driver.find_element(By.ID, "loginbutton")
    login_button.click()
    time.sleep(10)

    page_source = driver.page_source
    if re.search("登录信息有误", page_source):
        print("登录信息有误，请检查用户名或密码是否正确！")
        return None

    if re.search("Check your notifications", page_source):
        print("第二个页面：正在点击 Try another way 按钮")
        # button = driver.find_element(By.CLASS_NAME, "x1lliihq") # 需要 classname 唯一
        button = driver.find_element(By.XPATH, "//span[text()='Try another way']")
        button.click()
        time.sleep(10)

    page_source = driver.page_source
    if re.search("Choose a way to confirm", page_source):
        print("第三个页面：正在点击 Authentication app 复选框")
        radio_button = driver.find_element(By.XPATH, "//input[@type='radio' and @value='1']")
        radio_button.click()
        time.sleep(1)
        print("第三个页面：强制点击 Continue")
        click_element(driver, "//span[text()='Continue']")
        time.sleep(10)

    page_source = driver.page_source
    if re.search("Go to your authentication", page_source):
        print("第四个页面：正在定位输入框并输入2FA")
        wait = WebDriverWait(driver, 5)
        input_box = wait.until(EC.presence_of_element_located((By.ID, ":rh:")))

        # 点击输入框以确保提交按钮激活。
        # driver.execute_script("arguments[0].click();", input_box) # 不稳定，弃用
        # time.sleep(1)

        # 输入2FA代码
        # driver.execute_script("arguments[0].value = arguments[1];", input_box, get_totp_token(secret_key)) # 不稳定，弃用
        input_box.click()
        input_box.send_keys(get_totp_token(secret_key))
        time.sleep(1)

        print("点击 2FA 提交按钮")
        continue_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue']")))
        driver.execute_script("arguments[0].click();", continue_button)
        time.sleep(10)

    # page_source = driver.page_source
    # if re.search("You’re logged in", page_source) or re.search("成功", page_source) or re.search("Trust", page_source):
    print("登录成功，保存当前会话中")

    # 重新强刷 cookie，以验证会话。保证校验点 checkpoint 的通过
    driver.get("https://www.facebook.com")
    time.sleep(10)

    cookies = driver.get_cookies()
    cookies_format = ""
    for ck in cookies:
        if 'expiry' in ck:
            del ck['expiry']
        cookies_format += f"{ck.get('name')}={ck.get('value')}; "
    print(f"转换后的 cookie：{cookies_format}")
    return cookies_format

@app.route("/get_facebook_cookie", methods=["GET"])
def get_facebook_cookie():
    username = request.args.get("username")
    password = request.args.get("password")
    key = request.args.get("key")
    print(f"传入信息，账号: {username}, 密码: {password}, 2FA: {key}")

    with lock:
        driver = setup_driver()
        cookie = login_facebook(driver, username, password, key)
        if cookie:
            return {"cookie": cookie}
        else:
            sleep(10)
            return {"error": "登录失败，看日志去"}

def click_element(driver, xpath, wait_time=10):
    button = None  # 提前初始化 button 变量
    try:
        # 尝试等待元素可点击
        button = WebDriverWait(driver, wait_time).until(
            EC.element_to_be_clickable((By.XPATH, xpath))
        )
        button.click()
    except Exception:
        # 如果等待点击失败，尝试使用 JavaScript 强制点击
        try:
            button = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            # 最后手段：滚动到元素并重试点击
            button = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].scrollIntoView();", button)
            time.sleep(1)  # 短暂等待页面稳定
            try:
                button.click()
            except Exception as final_exception:
                print(f"点击失败: {final_exception}")

# http://localhost:5001/get_facebook_cookie?username=61565527259429&password=12H25WRIFqBU&key=HOVJLITOOOVVFUH4BWE45EUO5FY4P7EF
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

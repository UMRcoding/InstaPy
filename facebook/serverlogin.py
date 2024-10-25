from time import sleep

from flask import Flask, request, jsonify
from prompt_toolkit.contrib.telnet.protocol import EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyotp
from threading import Lock

from selenium.webdriver.support.wait import WebDriverWait

lock = Lock()
app = Flask(__name__)

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
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver

@app.route("/hangdlesubmit", methods=["GET"])
def hangdlesubmit(driver):
    page_source = driver.page_source
    if re.search("Choose a way to confirm", page_source):
        print("点击 Authentication app 复选框")
        radio_button = driver.find_element(By.XPATH, "//input[@type='radio' and @value='1']")
        radio_button.click()
        time.sleep(2)
        print("点击 Continue 按钮")
        time.sleep(30)

        # 滚动到按钮位置
        continue_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Continue']"))
        )
        driver.execute_script("arguments[0].scrollIntoView(true);", continue_button)
        continue_button.click()

        time.sleep(8)

    page_source = driver.page_source
    if re.search("Go to your authentication", page_source):
        print("点击 'Authentication app' 复选框")
        radio_button = driver.find_element(By.XPATH, "//input[@type='radio' and @value='1']")
        radio_button.click()
        time.sleep(2)
        print("点击 'Continue' 按钮")
        time.sleep(30)
        continue_button = driver.find_element(By.XPATH, "//span[text()='Continue']")
        continue_button.click()
        time.sleep(8)

        print("定位输入框并输入2FA")
        input_box = driver.find_element(By.ID, ":rk:")
        input_box.send_keys(get_totp_token)
        time.sleep(1)
        print("点击 '2FA' 提交按钮")
        continue_button = driver.find_element(By.XPATH, "//span[text()='Continue']")
        continue_button.click()
        time.sleep(8)

        page_source = driver.page_source
        if re.search("You’re logged in", page_source):
            print("登录成功，保存当前会话")
            cookies = driver.get_cookies()
            print(f"原始的 cookie：{cookies}")
            cookies_format = ""
            for ck in cookies:
                if 'expiry' in ck:
                    del ck['expiry']
                cookies_format += f"{ck.get('name')}={ck.get('value')}; "
            print(f"转换后的cookie：{cookies_format}")
            return cookies_format


def login_facebook(driver, username, password, secret_key):
    print("登录 facebook 网页")
    driver.get("https://www.facebook.com/login")
    time.sleep(8)

    try:
        print("处理 Cookie 弹窗中")
        accept_button = driver.find_element(By.XPATH, "//button[text()='允许所有Cookie']")
        accept_button.click()
        time.sleep(3)
    except Exception as e:
        print("未找到Cookie允许按钮，可能不需要确认。")

    print("输入用户名和密码中")
    username_field = driver.find_element(By.NAME, "email")
    password_field = driver.find_element(By.NAME, "pass")
    username_field.send_keys(username)
    time.sleep(1)
    password_field.send_keys(password)
    time.sleep(1)
    print("点击登录按钮")
    login_button = driver.find_element(By.ID, "loginbutton")
    time.sleep(1)
    login_button.click()
    time.sleep(10)

    page_source = driver.page_source
    if re.search("登录信息有误", page_source):
        print("登录信息有误，请检查用户名或密码是否正确！")
        return None

    page_source = driver.page_source
    if re.search("Check your notifications", page_source):
        print("点击 Try another way 按钮")
        # button = driver.find_element(By.CLASS_NAME, "x1lliihq") # 需要 classname 唯一
        button = driver.find_element(By.XPATH, "//span[text()='Try another way']")
        button.click()
        time.sleep(8)



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
            return jsonify({"cookie": cookie})
        else:
            sleep(20)
            return jsonify({"error": "登录失败"}), 400

# http://localhost:5001/get_facebook_cookie?username=61565527259429&password=12H25WRIFqBU&key=HOVJLITOOOVVFUH4BWE45EUO5FY4P7EF
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)

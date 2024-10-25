from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyotp
import pickle
from threading import Lock

lock = Lock()

app = Flask(__name__)

def get_totp_token(secret_key):
    totp = pyotp.TOTP(secret_key)
    # print(f"2FA: {totp.now()}")
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

def save_session(driver):
    print("转换和保存cookie中")
    cookies = driver.get_cookies()
    print(f"原始的 cookie：{cookies}")

    cookies_format = ""
    for ck in cookies:
        if 'expiry' in ck:
            del ck['expiry']
        cookies_format += f"{ck.get('name')}={ck.get('value')}; "
    print(f"转换后的cookie：{cookies_format}")

    # token = driver.get_cookie("ct0")["value"]
    # print(f"token-----{token}")
    # return {"cookie": cookies_format, "token": token}

    # with open('session.pkl', 'wb') as file:
    #     pickle.dump(cookies, file)
    # print("会话信息已保存到 session.pkl 文件中。")
    # cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    # return cookie_string


def handle_login_challenges(driver, secret_key):
    while True:
        current_url = driver.current_url
        if "challenge" in current_url:
            print("处理挑战页面")
            time.sleep(1)
        elif "two_factor" in current_url:
            print("处理两步验证!")
            totp_code = get_totp_token(secret_key)
            verification_code_field = driver.find_element(By.NAME, "verificationCode")
            verification_code_field.send_keys(totp_code)
            time.sleep(1)
            confirm_button = driver.find_element(By.XPATH, "//button[@type='button' and contains(text(),'确认')]")
            confirm_button.click()
            time.sleep(10)
        else:
            print("登录成功！")
            return save_session(driver)

def login_instagram(driver, username, password, secret_key):
    print("打开 Instagram 中")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(6)

    print("输入用户名和密码中")
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(username)
    time.sleep(2)

    password_field.send_keys(password)
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    time.sleep(1)

    login_button.click()
    time.sleep(10)

    page_source = driver.page_source
    if re.search("密码有误", page_source):
        print("请检查用户名或密码是否正确")
        return None
    return handle_login_challenges(driver, secret_key)

@app.route("/get_instagram_cookie", methods=["GET"])
def get_instagram_cookie():
    username = request.args.get("username")
    password = request.args.get("password")
    key = request.args.get("key")
    print(f"获取到信息，账号: {username}, 密码: {password}, 2FA Key: {key}")

    with lock:
        driver = setup_driver()
        cookie = login_instagram(driver, username, password, key)
        if cookie:
            return jsonify({"cookie": cookie})
        else:
            return jsonify({"error": "登录失败"}), 400


# http://localhost:5001/get_instagram_cookie?username=your_username&password=your_password&key=your_2fa_key
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)


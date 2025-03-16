from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import re
import pyotp
import pickle
import json

def get_totp_token(secret_key):
    """生成当前的 2FA 验证码"""
    totp = pyotp.TOTP(secret_key)
    print(f"2FA: {totp.now()}")
    return totp.now()

def setup_driver():
    options = Options()
    # 设置代理服务器
    # host = "210.12.28.122"
    # port = "8120"
    # options.add_argument(f'--proxy-server=http://{host}:{port}')
    # options.add_argument('--headless') # 启用无头模式
    options.add_argument('--no-sandbox')  # 禁用沙盒模式, 解决权限问题
    options.add_argument('--disable-dev-shm-usage')  # 禁用共享文件, 避免共享内存空间不足
    options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 去掉自动化控制提示
    options.add_experimental_option('useAutomationExtension', False)  # 禁用Chrome的自动化扩展，进一步减少网站检测到自动化控制的机会
    options.add_argument("--incognito")  # 无痕模式
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    return driver


def handle_login_challenges(driver, twofa_key):
    print("处理登录时的挑战页面或两步验证!")
    # current_url = driver.current_url
    # if "challenge" in current_url:
    #     handle_challenge(driver)

    totp_code = get_totp_token(twofa_key)
    fill_two_factor_code(driver, totp_code)

    page_source = driver.page_source
    if re.search("不再有效", page_source):
        print("验证码不再有效，请重新申请。")
    else:
        print("登录成功！")
        save_session(driver)


def save_session(driver):
    cookies = driver.get_cookies()

    # key=value
    cookie_string = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
    print(f"Cookie: {cookie_string}")

    with open('cookies.txt', 'w', encoding='utf-8') as file:
        file.write(cookie_string)
    print("会话信息已保存到 cookies.txt 文件中。")


def handle_challenge(driver):
    print("处理挑战验证!")
    start_time = time.time()
    while time.time() - start_time < 120:  # 2分钟倒计时
        current_url = driver.current_url
        if "challenge" in current_url:
            remaining_time = 120 - int(time.time() - start_time)
            print(f"账号短期风控，请在两分钟内完成挑战验证，剩余时间: {remaining_time}秒")
        else:
            break
        time.sleep(1)

# https://www.instagram.com/accounts/login/two_factor?next=%2F
def fill_two_factor_code(driver, totp_code):
    verification_code_field = driver.find_element(By.NAME, "verificationCode")
    time.sleep(1)
    # 填写验证码并点击确认按钮
    verification_code_field.send_keys(totp_code)
    time.sleep(1)

    # 点击确认按钮
    confirm_button = driver.find_element(By.XPATH, "//button[@type='button' and contains(text(),'确认')]")
    confirm_button.click()
    time.sleep(6)

def login_instagram(driver, username, password, twofa_key):
    print("登录 Instagram")
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(6)

    # 输入用户名和密码
    username_field = driver.find_element(By.NAME, "username")
    password_field = driver.find_element(By.NAME, "password")
    username_field.send_keys(username)
    time.sleep(1)
    password_field.send_keys(password)

    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    time.sleep(1)
    login_button.click()
    time.sleep(6)

    page_source = driver.page_source
    if re.search("密码有误", page_source):
        print("请检查用户名或密码是否正确")
        return
    handle_login_challenges(driver, twofa_key)

if __name__ == '__main__':
    username = "xi8454774"
    password = "bmLjw0x5_gsd"
    twofa_key = "L56MK747VUF7IFOMJ3RQXAWRTCQVMICD"

    driver = setup_driver()
    login_instagram(driver, username, password, twofa_key)



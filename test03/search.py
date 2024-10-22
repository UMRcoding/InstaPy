import pickle
import time
from regex import regex
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class InstagramSessionManager:
    def __init__(self, session_file, url="https://www.instagram.com"):
        self.session_file = session_file
        self.url = url
        self.driver = None
        self._setup_driver_options()

    def _setup_driver_options(self):
        # 设置Chrome选项
        self.options = Options()
        self.options.add_argument('--no-sandbox')  # 禁用沙盒模式, 解决权限问题
        self.options.add_argument('--disable-dev-shm-usage')  # 禁用共享文件, 避免共享内存空间不足
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 去掉自动化控制的提示，避免反爬机制的检测
        self.options.add_experimental_option('useAutomationExtension', False)  # 禁用Chrome的自动化扩展，减少检测机会


    def start_driver(self):
        # 必须先打开目标网站，才能添加Cookie，避免域名不匹配错误
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get(self.url)
        time.sleep(3)  # 给页面加载留时间

    def load_session_cookies(self):
        # 从文件加载会话信息并添加到浏览器
        try:
            with open(self.session_file, 'rb') as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    if 'domain' in cookie:
                        del cookie['domain']  # 删除domain以避免冲突
                    self.driver.add_cookie(cookie)
            self.driver.refresh()  # 刷新页面以应用Cookies
            time.sleep(5)
        except Exception as e:
            print(f"加载会话cookie失败: {e}")


    def extract_user_info(self):
        # 提取页面中的用户信息
        try:
            page_source = self.driver.page_source # 获取页面源代码，提取必要信息
            if "为你推荐" in page_source:
                print("使用保存的会话信息，已成功登录。")
            elif "无法正常运作" in page_source:
                print("未能成功使用会话信息，请重新登录。")

            if not all(keyword in page_source for keyword in ["\"username\"", "\"appId\"", "\"claim\"", "\"id\":"]):
                time.sleep(4)
                page_source = self.driver.page_source

            user_info = {}
            if any(keyword in page_source for keyword in ["\"username\"", "\"appId\"", "\"claim\"", "\"id\":"]):
                user_info['username'] = regex.search('"username":"(.*?)"', page_source).group(1)
                user_info['appId'] = regex.search('"X-IG-App-ID":"(.*?)"', page_source).group(1)
                user_info['id'] = regex.search('"id":"(.*?)"', page_source).group(1)
                user_info['claim'] = regex.search('"claim":"(.*?)"', page_source).group(1)
                return user_info
            return None
        except Exception as e:
            print(f"提取用户信息失败: {e}")
            return None

    def get_cookie_string(self):
        # 获取Cookie的字符串形式
        try:
            cookies = self.driver.get_cookies()
            cookie_string = "".join(f"{cookie['name']}={cookie['value']};" for cookie in cookies)
            return cookie_string
        except Exception as e:
            print(f"获取cookie字符串失败: {e}")
            return None


    def close_driver(self):
        if self.driver:
            self.driver.quit()
        print("浏览器已关闭")


if __name__ == '__main__':
    # 初始化并启动会话管理器
    session_manager = InstagramSessionManager(session_file='session.pkl')
    session_manager.start_driver()

    # 加载会话cookie并尝试登录
    session_manager.load_session_cookies()

    # 提取用户信息
    user_info = session_manager.extract_user_info()
    if user_info:
        print(f"用户信息: {user_info}")

    # 获取Cookie字符串
    cookie_string = session_manager.get_cookie_string()
    if cookie_string:
        print(f"Cookie字符串: {cookie_string}")

    # 关闭浏览器
    # session_manager.close_driver()


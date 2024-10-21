import pickle
import time
from regex import regex
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# 将Selenium的Cookie转换为requests的cookie字典格式
def convert_cookies_to_dict(cookies):
    cookie_dict = {}
    for cookie in cookies:
        cookie_dict[cookie['name']] = cookie['value']
    return cookie_dict

if __name__ == '__main__':
    options = Options()
    options.add_argument('--no-sandbox')  # 禁用沙盒模式, 解决权限问题
    options.add_argument('--disable-dev-shm-usage')  # 禁用共享文件, 避免共享内存空间不足
    options.add_experimental_option('excludeSwitches', ['enable-automation'])  # 去掉自动化控制的提示，避免反爬机制的检测
    options.add_experimental_option('useAutomationExtension', False)  # 禁用Chrome的自动化扩展，进一步减少网站检测到自动化控制的机会

    driver = webdriver.Chrome(options=options)
    # 必须先打开目标网站，才能添加Cookie，避免域名不匹配错误
    driver.get("https://www.instagram.com")
    time.sleep(3)  # 给页面加载留时间

    # 读取会话信息 (以二进制模式)
    with open('session.pkl', 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            # 确保Cookie不包含'domain'字段, 让Selenium自动匹配当前域
            if 'domain' in cookie:
                del cookie['domain'] # 确保Cookie不包含'domain'字段
            driver.add_cookie(cookie)

    # 刷新页面以应用Cookies
    driver.refresh()
    time.sleep(5)

    # 获取页面源代码，提取必要信息
    re = driver.page_source
    if "无法正常运作" in re:
        print("未能成功使用会话信息，请重新登录。")
    if "为你推荐" in re:
        print("使用保存的会话信息，已成功登录。")

    if not all(keyword in re for keyword in ["\"username\"", "\"appId\"", "\"claim\"", "\"id\":"]):
        time.sleep(4)
        re = driver.page_source

    try:
        # 构建 Cookie 字符串
        cookies = driver.get_cookies()
        strcookie = "".join(f"{cookie['name']}={cookie['value']};" for cookie in cookies)
        print(strcookie)

        # 解析页面源代码，提取用户信息
        user_info = {}
        if any(keyword in re for keyword in ["\"username\"", "\"appId\"", "\"claim\"", "\"id\":"]):
            user_info['username'] = regex.search('"username":"(.*?)"', re).group(1)
            user_info['appId'] = regex.search('"X-IG-App-ID":"(.*?)"', re).group(1)
            user_info['id'] = regex.search('"id":"(.*?)"', re).group(1)
            user_info['claim'] = regex.search('"claim":"(.*?)"', re).group(1)
            print(user_info)

    except Exception as e:
        print(f"error: {e}")
    finally:
        # driver.quit()
        print("结束")

# rur="EAG\05469799464176\0541760971045:01f72c4323bcd704e9413750dbc6059347b4cdb7a95db9c2550bc48247c6f3beb926bfc5";wd=1536x776;ig_nrcb=1;ds_user_id=69799464176;dpr=1.25;ig_did=29ECDE4B-5657-4319-A0DE-F4A364C2C4FA;ig_did=4E03EA67-F917-4FA1-B730-451CF8053485;csrftoken=jHy6QAAo9xkwynzh62Tt5DAj6jJqkdb3;datr=JhUVZ97CSukjFQfbPFCMT6yu;dpr=1.25;csrftoken=jHy6QAAo9xkwynzh62Tt5DAj6jJqkdb3;rur="EAG\05469799464176\0541760970992:01f7084c60d36284cee92b8a9321e7ca1fdfeec9280660c02589b2ad869c5bbd529da513";wd=1036x751;datr=mhUVZ_ALNj-LbsLZ8zdN7nfd;mid=ZxUVKAALAAFH3Y_1OuWDJshOscCH;ds_user_id=69799464176;mid=ZxUVmgALAAFmUsEzr5m4ddIG27_s;sessionid=69799464176%3A5ZvDyrw9t472na%3A22%3AAYcUo2vxfFNX0WejnwhIzKXnWYJ2g74XdFYdOpKsow;
# {'username': 'ethanjobs537', 'appId': '936619743392459', 'id': '69799464176', 'claim': 'hmac.AR2b5ZuB99ubN2-syrJEh-yeVYq4GcwAJ69RhxyLGePEH789'}
# 结束
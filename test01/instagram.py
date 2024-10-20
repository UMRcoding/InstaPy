import execjs  # pip install pyexecjs
import urllib.parse
import requests

# set cookie
HOME_PAGE = "https://www.instagram.com/"
# 请求获取 2FA 验证码，set cookie，400。错误密码 返 200。
CHECK = "https://www.instagram.com/api/v1/web/accounts/login/ajax/"

# 2FA 紧跟着的请求
twoFA01 = "https%3A%2F%2Fwww.instagram.com%2Fajax%2Fbulk-route-definitions%2F&is_from_rle&__req=1h"
twoFA01 = "https://www.instagram.com/accounts/login/?next=https%3A%2F%2Fwww.instagram.com%2Fajax%2Fbulk-route-definitions%2F&is_from_rle&__req=k"

# 2FA 提交失败 400。
LOGIN = "https://www.instagram.com/api/v1/web/account s/login/ajax/two_factor/"
CAPTCHA = ""

Headers = {
    'user-agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
}

# 执行 js 文件
def exec_js_func(js_file, func, *params):
    with open(js_file, 'r', encoding='utf-8') as f:  # 打开JS
        lines = f.readlines()  # 取代码
        js = ''.join(lines)  # 所有JS代码进行拼接
        js_context = execjs.compile(js)  # 运行时上下文编译
        result = js_context.call(func, *params)  # 上下文执行，传入所需参数，再获取结果
        return result


data = {
    "abc" : "123"
}
proxies = {
    "http": "http://127.0.0.1:10809",
    "https": "http://127.0.0.1:10809",
}

payload = urllib.parse.urlencode(data)  # URL 编码
print(exec_js_func('encrypt.js', 'myprint', payload))

class WebRequest:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session() # 保证必须是同一个会话 session
        print("username: {}, password: {}".format(self.username, self.password))

    def get_page(self):
        try:
            requests.get(HOME_PAGE, headers=Headers, proxies=proxies)

            # 定义负载
            check_payload = {
                "enc_password": "%23PWD_INSTAGRAM_BROWSER%3A10%3A1729393763%3AAQRQAHzBGPvXBUBALsjTPJcyyOZYdh2%2FlNurMgAnsv0fz%2FsS3AN7F9OLO90bBZmMt06ABlqWMcfnUWwBCnimQv6a6KuzRgZMYGvEGeClbgF8A6ZP6pW4vAmcBednDbeQLgZrz1X47btZl6XQzOKePQ%3D%3D",
                "caaF2DebugGroup": "0",
                "loginAttemptSubmissionCount": "0",
                "optIntoOneTap": "false",
                "queryParams": "%7B%7D",
                "trustedDeviceRecords": "%7B%7D",
                "username": self.username
            }
            response = self.session.post(CHECK, headers=Headers, proxies=proxies, data=check_payload)
            print(response.status_code)
            print(response.text)
            print(self.session.cookies)
        except Exception as e:
            print("get_page error! ", e)

    # def pre2fa_check(self):
    #     try:
    #         response = self.session.get(PRE2FA, headers=Headers, proxies=proxies)
    #         ret = response.json()
    #         if ret.get('show_2fa'):
    #             print("response.cookies")
    #             res = self.session.put(CAPTCHA, headers=Headers, proxies=proxies)
    #         else:
    #             print("无需验证码")
    #     except Exception as e:
    #         print("pre2fa_check error! ", e)

if __name__ == '__main__':
    WebRequest('111','222').get_page()


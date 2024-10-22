import pickle

# res = ""
# appId = "936619743392459"
# claim = ""
# csrfToken = "q8mseaddBihqanNVYUlV82EZ3LQQKeC9"
# cookie = "mid=Zll2SQAEAAEvXFh-lvoHb_o5V4Ov; ig_did=D1FCCF7A-CD42-41E7-8E45-D1ADA740157C; datr=SXZZZmHf5sGyDVDQXRnb5nYf; ig_nrcb=1; ps_n=1; ps_l=1; csrftoken=q8mseaddBihqanNVYUlV82EZ3LQQKeC9; ds_user_id=68325479805; sessionid=68325479805%3AAWTnuZjZ1Cgsug%3A16%3AAYfDp8lN28OfxRqvp8AU08ppwsDZHsgYoDfv8AkDsw; wd=817x779; rur=\"EAG\\05468325479805\\0541756030493:01f727d1a7f74b73b5d147f8bfb8c4e6e95982982af731acf4e168826b605026796defb2\""

    # Csrftoken = cookie.split("csrftoken=")[1]
    # Csrftoken = Csrftoken.split(";")[0]
    # print(Csrftoken)
    #


# 重新构造Cookie字符串
def construct_cookie_string(cookies):
    cookie_str = ""
    try:
        for cookie in cookies:
            # 过滤掉 domain 信息，保留 name 和 value 组成的键值对
            cookie_str += f"{cookie['name']}={cookie['value']}; "
    except Exception as e:
        print(f"构造cookie字符串时出错: {e}")

    return cookie_str.strip('; ')


if __name__ == '__main__':
    try:
        # 从pkl文件加载会话cookie
        with open("session.pkl", 'rb') as file:
            cookies = pickle.load(file)
            # 打印加载的cookie数据
            for cookie in cookies:
                if 'domain' in cookie:
                    del cookie['domain']  # 删除domain以避免冲突
                # print(cookie)

            # 构造cookie字符串
            cookie_string = construct_cookie_string(cookies)
            print(f"构造的cookie字符串: {cookie_string}")

    except Exception as e:
        print(f"加载会话cookie失败: {e}")



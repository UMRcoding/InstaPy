import pickle

if __name__ == '__main__':
    # 读取会话信息 (以二进制模式)
    with open('session.pkl', 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            # 确保Cookie不包含'domain'字段, 让Selenium自动匹配当前域
            if 'domain' in cookie:
                del cookie['domain']  # 确保Cookie不包含'domain'字段
            print(cookie)



    # 获取Selenium的Cookies并转换为requests格式
    selenium_cookies = driver.get_cookies()
    requests_cookies = convert_cookies_to_dict(selenium_cookies)

    payload = {
        'av': '17841456931372276',
        '__d': 'www',
        '__user': '0',
        '__a': '1',
        '__req': '13',
        '__hs': '20016.HYP:instagram_web_pkg.2.1..0.1',
        'dpr': '1',
        '__ccg': 'MODERATE',
        # '__rev': '1017504446',
        # '__s': 'oqsfga:dx2zxx:ext69q',
        # '__hsi': '7427833527145263373',
        # '__dyn': '7xeUjG1mxu1syUbFp41twpUnwgU7SbzEdF8aUco2qwJxS0k24o1DU2_CwjE1xoswaq0yE462mcw5Mx62G5UswoEcE7O2l0Fwqo31w9a9wtUd8-U2zxe2GewGw9a361qw8Xxm16wUwtEvwww4WCwLyESE7i3vwDwHg2ZwrUdUbGwmk0zU8oC1Iwqo5q3e3zhA6bwIxe6V89F8uwm9EO6UaU3cG8yohw',
        # '__csr': 'h4cgrNsBgD5jdNcOBaDkihikBHfdJfcVtkKVaF_Q_rGHKbGhqUKQp7h9ujBAFeiVay9paim9_jCRAGqya5XzHG4eZ6hby8ryqKbh9eUb9pebWUVbVlUgD89gKblpkuivBGaF28gAzkby4E4-i00jF66C17GGwJwik1rw6km08Owdsgbzm542u787twxwd6060U0C21eCzk08Cw8B7jxaub5o1lpE5W4RG316Vkawm0zO7AhEPjh40E9m2-2u64qt2J90I83iywhES6E4m0MqwZzogCy88p7gedwmo4C0gB3ov2oCzxgl81Yw0MZw0iVE0nnw',
        # '__comet_req': '7',
        'fb_dtsg': 'NAcPn9M8mMLxEG7UFMILgE8ok-n094z8PPXgI82VibCXK7aq7hFw0PQ:17843691127146670:1729427253',
        'jazoest': '25914',
        'lsd': 'rpTu4BHOBC4VjK_EbHRtld',
        '__spin_r': '1017504446',
        '__spin_b': 'trunk',
        '__spin_t': '1729427261',
        'fb_api_caller_class': 'RelayModern',
        'fb_api_req_friendly_name': 'PolarisSearchBoxRefetchableQuery',
        'variables': '{"data":{"context":"blended","include_reel":"true","query":"11","rank_token":"","search_surface":"web_top_search"},"hasQuery":true}',
        # 'server_timestamps': 'true',
        'doc_id': '9153895011291216'
    }
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    url = 'https://www.instagram.com/graphql/query'
    response = requests.post(url, data=payload, headers=headers, cookies=requests_cookies)


    # 检查响应状态码
    if response.status_code == 200:
        print("请求成功")
        print(response)
    else:
        print(f"请求失败，状态码: {response.status_code}")
        print(response)  # 输出详细的错误信息

    # driver.quit()


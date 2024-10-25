import time

import requests
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify
from seleniumbase import SB
from threading import Lock

lock = Lock()


def get_2fa_code(_2fa):
    url = f"https://2fa.show/2fa/{_2fa}"
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.content, "html.parser")
    verification_code = soup.find("h2", id="code").text.strip()
    return verification_code


def get_twitter_cookie_and_token(
        username: str, password: str, _2fa: str, host: str, port: str
):
    # print(username, password, _2fa)

    cookie = ""
    token = ""
    with lock:
        with SB(uc=True, test=True, headless=True, proxy=f"{host}:{port}") as sb:
            url = "https://x.com/i/flow/login"
            sb.uc_open_with_reconnect(url, 3)
            # print(sb.get_page_source())

            # username = "uz3HO90u4IUu7O"
            # password = "3sKfWK9phF6"
            # _2fa = "HQWJLEBPW6R3RWSA"

            sb.type("text", text=f"{username}\n", by="name", timeout=30)
            sb.type("password", text=f"{password}\n", by="name")

            _2fa_code = get_2fa_code(_2fa)
            sb.type("text", text=f"{_2fa_code}\n", by="name")

            time.sleep(3)
            tokens = sb.get_cookies()
            print(tokens)
            tokens = sb.get_cookies()
            cookie = ""
            for token in tokens:
                cookie += f"{token.get('name')}={token.get('value')}; "
            print(f"cookie-----{cookie}")
            token = sb.get_cookie("ct0")["value"]
            print(f"token-----{token}")
    return {"cookie": cookie, "token": token}


app = Flask(__name__)


@app.route("/get_twitter_token", methods=["GET"])
def gettoken():
    username = request.args.get("username")
    password = request.args.get("password")
    host = request.args.get("host")
    key = request.args.get("key")
    port = request.args.get("port")
    print(username, password, host, port, key)
    data = get_twitter_cookie_and_token(username, password, key, host, port)
    return data


@app.route("/tt", methods=["GET"])
def gettoken1():
    username = request.args.get("username")
    password = request.args.get("password")
    host = request.args.get("host")
    key = request.args.get("key")
    port = request.args.get("port")
    print(username, password, host, port, key)
    return {"username": username}

@app.route("/get_page_source", methods=["POST"])
def get_page_source():
    data = request.get_json()
    url = data.get("url")
    cookie_value = data.get("cookieValue")
    print(url, cookie_value)
    page_source = ""
    with SB(headless=True, test=True) as driver:
        print("start open first")
        driver.open(url)
        print("start set cookie")
        for cookie in cookie_value.split(";"):
            key, value = cookie.strip().split("=", 1)
            driver.add_cookie({"name": key, "value": value})
        print("start open second")
        driver.open(url)

        time.sleep(2)
        page_source = driver.get_page_source()
    with open(f"/root/ins_login/logs/{url.split('/')[-1]}", "w", encoding="utf-8") as f:
        f.write(page_source)
    return {"page_source": page_source}


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5500)


import json
import string
import uuid

import requests
from loguru import logger

from geetest_captcha.geetest import GeeTest
from utils.randomUtils import random_string


ANDROID_CAPTCHA_ID = "3f7e2d848ce0cb7e7d019d621e556ce2"


def random_device() -> str:
    alphabet = "ABCDEF" + string.digits
    return random_string(alphabet, 40)


class SMS(object):
    def __init__(self, phone_number: str, device_id: str, sec_code: str) -> None:
        self.phone_number = phone_number
        self.device_id = device_id
        self.sec_code = sec_code

    def send_sms_code(self):
        headers = {
            "Host": "api.kurobbs.com",
            "osversion": "Android",
            "devcode": self.device_id,
            "countrycode": "CN",
            "model": "MIX 2",
            "source": "android",
            "lang": "zh-Hans",
            "version": "2.2.0",
            "versioncode": "2200",
            "channelid": "4",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.11.0",
        }
        url = "https://api.kurobbs.com/user/getSmsCode"
        data = {"mobile": self.phone_number, "geeTestData": self.sec_code}
        response = requests.post(url, headers=headers, data=data)
        return response.json()

    def sdk_login(self, sms_code: str):
        headers = {
            "Host": "api.kurobbs.com",
            "osversion": "Android",
            "devcode": self.device_id,
            "countrycode": "CN",
            "model": "MIX 2",
            "source": "android",
            "lang": "zh-Hans",
            "version": "2.2.0",
            "versioncode": "2200",
            "channelid": "4",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.11.0",
        }
        url = "https://api.kurobbs.com/user/sdkLogin"
        data = {
            "code": sms_code,
            "devCode": self.device_id,
            "gameList": "",
            "mobile": self.phone_number,
        }
        response = requests.post(url=url, data=data, headers=headers)
        json_result = response.json()

        if json_result["code"] != 200:
            error_message = json_result["msg"]
            raise Exception(f"SDK login error, message:{error_message}")

        return json_result["data"]

    def get_login_data(self, token: str):
        headers = {
            "Host": "api.kurobbs.com",
            "devcode": self.device_id,
            "source": "android",
            "version": "2.2.0",
            "versioncode": "2200",
            "token": token,
            "osversion": "Android",
            "countrycode": "CN",
            "model": "MIX 2",
            "lang": "zh-Hans",
            "channelid": "4",
            "content-type": "application/x-www-form-urlencoded",
            "user-agent": "okhttp/3.11.0",
        }
        cookies = {"user_token": token}
        url = "https://api.kurobbs.com/gamer/widget/game3/getData"
        data = {"type": "1", "sizeType": "2"}
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        json_result = response.json()

        if json_result["code"] != 200:
            error_message = json_result["msg"]
            raise Exception(f"SDK login error, message:{error_message}")

        return json_result["data"]


if __name__ == "__main__":
    sec_code = GeeTest(ANDROID_CAPTCHA_ID).get_sec_code()
    random_device_id = random_device()
    phone_number = input("Enter your mobile number: ")
    sms = SMS(phone_number, random_device_id, sec_code)
    status = sms.send_sms_code()
    logger.info(status["msg"])
    sms_code = input("Enter the SMS code: ")
    login_response = sms.sdk_login(sms_code)
    logger.debug(f"Login Response ==> \n{login_response}")
    token = login_response["token"]
    userId = login_response["userId"]
    login_data = sms.get_login_data(token=token)
    random_uuid = uuid.uuid4()
    meta = {
        "token": token,
        "userId": userId,
        "roleId": login_data["roleId"],
        "roleName": login_data["roleName"],
        "serverId": login_data["serverId"],
        "deviceCode": str(random_uuid),
        "distinctId": str(uuid.uuid4()),
    }
    logger.success(f"Get login Info ==> \n{meta}")

    with open("login_data.json", "w") as f:
        json.dump(meta, f, ensure_ascii=False, indent=4)
    logger.success("The info has written in login_data.json")
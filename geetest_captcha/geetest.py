import json
import hashlib
import importlib
from typing import Any

import requests

from geetest_captcha.typings import PowInfo
from geetest_captcha.geetestEnc import get_guid, get_m
from utils.timeUtils import get_current_timestamp


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}


def _convertCallBack(callBackSign: str, context: str):
    return json.loads(context[len(callBackSign) + 1 : len(context) - 1])


class GeeTest(object):
    def __init__(self, captcha_id: str) -> None:
        self.captcha_id = captcha_id
        self.geetest_info_data: dict[str, Any] = {}
        self.callback_sign = f"geetest_{get_current_timestamp()}"

    def send_load(self):
        url = "https://gcaptcha4.geetest.com/load"
        params = {
            "callback": self.callback_sign,
            "captcha_id": self.captcha_id,
            "client_type": "web",
            "pt": "1",
            "lang": "zho",
        }
        response = requests.get(url, headers=headers, params=params)
        geetest_info = _convertCallBack(
            callBackSign=self.callback_sign, context=response.text
        )
        if geetest_info.get("status") != "success":
            raise Exception("Send load error")

        self.geetest_info_data = geetest_info["data"]

    # 所有类型的验证都需要pow
    def get_pow(self) -> PowInfo:
        pow_detail = self.geetest_info_data["pow_detail"]
        hashfunc = pow_detail["hashfunc"]
        pow_info = [
            str(pow_detail["version"]),
            str(pow_detail["bits"]),
            hashfunc,
            pow_detail["datetime"],
            str(self.captcha_id),
            self.geetest_info_data["lot_number"],
            get_guid(),
        ]
        pow_message = "|".join(pow_info)
        hash_obj = hashlib.new(hashfunc)  # 但愿所获hash名字能对应上
        hash_obj.update(pow_message.encode("utf-8"))
        sign = hash_obj.hexdigest()
        return {"message": pow_message, "sign": sign}

    def get_track(self, pow_info: PowInfo) -> dict[str, Any]:
        captcha_type = self.geetest_info_data["captcha_type"]
        try:
            module = importlib.import_module(
                f"geetest_captcha.track_detect.{captcha_type}"
            )
            return module.get_track(self.geetest_info_data, pow_info)
        except ModuleNotFoundError:
            raise Exception(
                f"captcha_type: {captcha_type} is not supported, Please send issue"
            )

    def verify(self, w):
        url = "https://gcaptcha4.geetest.com/verify"
        params = {
            "callback": self.callback_sign,
            "captcha_id": self.captcha_id,
            "client_type": "web",
            "lot_number": self.geetest_info_data["lot_number"],
            "payload": self.geetest_info_data["payload"],
            "process_token": self.geetest_info_data["process_token"],
            "payload_protocol": "1",
            "pt": "1",
            "w": w,
        }
        response = requests.get(url, headers=headers, params=params)
        response_data = _convertCallBack(
            callBackSign=self.callback_sign, context=response.text
        )
        if response_data.get("status") != "success":
            raise Exception("Captcha not pass, please retry or send issue")

        return response_data

    def get_sec_code(self):
        self.send_load()
        pow_info = self.get_pow()
        track = self.get_track(pow_info)
        w = get_m(track)
        verify_result = self.verify(w)
        return json.dumps(verify_result["data"]["seccode"])


if __name__ == "__main__":
    geetest = GeeTest("3f7e2d848ce0cb7e7d019d621e556ce2")
    print(geetest.get_sec_code())

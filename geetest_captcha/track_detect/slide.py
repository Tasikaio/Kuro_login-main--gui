import requests
from typing import Any
from urllib.parse import urljoin

import ddddocr
from geetest_captcha.typings import PowInfo

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}


def get_slide_distance(bgPath: str, slicePath: str) -> int:
    # Get the geetest picture
    geeHost = "https://static.geetest.com/"
    targetUrl = urljoin(geeHost, slicePath)
    bgUrl = urljoin(geeHost, bgPath)
    targetBytes = requests.get(url=targetUrl, headers=headers).content
    bgBytes = requests.get(url=bgUrl, headers=headers).content

    # Identify
    det = ddddocr.DdddOcr(det=False, ocr=False, show_ad=False)
    target = det.slide_match(
        target_bytes=targetBytes, background_bytes=bgBytes, simple_target=True
    )["target"]
    return target[0]


def get_track(geetest_info_data: dict[str, Any], pow_info: PowInfo) -> dict[str, Any]:
    slide_distance = get_slide_distance(
        geetest_info_data["bg"], geetest_info_data["slice"]
    )
    return {
        "setLeft": slide_distance,
        "passtime": 1718,  # 检测不严格
        "userresponse": slide_distance / 1.0059466666666665 + 2,
        "device_id": "",
        "lot_number": geetest_info_data["lot_number"],
        "pow_msg": pow_info["message"],
        "pow_sign": pow_info["sign"],
        "geetest": "captcha",
        "lang": "zh",
        "ep": "123",
        "biht": "1426265548",
        "dRjQ": "738u",
        "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0},
    }

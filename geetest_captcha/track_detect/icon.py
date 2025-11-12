from typing import Any
from urllib.parse import urljoin

import requests

from utils import pathUtils, pictureUtils
from geetest_captcha.typings import PowInfo

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}


def _download(url, name):
    response = requests.get(url=url, headers=headers)
    pngPath = pathUtils.STATIC_PATH.joinpath("pictures").joinpath(f"{name}.png")
    pathUtils.mk_dir(str(pngPath))
    with open(str(pngPath), "wb") as f:
        f.write(response.content)


def download_pic(gee_info_data):
    geeHost = "https://static.geetest.com/"
    target_picture = gee_info_data["imgs"]
    target_picture_url = urljoin(geeHost, target_picture)
    _download(target_picture_url, "target")
    ques_list = gee_info_data["ques"]
    for index in range(len(ques_list)):
        ques = ques_list[index]
        que_url = urljoin(geeHost, ques)
        _download(que_url, f"que_{index}")


def get_track(geetest_info_data: dict[str, Any], pow_info: PowInfo) -> dict[str, Any]:
    download_pic(geetest_info_data)
    pictureUtils.process_picture()
    points = pictureUtils.get_points()
    userresponse = [
        [
            int(round(i[0] / 301.8125 * 100 * 100)),
            int(round(i[1] / 201.296875 * 100 * 100)),
        ]
        for i in points
    ]
    return {
        "passtime": 2098,  # 检测不严格,干脆固定了
        "userresponse": userresponse,
        "device_id": "",
        "lot_number": geetest_info_data["lot_number"],
        "pow_msg": pow_info["message"],
        "pow_sign": pow_info["sign"],
        "geetest": "captcha",
        "lang": "zh",
        "ep": "123",
        "biht": "1426265548",
        "HufC": "hxdr",
        "d229": {"543fa0": "24e1b527"},
        "em": {"ph": 0, "cp": 0, "ek": "11", "wd": 1, "nt": 0, "si": 0, "sc": 0},
    }

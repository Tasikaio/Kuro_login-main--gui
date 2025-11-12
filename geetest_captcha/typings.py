# 存放类型别名
from typing import Literal, TypedDict

"""
CaptchaType:
    slide: 滑块
    match: 消消乐
    word: 文字点选
    icon: 图标点选
    phrase: 字序点选
    winlinze: 五子棋
    nine: 九宫格
    ai: 一键通过
"""

CaptchaType = Literal[
    "slide", "match", "word", "icon", "phrase", "winlinze", "nine", "ai"
]


class PowInfo(TypedDict):
    message: str
    sign: str

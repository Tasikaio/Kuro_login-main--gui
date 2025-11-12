import json
import string

from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad
from Crypto.Cipher import AES, PKCS1_v1_5

from geetest_captcha.constants import RSA_KEY
from utils.randomUtils import random_string


def get_guid():
    alphabet = string.ascii_lowercase + string.digits
    return random_string(alphabet=alphabet, length=16)


def geetest_rsa_enc(plaintext: str) -> str:
    public_key = RSA.construct((RSA_KEY.n, RSA_KEY.e))
    pandding_public_key = PKCS1_v1_5.new(public_key)
    cipher_bytes = pandding_public_key.encrypt(plaintext.encode("utf-8"))
    cipher_hex = cipher_bytes.hex()
    if len(cipher_hex) % 2 != 0:
        cipher_hex = "0" + cipher_hex
    return cipher_hex


def get_m(track: dict):
    key = get_guid()
    rsa_enc = geetest_rsa_enc(plaintext=key)
    iv = "0000000000000000".encode("utf-8")
    plaintext = json.dumps(track).encode("utf-8")
    padding_plaintext = pad(plaintext, 16, "pkcs7")
    aes = AES.new(key=key.encode("utf-8"), mode=AES.MODE_CBC, iv=iv)
    aes_enc = aes.encrypt(padding_plaintext).hex()
    return aes_enc + rsa_enc


if __name__ == "__main__":
    print(get_guid())

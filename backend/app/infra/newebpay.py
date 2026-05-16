"""藍新 MPG 加解密與簽章工具。"""

from __future__ import annotations

import hashlib
import json
from urllib.parse import urlencode

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


class NewebPayCrypto:
    """封裝藍新 MPG 所需的 AES/CBC 與 SHA256 處理。"""

    def __init__(self, hash_key: str, hash_iv: str):
        """建立加解密工具。"""
        self.hash_key = hash_key
        self.hash_iv = hash_iv

    def encrypt_trade_info(self, payload: dict) -> str:
        """將交易資料組成 query string 後做 AES/CBC/PKCS7 加密。"""
        plain = urlencode(payload)
        pad_size = 16 - (len(plain.encode("utf-8")) % 16)
        padded = plain.encode("utf-8") + bytes([pad_size] * pad_size)
        cipher = Cipher(algorithms.AES(self.hash_key.encode("utf-8")), modes.CBC(self.hash_iv.encode("utf-8")))
        encryptor = cipher.encryptor()
        encrypted = encryptor.update(padded) + encryptor.finalize()
        return encrypted.hex()

    def decrypt_trade_info(self, trade_info: str) -> dict:
        """解密 TradeInfo 並轉回 JSON 字典。"""
        cipher = Cipher(algorithms.AES(self.hash_key.encode("utf-8")), modes.CBC(self.hash_iv.encode("utf-8")))
        decryptor = cipher.decryptor()
        decrypted = decryptor.update(bytes.fromhex(trade_info)) + decryptor.finalize()
        pad_size = decrypted[-1]
        plain_text = decrypted[:-pad_size].decode("utf-8")
        try:
            return json.loads(plain_text)
        except json.JSONDecodeError:
            # 回傳參數若不是 JSON，仍維持可追蹤字串。
            return {"raw_text": plain_text}

    def generate_trade_sha(self, trade_info: str) -> str:
        """依藍新規則產生 TradeSha。"""
        source = f"HashKey={self.hash_key}&{trade_info}&HashIV={self.hash_iv}"
        return hashlib.sha256(source.encode("utf-8")).hexdigest().upper()

    def verify_trade_sha(self, trade_info: str, trade_sha: str) -> bool:
        """驗證 TradeSha 是否正確。"""
        expected = self.generate_trade_sha(trade_info=trade_info)
        return expected == trade_sha.upper()


def get_newebpay_gateway_url(newebpay_env: str) -> str:
    """依環境回傳藍新 MPG gateway URL。"""
    if newebpay_env == "production":
        return "https://core.newebpay.com/MPG/mpg_gateway"
    return "https://ccore.newebpay.com/MPG/mpg_gateway"

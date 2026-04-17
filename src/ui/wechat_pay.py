

WECHAT_CONFIG = {
    "APPID": "wx8397f8696b538317",
    "MCHID": "1473426802",
    "API_KEY": "T6m9iK73b0kn9g5v426MKfHQH7X8rKwb",
    "CERT_PATH": "",
    "KEY_PATH": "",
    "NOTIFY_URL": "",
}

import hashlib
import time
import random
import string
import requests
from urllib.parse import urlencode


def is_configured():
    return bool(WECHAT_CONFIG.get("APPID") and WECHAT_CONFIG["APPID"] != "")


def generate_order_id():
    ts = int(time.time())
    rnd = ''.join(random.choices(string.digits, k=6))
    return f"RC{ts}{rnd}"


def generate_sign(params, api_key):
    items = sorted([(k, v) for k, v in params.items() if k != "sign" and v])
    sign_str = "&".join([f"{k}={v}" for k, v in items]) + f"&key={api_key}"
    return hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()


def create_native_order(amount, order_id, description="会员充值"):
    cfg = WECHAT_CONFIG
    if not is_configured():
        raise ValueError("WECHAT_CONFIG未配置")

    url = "https://api.mch.weixin.qq.com/pay/unifiedorder"
    nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    params = {
        "appid": cfg["APPID"],
        "mch_id": cfg["MCHID"],
        "nonce_str": nonce_str,
        "body": description,
        "out_trade_no": order_id,
        "total_fee": int(amount * 100),
        "spbill_create_ip": "127.0.0.1",
        "notify_url": cfg["NOTIFY_URL"],
        "trade_type": "NATIVE",
    }

    params["sign"] = generate_sign(params, cfg["API_KEY"])

    if cfg["CERT_PATH"] and cfg["KEY_PATH"]:
        resp = requests.post(url, data=params, cert=(cfg["CERT_PATH"], cfg["KEY_PATH"]), timeout=10)
    else:
        resp = requests.post(url, data=params, timeout=10)

    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.content)
    result = {c.tag: c.text for c in root}

    if result.get("return_code") == "SUCCESS" and result.get("result_code") == "SUCCESS":
        return result.get("code_url")
    raise Exception(result.get("err_code_des", result.get("return_msg", "未知错误")))


def query_order_status(order_id):
    cfg = WECHAT_CONFIG
    if not is_configured():
        return {"success": False, "trade_state": "NOT_CONFIGURED"}

    url = "https://api.mch.weixin.qq.com/pay/orderquery"
    nonce_str = ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    params = {
        "appid": cfg["APPID"],
        "mch_id": cfg["MCHID"],
        "out_trade_no": order_id,
        "nonce_str": nonce_str,
    }
    params["sign"] = generate_sign(params, cfg["API_KEY"])

    if cfg["CERT_PATH"] and cfg["KEY_PATH"]:
        resp = requests.post(url, data=params, cert=(cfg["CERT_PATH"], cfg["KEY_PATH"]), timeout=10)
    else:
        resp = requests.post(url, data=params, timeout=10)

    import xml.etree.ElementTree as ET
    root = ET.fromstring(resp.content)
    result = {c.tag: c.text for c in root}

    if result.get("return_code") == "SUCCESS":
        trade_state = result.get("trade_state", "UNKNOWN")
        return {
            "success": trade_state == "SUCCESS",
            "trade_state": trade_state,
            "transaction_id": result.get("transaction_id"),
            "total_fee": int(result.get("total_fee") or 0) / 100,
        }
    return {"success": False, "trade_state": "QUERY_FAILED"}


def create_demo_order(amount, order_id):
    return {
        "order_id": order_id,
        "amount": amount,
        "qr_content": f"weixin://wxpay/bizpayurl?pr=DEMO",
        "demo_mode": True,
    }

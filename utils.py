import json
import requests
from model import Log
from decimal import Decimal

_addr_labels = json.load(open("addr_labels.json", "r"))


def truncate_addr(addr: str, offset: int = 4) -> str:
    return addr[: offset + 2] + "..." + addr[-offset:]


def get_addr_entry(addr: str, inplace: bool = True) -> str:
    addr = addr.lower()
    if addr in _addr_labels:
        label: dict = _addr_labels[addr]
        name = label.get("name", "")
        name_str = f"{name}"
        labels = label.get("labels", [])
        label_str = f"{','.join(labels)}" if labels else ""
        if inplace:
            return f"{name_str} [label: {label_str}]"
        else:
            return f"{truncate_addr(addr)} ({name_str}) [label: {label_str}]"
    else:
        return f"{truncate_addr(addr)}"


def get_gas_entry(gas: int) -> str:
    return f"{gas} Gwei"


def get_value_entry(value: int) -> str:
    return f"{value} ETH"


def get_status_entry(status: int) -> str:
    return "Success" if status == 1 else "Fail"


def decode_hex_to_utf8(hex: str) -> str | None:
    try:
        bytes_data = bytes.fromhex(hex.lstrip("0x"))
        decoded_text = bytes_data.decode("utf-8")
        transformed_text = decoded_text.lower()
        return transformed_text
    except UnicodeDecodeError:
        return None


def get_input_entry(input: str) -> str:
    # Check if input is empty
    if input == "0x":
        return ""

    # Try to decode as utf-8
    decoded_text = decode_hex_to_utf8(input)
    if decoded_text:
        return f"Message: {decoded_text}"

    # Try to decode as function signature
    func_sig = input[:10]
    url = "https://www.4byte.directory/api/v1/signatures"
    candidates = requests.get(url, params={"hex_signature": func_sig}).json()
    if not candidates or not candidates.get("result", []):
        return f"Call Method: {func_sig}"
    else:
        results = candidates["result"]
        results = sorted(results, key=lambda x: int(x["id"]))
        return f"Call Method: {func_sig} ({results[0]['text_signature']})"
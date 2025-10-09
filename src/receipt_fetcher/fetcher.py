import json
import ssl
import requests
from pathlib import Path
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.ssl_ import create_urllib3_context

# Load config
CONFIG_PATH = Path(__file__).resolve().parents[2] / "stores.json"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    CONFIGS = json.load(f)


class UnsafeAdapter(HTTPAdapter):
    """
    Adapter that lowers OpenSSL security level and disables hostname verification
    for servers with broken TLS (e.g., Dobronom).
    """
    def __init__(self, *args, **kwargs):
        self._ciphers = "DEFAULT:@SECLEVEL=0"
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, connections, maxsize, block=False, **pool_kwargs):
        ctx = create_urllib3_context()
        try:
            ctx.set_ciphers(self._ciphers)
        except Exception:
            pass
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        pool_kwargs["ssl_context"] = ctx
        return super().init_poolmanager(connections, maxsize, block=block, **pool_kwargs)

    def proxy_manager_for(self, proxy, **proxy_kwargs):
        ctx = create_urllib3_context()
        try:
            ctx.set_ciphers(self._ciphers)
        except Exception:
            pass
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        proxy_kwargs["ssl_context"] = ctx
        return super().proxy_manager_for(proxy, **proxy_kwargs)


def download_receipt_pdf(link_or_guid: str, output_file: str):
    """
    Accepts either a full URL (https://...) or a bare GUID.
    Chooses store config by hostname.
    """
    parsed = urlparse(link_or_guid)
    if parsed.scheme and parsed.netloc:
        guid = link_or_guid.rstrip("/").split("/")[-1]
        host = parsed.hostname
    else:
        # If GUID only, default to first store in config
        guid = link_or_guid
        host = list(CONFIGS.keys())[0]

    cfg = CONFIGS.get(host)
    if not cfg:
        raise ValueError(f"Unsupported host: {host}")

    payload = {
        "CRC": "",
        "Packet": {
            "JWT": "",
            "MethodName": "DiscountClub.GetVirtualReceipt",
            "ServiceNumber": cfg["service"],
            "Data": {"CreditGroupGUID": guid},
        },
    }

    url = cfg["url"]

    try:
        if cfg.get("insecure", False):
            print(f"[!] {host} detected — using relaxed TLS adapter (insecure).")
            session = requests.Session()
            session.mount(url, UnsafeAdapter())
            r = session.post(url, json=payload, timeout=30)
        else:
            r = requests.post(url, json=payload, timeout=30)

        r.raise_for_status()
    # except requests.exceptions.RequestException as e:
        # raise RuntimeError(f"Network error while fetching receipt: {e}") from e
    except: 
        raise

    with open(output_file, "wb") as f:
        f.write(r.content)

import requests

URL = "https://rest.eurotorg.by/10101/Json"

def download_receipt_pdf(guid: str, output_file: str):
    payload = {
        "CRC": "",
        "Packet": {
            "JWT": "",
            "MethodName": "DiscountClub.GetVirtualReceipt",
            "ServiceNumber": "04FA4558-EF8A-4783-A112-036204888532",
            "Data": {"CreditGroupGUID": guid},
        },
    }

    r = requests.post(URL, json=payload)
    r.raise_for_status()

    with open(output_file, "wb") as f:
        f.write(r.content)

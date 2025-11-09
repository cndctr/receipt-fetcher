import sys
import os
from pathlib import Path
from . import fetcher, parser, exporter

FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

def main():
    if len(sys.argv) < 2 or "--help" in sys.argv:
        print("Usage: receipt-fetcher <receipt-link> [output.xlsx]")
        sys.exit(1)

    link = sys.argv[1]

    guid = link.split("/")[-1]

    # The receipt type is determined by the fetcher
    receipt_type = fetcher.download_receipt(link, FILES_DIR / f"{guid}_receipt.dat")
    
    if receipt_type == "pdf":
        pdf_file = FILES_DIR / f"{guid}_receipt.pdf"
        os.replace(FILES_DIR / f"{guid}_receipt.dat", pdf_file)
        print(f"[+] PDF saved as {pdf_file}")
        receipt = parser.parse_receipt(pdf_file)
    elif receipt_type == "html":
        html_file = FILES_DIR / f"{guid}_receipt.html"
        os.replace(FILES_DIR / f"{guid}_receipt.dat", html_file)
        print(f"[+] HTML saved as {html_file}")
        receipt = parser.parse_html_receipt(html_file)
    else:
        print(f"Unsupported receipt type: {receipt_type}")
        sys.exit(1)

    output = sys.argv[2] if len(sys.argv) > 2 else f"{guid}_receipt.xlsx"

    print(f"[+] Parsed {len(receipt['items'])} items")
    print(f"[=]     Total:  {receipt['total']}" )
    print(f"[=] Total alc:  {receipt['total_alc']}" )

    exporter.export_to_excel(receipt, output)
    print(f"[+] Receipt saved to {output}")

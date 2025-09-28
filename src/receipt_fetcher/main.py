import sys
from . import fetcher, parser, exporter

def main():
    if len(sys.argv) < 2:
        print("Usage: receipt-fetcher <receipt-link> [output.xlsx]")
        sys.exit(1)

    link = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "receipt.xlsx"

    guid = link.split("/")[-1]
    pdf_file = "receipt.pdf"

    print(f"[+] Fetching receipt for GUID: {guid}")
    fetcher.download_receipt_pdf(guid, pdf_file)
    print(f"[+] PDF saved as {pdf_file}")

    receipt = parser.parse_receipt(pdf_file)
    print(f"[+] Parsed {len(receipt['items'])} items")

    exporter.export_to_excel(receipt, output)
    print(f"[+] Receipt saved to {output}")

import sys
import os
import argparse
from pathlib import Path
from . import fetcher, parser, exporter

FILES_DIR = Path("files")
FILES_DIR.mkdir(exist_ok=True)

def process_receipt(link: str, output_file: Path | None = None):
    guid = link.split("/")[-1]
    temp_receipt_path = FILES_DIR / f"{guid}_receipt.dat"

    try:
        receipt_type = fetcher.download_receipt(link, temp_receipt_path)
    except Exception as e:
        print(f"[-] Error downloading receipt for {link}: {e}")
        return

    receipt = None
    if receipt_type == "pdf":
        final_receipt_path = FILES_DIR / f"{guid}_receipt.pdf"
        os.replace(temp_receipt_path, final_receipt_path)
        print(f"[+] PDF saved as {final_receipt_path}")
        receipt = parser.parse_receipt(final_receipt_path)
    elif receipt_type == "html":
        final_receipt_path = FILES_DIR / f"{guid}_receipt.html"
        os.replace(temp_receipt_path, final_receipt_path)
        print(f"[+] HTML saved as {final_receipt_path}")
        receipt = parser.parse_html_receipt(final_receipt_path)
    else:
        print(f"[-] Unsupported receipt type: {receipt_type} for link {link}")
        return

    if receipt:
        print(f"[+] Parsed {len(receipt['items'])} items from {link}")
        print(f"[=]     Total:  {receipt['total']}")
        print(f"[=] Total alc:  {receipt['total_alc']}")

        if output_file:
            exporter.export_to_excel(receipt, output_file)
            print(f"[+] Receipt saved to {output_file}")
        else:
            # For console output, just print the receipt dictionary for now
            print(receipt)

def main():
    parser = argparse.ArgumentParser(description="Fetch, parse, and export e-receipts.")
    parser.add_argument("link", nargs="?", help="The full URL of the e-receipt or just the GUID.")
    parser.add_argument("--links", help="Path to a file containing multiple receipt links, one per line.")
    parser.add_argument("output", nargs="?", help="The name of the output Excel file. Defaults to <guid>_receipt.xlsx.")

    args = parser.parse_args()

    if args.links:
        if args.link or args.output:
            print("Error: Cannot use --links with a single link or output file argument.")
            sys.exit(1)
        
        try:
            with open(args.links, 'r') as f:
                links = [line.strip() for line in f if line.strip()]
            
            for link in links:
                print(f"--- Processing link: {link} ---")
                process_receipt(link)
                print(f"--- Finished processing link: {link} ---\n")
        except FileNotFoundError:
            print(f"Error: Links file not found at {args.links}")
            sys.exit(1)
    elif args.link:
        guid = args.link.split("/")[-1]
        output_file = Path(args.output) if args.output else FILES_DIR / f"{guid}_receipt.xlsx"
        process_receipt(args.link, output_file)
    else:
        parser.print_help()
        sys.exit(1)


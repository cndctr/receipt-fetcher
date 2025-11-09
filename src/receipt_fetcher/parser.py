from bs4 import BeautifulSoup
import pdfplumber
import re

price_re = re.compile(r'(?P<price>\d+[\.,]\d+)\s*[xх]\s*(?P<qty>\d+[\.,]?\d*)\s+(?P<subtotal>\d+[\.,]\d+)')

ALCO_KEYWORDS = ["пиво", "водка", "вино", "слабоалко"]

def parse_receipt(pdf_file: str):
    items = []
    total = None
    total_alc = 0.0

    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect total
        if line.startswith("ИТОГО К ОПЛАТЕ"):
            parts = line.split()
            if len(parts) >= 3:
                try:
                    total = float(parts[-1].replace(",", "."))
                except ValueError:
                    pass
            break

        # Detect article (numeric or alphanumeric)
        if re.fullmatch(r"[A-ZА-Я0-9]+", line):
            article = line
            if i + 2 < len(lines):
                name = lines[i + 1]
                price_line = lines[i + 2]
                m = price_re.search(price_line)
                if m:
                    item = {
                        "Article": article,
                        "Name": name,
                        "Price": float(m.group("price").replace(",", ".")),
                        "Quantity": float(m.group("qty").replace(",", ".")),
                        "Subtotal": float(m.group("subtotal").replace(",", "."))
                    }
                    items.append(item)

                    # Alcohol detection (case-insensitive)
                    lower_name = name.lower()
                    if any(key in lower_name for key in ALCO_KEYWORDS):
                        total_alc += item["Subtotal"]

                i += 3
                continue

        i += 1

    return {"items": items, "total": total, "total_alc": total_alc}


def parse_html_receipt(html_file: str):
    items = []
    total = None
    total_alc = 0.0

    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    rows = soup.find_all("tr")
    i = 0
    while i < len(rows):
        row = rows[i]
        cells = row.find_all("td")

        # Item name is in a row with one cell spanning 4 columns
        if len(cells) == 1 and cells[0].get("colspan") == "4":
            name = cells[0].text.strip()
            
            # The next row contains price, quantity, and subtotal
            if i + 1 < len(rows):
                next_row_cells = rows[i+1].find_all("td")
                if len(next_row_cells) == 4:
                    try:
                        price_text = next_row_cells[1].text.strip()
                        qty_text = next_row_cells[2].text.strip().replace("x", "")
                        subtotal_text = next_row_cells[3].text.strip()

                        price = float(price_text.replace(",", "."))
                        qty = float(qty_text.replace(",", "."))
                        subtotal = float(subtotal_text.replace(",", "."))

                        item = {
                            "Article": "",  # HTML receipts may not have an article number
                            "Name": name,
                            "Price": price,
                            "Quantity": qty,
                            "Subtotal": subtotal,
                        }
                        items.append(item)

                        lower_name = name.lower()
                        if any(key in lower_name for key in ALCO_KEYWORDS):
                            total_alc += item["Subtotal"]
                        
                        i += 1 # Skip the next row since we've processed it
                    except (ValueError, IndexError):
                        pass # Ignore rows that don't parse correctly

        # Total is in a row with "ИТОГО К ОПЛАТЕ"
        if "ИТОГО К ОПЛАТE" in row.text:
             total_cells = row.find_all("td")
             if len(total_cells) >= 2:
                 try:
                     total = float(total_cells[-1].text.strip().replace(",", "."))
                 except (ValueError, IndexError):
                     pass

        i += 1

    return {"items": items, "total": total, "total_alc": total_alc}
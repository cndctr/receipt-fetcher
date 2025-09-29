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

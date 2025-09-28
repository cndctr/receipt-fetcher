import pdfplumber
import re

line_re = re.compile(
    r'(?P<price>\d+[\.,]\d+)\s*[xх]\s*(?P<qty>\d+[\.,]?\d*)\s+(?P<subtotal>\d+[\.,]\d+)\s*(?P<name>.+?)(?P<article>[A-ZА-Я0-9]+)$'
)


def parse_receipt(pdf_file: str):
    items = []
    total = None

    with pdfplumber.open(pdf_file) as pdf:
        text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    print("=== DEBUG PDF TEXT ===")
    print(text)
    print("======================")

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        m = line_re.match(line)
        if m:
            items.append({
                "Article": m.group("article"),
                "Name": m.group("name").strip(),
                "Price": float(m.group("price").replace(",", ".")),
                "Quantity": float(m.group("qty").replace(",", ".")),
                "Subtotal": float(m.group("subtotal").replace(",", "."))
            })
            continue

        if "ИТОГО К ОПЛАТЕ" in line:
            total_str = line.split()[0].replace(",", ".")
            try:
                total = float(total_str)
            except ValueError:
                pass

    return {"items": items, "total": total}

import openpyxl

def export_to_excel(receipt: dict, output_file: str):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Receipt"

    headers = ["Article", "Name", "Price", "Quantity", "Subtotal"]
    ws.append(headers)

    for row in receipt["items"]:
        ws.append([
            row["Article"],
            row["Name"],
            row["Price"],
            row["Quantity"],
            row["Subtotal"],
        ])

    # Totals
    if receipt.get("total") is not None:
        ws.append([])
        ws.append(["", "", "", "Total", receipt["total"]])
    if receipt.get("total_alc") is not None:
        ws.append(["", "", "", "Total alc. inc", receipt["total_alc"]])

    wb.save(output_file)

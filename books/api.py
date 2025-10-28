import frappe

@frappe.whitelist()
def send_invoice_email(doc, method):
    if isinstance(doc, str):
        doc = frappe.get_doc("Sales Invoice", doc)

    recipient = None
    if hasattr(doc, "customer") and doc.customer:
        recipient = frappe.db.get_value("Customer", doc.customer, "email")
    elif hasattr(doc, "supplier") and doc.supplier:
        recipient = frappe.db.get_value("Supplier", doc.supplier, "email")

    if not recipient:
        frappe.throw(f"No email found for {doc.doctype} {doc.name}", "Email Not Sent")
        return

    pdf_data = frappe.get_print(doc.doctype, doc.name, print_format="Standard", as_pdf=True)

    subject = f"{doc.doctype} {doc.name} Submitted"
    name_field = getattr(doc, "customer", None) or getattr(doc, "supplier", None)
    message = f"Dear {name_field},<br><br>Your {doc.doctype} <b>{doc.name}</b> has been successfully submitted.<br><br>Regards,<br>{doc.company}"

    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=message,
        attachments=[{"fname": f"{doc.name}.pdf", "fcontent": pdf_data}]
    )

    frappe.msgprint(f"Email sent successfully to {recipient}")

@frappe.whitelist()
def send_payment_email(doc, method):
    if isinstance(doc, str):
        doc = frappe.get_doc("Payment Entry", doc)

    recipient = None
    if doc.party_type == "Customer":
        recipient = frappe.db.get_value("Customer", doc.party, "email")
    elif doc.party_type == "Supplier":
        recipient = frappe.db.get_value("Supplier", doc.party, "email")

    if not recipient:
        frappe.throw(f"No email found for {doc.doctype} {doc.name}", "Payment Email Not Sent")
        return

    pdf_data = frappe.get_print(doc.doctype, doc.name, print_format="Standard", as_pdf=True)

    subject = f"{doc.doctype} {doc.name} Submitted"
    message = f"Dear {doc.party},<br><br>Your {doc.doctype} <b>{doc.name}</b> has been successfully recorded.<br><br>Regards,<br>{doc.company}"

    frappe.sendmail(
        recipients=[recipient],
        subject=subject,
        message=message,
        attachments=[{"fname": f"{doc.name}.pdf", "fcontent": pdf_data}]
    )

    frappe.msgprint(f"Payment email sent successfully to {recipient}")

def update_stock_on_purchase(doc, method=None):
    for item in doc.items:
        sle = frappe.new_doc("Stock Ledger Entry")
        sle.item = item.item
        sle.warehouse = item.warehouse
        sle.posting_date = doc.posting_date
        sle.voucher_type = doc.doctype
        sle.voucher_no = doc.name
        sle.actual_qty = item.qty 
        sle.stock_uom = item.uom
        sle.company = doc.company
        sle.insert(ignore_permissions=True)

        existing = frappe.db.exists("Stock Balance", {"item": item.item, "warehouse": item.warehouse})
        if existing:
            sb = frappe.get_doc("Stock Balance", existing)
            sb.actual_qty += item.qty
            sb.save(ignore_permissions=True)
        else:
            sb = frappe.new_doc("Stock Balance")
            sb.item = item.item
            sb.warehouse = item.warehouse
            sb.actual_qty = item.qty
            sb.stock_uom = item.uom
            sb.company = doc.company
            sb.insert(ignore_permissions=True)


def update_stock_on_sales(doc, method=None):
    for item in doc.items:
        sle = frappe.new_doc("Stock Ledger Entry")
        sle.item = item.item
        sle.warehouse = item.warehouse
        sle.posting_date = doc.posting_date
        sle.voucher_type = doc.doctype
        sle.voucher_no = doc.name
        sle.actual_qty = -1 * item.qty  
        sle.stock_uom = item.uom
        sle.company = doc.company
        sle.insert(ignore_permissions=True)

        existing = frappe.db.exists("Stock Balance", {"item": item.item, "warehouse": item.warehouse})
        if existing:
            sb = frappe.get_doc("Stock Balance", existing)
            sb.actual_qty -= item.qty
            sb.save(ignore_permissions=True)
        else:
            sb = frappe.new_doc("Stock Balance")
            sb.item = item.item
            sb.warehouse = item.warehouse
            sb.actual_qty = -1 * item.qty
            sb.stock_uom = item.uom
            sb.company = doc.company
            sb.insert(ignore_permissions=True)

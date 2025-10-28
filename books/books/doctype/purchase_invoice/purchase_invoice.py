# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.model.document import Document
class PurchaseInvoice(Document):
    def validate(self):
        self.calculate_totals()
    def calculate_totals(self):
        total_qty = 0
        total = 0
        for item in self.items:
            if not item.rate:
                rate = frappe.db.get_value(
                    "Price List",
                    {
                        "item": item.item,
                        "uom": item.uom,
                        "price_list_type": "Purchase",
                        "name": self.price_list,
                    },
                    "rate",
                )
                item.rate = rate or 0

            item.amount = (item.qty or 0) * (item.rate or 0)
            item.discount_amount = (item.amount * (item.discount_percentage or 0)) / 100
            item.net_amount = item.amount - item.discount_amount

            total_qty += item.qty or 0
            total += item.net_amount or 0

        self.total_qty = total_qty
        self.total_amount = total

        if self.discount_type == "Percentage":
            self.discount_amount = (total * (self.discount_value or 0)) / 100
        elif self.discount_type == "Amount":
            self.discount_amount = self.discount_value or 0
        else:
            self.discount_amount = 0

        self.grand_total = total - self.discount_amount
        self.rounded_total = round(self.grand_total, 2)


@frappe.whitelist()
def create_payment_entry(invoice_name):
    invoice = frappe.get_doc("Purchase Invoice", invoice_name)

    total_paid = frappe.db.sql("""
        SELECT SUM(amount_paid)
        FROM `tabPayment Entry`
        WHERE reference_invoice = 'Purchase Invoice' AND reference_name = %s AND docstatus = 1
    """, (invoice.name,), as_dict=True)[0].get("SUM(amount_paid)") or 0

    outstanding = invoice.rounded_total - total_paid
    if outstanding <= 0:
        frappe.throw("This invoice is already fully paid.")

    payment = frappe.new_doc("Payment Entry")
    payment.payment_type = "Pay"
    payment.party_type = "Supplier"
    payment.party = invoice.supplier
    payment.reference_invoice = "Purchase Invoice"
    payment.reference_name = invoice.name
    payment.amount_paid = outstanding
    payment.reference_amount = invoice.rounded_total
    payment.mode_of_payment = "Cash"
    payment.posting_date = frappe.utils.nowdate()
    payment.company = invoice.company
    payment.insert()

    total_paid += payment.amount_paid
    remaining_outstanding = invoice.rounded_total - total_paid
    invoice.db_set("outstanding_amount", remaining_outstanding)
    invoice.db_set("payment_entry", payment.name)

    frappe.msgprint(f"Payment Entry <b>{payment.name}</b> created successfully.")
    return payment.name


@frappe.whitelist()
def create_purchase_return(invoice_name, return_items):
    if isinstance(return_items, str):
        return_items = json.loads(return_items)
    invoice = frappe.get_doc("Purchase Invoice", invoice_name)

    return_invoice = frappe.new_doc("Purchase Invoice")
    return_invoice.is_return = 1
    return_invoice.return_against = invoice.name
    return_invoice.supplier = invoice.supplier
    return_invoice.company = invoice.company
    return_invoice.posting_date = frappe.utils.nowdate()
    return_invoice.price_list = invoice.price_list
    return_invoice.discount_type = invoice.discount_type
    return_invoice.discount_value = invoice.discount_value

    for i in return_items:
        return_invoice.append("items", {
            "item": i["item"],
            "uom": i.get("uom"),
            "qty": -1 * float(i["qty"]),
            "rate": float(i.get("rate", 0)),
            "amount": -1 * float(i.get("amount", 0)),
            "discount_percentage": i.get("discount_percentage") or 0,
            "discount_amount": -1 * float(i.get("discount_amount", 0) or 0),
            "net_amount": -1 * float(i.get("net_amount", 0) or 0),
            "warehouse": i.get("warehouse")
        })

    if hasattr(return_invoice, "calculate_totals"):
        return_invoice.calculate_totals()

    return_invoice.insert(ignore_permissions=True)
    return_invoice.submit()
    return_invoice.db_set("status", "Returned")
    
    frappe.msgprint(f"Purchase Return <b>{return_invoice.name}</b> created successfully.")
    return return_invoice.name
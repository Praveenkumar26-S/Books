# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
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
					{"item":item.item, "uom": item.uom, "price_list_type": "Purchase", "name": self.price_list},
					"rate"
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
        self.rounded_total = round(self.grand_total,2)
     
@frappe.whitelist()
def create_payment_entry(invoice_name):
    invoice = frappe.get_doc("Purchase Invoice", invoice_name)
    payment = frappe.new_doc("Payment Entry")
    payment.payment_type = "Pay"
    payment.party_type = "Supplier"
    payment.party = invoice.supplier
    payment.reference_invoice = "Purchase Invoice"
    payment.reference_name = invoice.name
    payment.amount_paid = invoice.outstanding_amount
    payment.reference_amount = invoice.rounded_total
    payment.mode_of_payment = "Cash"
    payment.posting_date = frappe.utils.nowdate()
    payment.insert()
    invoice.db_set("payment_entry", payment.name)
    return payment.name

@frappe.whitelist()
def create_purchase_return(invoice_name, return_items):
    return_items = frappe.parse_json(return_items)
    pi = frappe.get_doc("Purchase Invoice", invoice_name)

    new_pi = frappe.new_doc("Purchase Invoice")
    new_pi.is_return = 1
    new_pi.return_against = pi.name
    new_pi.supplier = pi.supplier
    new_pi.company = pi.company
    new_pi.items = []

    for i in return_items:
        new_pi.append("items", {
            "item": i["item"],
            "qty": -1 * float(i["qty"]),
            "rate": i["rate"],
            "amount": -1 * float(i["amount"]),
        })

    new_pi.insert(ignore_permissions=True)
    new_pi.submit()
    return new_pi.name

# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class SalesInvoice(Document):
    def validate(self):
        self.calculate_totals()
    def calculate_totals(self):
        total_qty = 0
        total = 0
        for item in self.items:
            if not item.rate:
                rate = frappe.db.get_value(
					"Price List",
					{"item": item.item, "uom": item.uom, "price_list_type": "Sales", "name": self.price_list},
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
        self.rounded_total = round(self.grand_total, 2)
        
@frappe.whitelist()
def create_payment_entry(invoice_name):
    invoice = frappe.get_doc("Sales Invoice", invoice_name)
    payment = frappe.new_doc("Payment Entry")
    payment.payment_type = "Receive"
    payment.party_type = "Customer"
    payment.party = invoice.customer
    payment.reference_type = "Sales Invoice"
    payment.reference_name = invoice.name
    payment.amount_paid = invoice.rounded_total
    payment.reference_amount = invoice.rounded_total
    payment.mode_of_payment = "Cash"
    payment.posting_date = frappe.utils.nowdate()
    payment.insert()
    invoice.db_set("payment_entry", payment.name)
    return payment.name

@frappe.whitelist()
def create_purchase_return(invoice_name, return_items=None):
    import json
    invoice = frappe.get_doc("Purchase Invoice", invoice_name)

    return_invoice = frappe.new_doc("Purchase Invoice")
    return_invoice.supplier = invoice.supplier
    return_invoice.company = invoice.company
    return_invoice.price_list = invoice.price_list
    return_invoice.currency = invoice.currency
    return_invoice.amended_from = invoice.name

    for item in invoice.items:
        qty_to_return = item.qty
        if return_items:
            selected_item = next((i for i in return_items if i["item"] == item.item), None)
            if selected_item:
                qty_to_return = selected_item["qty"]
            else:
                continue
        return_invoice.append("items", {
            "item": item.item,
            "uom": item.uom,
            "qty": qty_to_return,
            "rate": item.rate,
            "discount_percentage": item.discount_percentage or 0
        })

    return_invoice.calculate_totals()
    return_invoice.insert()
    return return_invoice.name

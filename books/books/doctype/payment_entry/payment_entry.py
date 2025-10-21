# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PaymentEntry(Document):
    def validate(self):
        self.set_reference_details()
        self.validate_payment_amount()

    def set_reference_details(self):
        if self.reference_invoice and self.reference_name:
            details = get_reference_details(self.reference_invoice, self.reference_name)
            if details:
                self.party_type = details["party_type"]
                self.party = details["party"]
                self.reference_amount = details["reference_amount"]
                self.outstanding_amount = details["outstanding_amount"]

    def validate_payment_amount(self):
        if not self.amount_paid and self.reference_amount:
            self.amount_paid = self.reference_amount
        paid = float(self.amount_paid or 0)
        reference = float(self.reference_amount or 0)
        if paid > reference:
            frappe.throw("Paid amount cannot exceed reference amount.")

@frappe.whitelist()
def get_reference_details(reference_invoice, reference_name):
    if reference_invoice == "Sales Invoice":
        inv = frappe.get_doc("Sales Invoice", reference_name)
        paid_entries = frappe.db.get_all(
            "Payment Entry",
            filters={"reference_name": reference_name, "docstatus": 1},
            fields=["amount_paid"]
        )
        total_paid = sum(float(pe.amount_paid or 0) for pe in paid_entries)
        outstanding = float(inv.rounded_total or 0) - total_paid

        return {
            "party_type": "Customer",
            "party": inv.customer,
            "reference_amount": inv.rounded_total,
            "outstanding_amount": outstanding,
        }

    elif reference_invoice == "Purchase Invoice":
        inv = frappe.get_doc("Purchase Invoice", reference_name)
        paid_entries = frappe.db.get_all(
            "Payment Entry",
            filters={"reference_name": reference_name, "docstatus": 1},
            fields=["amount_paid"]
        )
        total_paid = sum(float(pe.amount_paid or 0) for pe in paid_entries)
        outstanding = float(inv.rounded_total or 0) - total_paid

        return {
            "party_type": "Supplier",
            "party": inv.supplier,
            "reference_amount": inv.rounded_total,
            "outstanding_amount": outstanding,
        }
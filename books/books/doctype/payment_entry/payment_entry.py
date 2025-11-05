# Copyright (c) 2025, Praveen
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

    def on_submit(self):
        if self.reference_invoice and self.reference_name:
            update_invoice_payment_status(self.reference_invoice, self.reference_name)

    def on_cancel(self):
        if self.reference_invoice and self.reference_name:
            update_invoice_payment_status(self.reference_invoice, self.reference_name)

@frappe.whitelist()
def get_reference_details(reference_invoice, reference_name):
    if reference_invoice == "Sales Invoice":
        inv = frappe.get_doc("Sales Invoice", reference_name)

        paid_entries = frappe.db.get_all(
            "Payment Entry",
            filters={
                "reference_invoice": "Sales Invoice",
                "reference_name": reference_name,
                "docstatus": 1
            },
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
            filters={
                "reference_invoice": "Purchase Invoice",
                "reference_name": reference_name,
                "docstatus": 1
            },
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


def update_invoice_payment_status(reference_invoice, reference_name):
    if reference_invoice == "Sales Invoice":
        inv = frappe.get_doc("Sales Invoice", reference_name)

        paid_entries = frappe.db.get_all(
            "Payment Entry",
            filters={
                "reference_invoice": "Sales Invoice",
                "reference_name": reference_name,
                "docstatus": 1
            },
            fields=["amount_paid"]
        )

        total_paid = sum(float(pe.amount_paid or 0) for pe in paid_entries)
        outstanding = float(inv.rounded_total or 0) - total_paid

        inv.paid_amount = total_paid
        inv.outstanding_amount = outstanding
        inv.payment_status = "Paid" if outstanding <= 0 else "Partially Paid"

        inv.db_update()

        frappe.msgprint(f"Sales Invoice {reference_name} updated — Paid: {total_paid}, Outstanding: {outstanding}")

    elif reference_invoice == "Purchase Invoice":
        inv = frappe.get_doc("Purchase Invoice", reference_name)

        paid_entries = frappe.db.get_all(
            "Payment Entry",
            filters={
                "reference_invoice": "Purchase Invoice",
                "reference_name": reference_name,
                "docstatus": 1
            },
            fields=["amount_paid"]
        )

        total_paid = sum(float(pe.amount_paid or 0) for pe in paid_entries)
        outstanding = float(inv.rounded_total or 0) - total_paid

        inv.paid_amount = total_paid
        inv.outstanding_amount = outstanding
        inv.payment_status = "Paid" if outstanding <= 0 else "Partially Paid"

        inv.db_update()

        frappe.msgprint(f"Purchase Invoice {reference_name} updated — Paid: {total_paid}, Outstanding: {outstanding}")
# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt


import frappe
from frappe import _

def execute(filters=None):
	filters = frappe._dict(filters or {})

	params = {"date": filters.date}
	data = []

	if filters.get("customer"):
		params["customer"] = filters.customer
		data = frappe.db.sql("""
			SELECT
				'Sales Invoice' AS voucher_type,
				si.name AS voucher_no,
				si.posting_date,
				si.customer AS party,
				si.grand_total AS invoice_amount,
				si.outstanding_amount AS outstanding_amount
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1
				AND si.outstanding_amount > 0
				AND si.posting_date <= %(date)s
				AND si.customer = %(customer)s
		""", params, as_dict=True)

	elif filters.get("supplier"):
		params["supplier"] = filters.supplier
		data = frappe.db.sql("""
			SELECT
				'Purchase Invoice' AS voucher_type,
				pi.name AS voucher_no,
				pi.posting_date,
				pi.supplier AS party,
				pi.grand_total AS invoice_amount,
				pi.outstanding_amount AS outstanding_amount
			FROM `tabPurchase Invoice` pi
			WHERE pi.docstatus = 1
				AND pi.outstanding_amount > 0
				AND pi.posting_date <= %(date)s
				AND pi.supplier = %(supplier)s
		""", params, as_dict=True)

	else:
		receivables = frappe.db.sql("""
			SELECT
				'Sales Invoice' AS voucher_type,
				si.name AS voucher_no,
				si.posting_date,
				si.customer AS party,
				si.grand_total AS invoice_amount,
				si.outstanding_amount AS outstanding_amount
			FROM `tabSales Invoice` si
			WHERE si.docstatus = 1
				AND si.outstanding_amount > 0
				AND si.posting_date <= %(date)s
		""", params, as_dict=True)

		payables = frappe.db.sql("""
			SELECT
				'Purchase Invoice' AS voucher_type,
				pi.name AS voucher_no,
				pi.posting_date,
				pi.supplier AS party,
				pi.grand_total AS invoice_amount,
				pi.outstanding_amount AS outstanding_amount
			FROM `tabPurchase Invoice` pi
			WHERE pi.docstatus = 1
				AND pi.outstanding_amount > 0
				AND pi.posting_date <= %(date)s
		""", params, as_dict=True)

		data = receivables + payables


	columns = [
		_("Voucher Type") + "::150",
		_("Voucher No") + ":Dynamic Link/voucher_type:180",
		_("Posting Date") + ":Date:120",
		_("Party") + "::180",
		_("Invoice Amount") + ":Currency:150",
		_("Outstanding Amount") + ":Currency:160",
	]
	return columns, data

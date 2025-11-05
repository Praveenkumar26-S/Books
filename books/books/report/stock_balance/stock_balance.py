# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
	if not filters:
		filters = {}

	till_date = filters.get("till_date")
	item = filters.get("item")
	item_group = filters.get("item_group")


	sql = """
		SELECT
			sle.item AS item_code,
			it.item_name AS item_name,
			it.item_group AS item_group,
			sle.warehouse AS warehouse,
			SUM(sle.actual_qty) AS balance_qty
		FROM `tabStock Ledger Entry` sle
		LEFT JOIN `tabItem` it ON it.name = sle.item
		WHERE sle.posting_date <= %(till_date)s
			AND (%(item)s IS NULL OR sle.item = %(item)s)
			AND (%(item_group)s IS NULL OR it.item_group = %(item_group)s)
		GROUP BY sle.item, sle.warehouse, it.item_group
		HAVING balance_qty != 0
		ORDER BY it.item_group, sle.item
	"""

	data = frappe.db.sql(sql, {
		"till_date": till_date,
		"item": item,
		"item_group": item_group
	}, as_dict=True)

	columns = [
		_("Item Code") + ":Link/Item:150",
		_("Item Name") + ":Data:200",
		_("Item Group") + ":Link/Item Group:150",
		_("Warehouse") + ":Link/Warehouse:150",
		_("Balance Qty") + ":Float:120"
	]

	return columns, data

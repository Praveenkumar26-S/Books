// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt

frappe.query_reports["Item-wise Sales Register"] = {
	"filters": [
		{
			"fieldname": "from_date",
			"fieldtype": "Date",
			"label": "From Date",
			"mandatory": 1
		},
		{
			"fieldname": "to_date",
			"fieldtype": "Date",
			"label": "To Date",
			"mandatory": 1
		},
		{
			"fieldname": "item",
			"fieldtype": "Link",
			"label": "Item",
			"mandatory": 0,
			"options": "Item"
		},
		{	
			"fieldname": "item_group",
			"fieldtype": "Link",
			"label": "Item group",
			"mandatory": 0,
			"options": "Item Group"
		},
		{
			"fieldname": "doc_type",
			"fieldtype": "Select",
			"label": "Doctype",
			"mandatory": 0,
			"options": "Sales Invoice\nPurchase Invoice"
		}
	]
};

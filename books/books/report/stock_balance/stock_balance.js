// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt


frappe.query_reports["Stock Balance"] = {
	filters: [
		{
			fieldname: "till_date",
			label: __("Till Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "item",
			label: __("Item"),
			fieldtype: "Link",
			options: "Item"
		},
		{
			fieldname: "item_group",
			label: __("Item Group"),
			fieldtype: "Link",
			options: "Item Group"
		}
	]
};

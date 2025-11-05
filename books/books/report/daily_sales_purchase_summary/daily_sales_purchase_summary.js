// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt


frappe.query_reports["Daily Sales Purchase Summary"] = {
	filters: [
		{
			fieldname: "date",
			label: __("Date"),
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "based_on",
			label: __("Based On"),
			fieldtype: "Select",
			options: ["Item", "Customer", "Supplier"],
			reqd: 1
		}
	]
};

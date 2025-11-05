// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt

frappe.query_reports["Profit and Loss Report"] = {
	"filters": [
		{
		"fieldname": "company",
		"label": "Company",
		"fieldtype": "Link",
		"options": "Company",
		"reqd": 1
		},
		{
		"fieldname": "year",
		"label": "Year",
		"fieldtype": "Int",
		"default": 2025,
		"reqd": 1
		}
	]
};

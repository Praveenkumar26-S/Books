// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt


frappe.query_reports["Payable Receivable Summary"] = {
	filters: [
		{
			fieldname: "date",
			label: "As on Date",
			fieldtype: "Date",
			reqd: 1		},
		{
			fieldname: "customer",
			label: "Customer",
			fieldtype: "Link",
			options: "Customer",
			depends_on: "eval:!doc.supplier"
		},
		{
			fieldname: "supplier",
			label: "Supplier",
			fieldtype: "Link",
			options: "Supplier",
			depends_on: "eval:!doc.customer"
		}
	]
};

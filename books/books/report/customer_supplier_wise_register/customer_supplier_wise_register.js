// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt

frappe.query_reports["Customer Supplier Wise Register"] = {
	filters: [
		{
			fieldname: "from_date",
			label: "From Date",
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "to_date",
			label: "To Date",
			fieldtype: "Date",
			reqd: 1
		},
		{
			fieldname: "doc_type",
			label: "Doctype",
			fieldtype: "Select",
			options: ["Sales Invoice", "Purchase Invoice"],
			reqd: 1
		},
		{
			fieldname: "customer",
			label: __("Customer"),
			fieldtype: "Link",
			options: "Customer",
			depends_on: "eval:frappe.query_report.get_filter_value('doc_type') == 'Sales Invoice'"
		},
		{
			fieldname: "customer_group",
			label: __("Customer Group"),
			fieldtype: "Link",
			options: "Customer Group",
			depends_on: "eval:frappe.query_report.get_filter_value('doc_type') == 'Sales Invoice'"
		},
		{
			fieldname: "supplier",
			label: __("Supplier"),
			fieldtype: "Link",
			options: "Supplier",
			depends_on: "eval:frappe.query_report.get_filter_value('doc_type') == 'Purchase Invoice'"
		},
		{
			fieldname: "supplier_group",
			label: __("Supplier Group"),
			fieldtype: "Link",
			options: "Supplier Group",
			depends_on: "eval:frappe.query_report.get_filter_value('doc_type') == 'Purchase Invoice'"
		}
	]
};

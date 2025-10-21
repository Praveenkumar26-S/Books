// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Purchase Invoice", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Payment Entry'), function() {
                frappe.call({
                    method: "books.books.doctype.purchase_invoice.purchase_invoice.create_payment_entry",
                    args: { invoice_name: frm.doc.name },
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route("Form", "Payment Entry", r.message);
                        }
                    }
                });
            }, __("Create"));
        }
    }
});

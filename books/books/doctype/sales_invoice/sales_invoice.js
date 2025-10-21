// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Sales Invoice", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on("Sales Invoice", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Payment Entry'), function() {
                frappe.call({
                    method: "books.books.doctype.sales_invoice.sales_invoice.create_payment_entry",
                    args: { invoice_name: frm.doc.name },
                    callback: function(r) {
                        if (r.message) {
                            frappe.set_route("Form", "Payment Entry", r.message);
                        }
                    }
                });
            }, __("Create"));

            frm.add_custom_button(__('Return Items'), function() {
                let dialog = new frappe.ui.Dialog({
                    title: __('Return Items'),
                    fields: [
                        {
                            fieldname: 'return_items',
                            fieldtype: 'Table',
                            label: 'Items to Return',
                            cannot_add_rows: false,
                            in_place_edit: true,
                            fields: [
                                { fieldname: 'item', fieldtype: 'Data', label: 'Item', read_only: 1 },
                                { fieldname: 'description', fieldtype: 'Data', label: 'Description', read_only: 1 },
                                { fieldname: 'uom', fieldtype: 'Data', label: 'UOM', read_only: 1 },
                                { fieldname: 'qty', fieldtype: 'Float', label: 'Return Qty', reqd: 1 },
                                { fieldname: 'rate', fieldtype: 'Currency', label: 'Rate', read_only: 1 },
                                { fieldname: 'amount', fieldtype: 'Currency', label: 'Amount', read_only: 1 }
                            ],
                            data: frm.doc.items.map(i => ({
                                item: i.item,
                                description: i.description || '',
                                uom: i.uom,
                                qty: i.qty,
                                rate: i.rate,
                                amount: i.amount
                            }))
                        }
                    ],
                    primary_action_label: __('Create Return'),
                    primary_action: function(values) {
                        let return_items = values.return_items.map(i => ({
                            item: i.item,
                            qty: i.qty
                        }));

                        frappe.call({
                            method: "books.books.doctype.sales_invoice.sales_invoice.create_sales_return",
                            args: {
                                invoice_name: frm.doc.name,
                                return_items: return_items
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.msgprint(__('Sales Return {0} created', [r.message]));
                                    frappe.set_route('Form','Sales Invoice', r.message);
                                }
                            }
                        });

                        dialog.hide();
                    }
                });

                dialog.show();
            }, __("Create"));
        }
    }
});


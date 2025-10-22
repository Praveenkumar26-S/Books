// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt


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

            frm.add_custom_button(__('Return Items'), function() {
                let dialog = new frappe.ui.Dialog({
                    title: __('Return Purchase Items'),
                    size: 'large',
                    fields: [
                        {
                            fieldname: 'purchase_items',
                            fieldtype: 'Table',
                            label: 'Items to Return',
                            cannot_add_rows: true,
                            in_place_edit: true,
                            fields: [
                                { fieldname: 'item', fieldtype: 'Data', label: 'Item', read_only: 1, columns: 2 },
                                { fieldname: 'description', fieldtype: 'Data', label: 'Description', read_only: 1, columns: 3 },
                                { fieldname: 'uom', fieldtype: 'Data', label: 'UOM', read_only: 1, columns: 1 },
                                { fieldname: 'max_qty', fieldtype: 'Float', label: 'Purchased Qty', read_only: 1, columns: 1 },
                                { fieldname: 'return_qty', fieldtype: 'Float', label: 'Return Qty', reqd: 1, columns: 1 },
                                { fieldname: 'rate', fieldtype: 'Currency', label: 'Rate', read_only: 1, columns: 1 },
                                { fieldname: 'amount', fieldtype: 'Currency', label: 'Amount', read_only: 1, columns: 1 }
                            ],
                            data: (frm.doc.items || []).map(i => ({
                                item: i.item,
                                description: i.description || '',
                                uom: i.uom,
                                max_qty: i.qty,
                                return_qty: 0,
                                rate: i.rate,
                                amount: 0
                            }))
                        }
                    ],
                    primary_action_label: __('Create Return'),
                    primary_action(values) {
                        let return_items = [];

                        (values.purchase_items || []).forEach(row => {
                            if (row.return_qty > 0) {
                                if (row.return_qty > row.max_qty) {
                                    frappe.throw(`Return qty for ${row.item} cannot exceed purchased qty (${row.max_qty})`);
                                }
                                row.amount = row.return_qty * row.rate;
                                return_items.push(row);
                            }
                        });

                        if (!return_items.length) {
                            frappe.msgprint(__('Please enter at least one item with a Return Qty greater than 0.'));
                            return;
                        }

                        frappe.call({
                            method: "books.books.doctype.purchase_invoice.purchase_invoice.create_purchase_return",
                            args: {
                                invoice_name: frm.doc.name,
                                return_items
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.msgprint(__('Purchase Return {0} created', [r.message]));
                                    frappe.set_route('Form', 'Purchase Invoice', r.message);
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

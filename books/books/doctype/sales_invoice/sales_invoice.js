// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt

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
<<<<<<< HEAD
         
=======

>>>>>>> 89e478fc14c46d7bd5b06004156e4fd5f5ff778b
            frm.add_custom_button(__('Return Items'), function() {
                let dialog = new frappe.ui.Dialog({
                    title: __('Return Sales Items'),
                    size: 'large',
                    fields: [
                        {
                            fieldname: 'return_items',
                            fieldtype: 'Table',
                            label: 'Items to Return',
                            cannot_add_rows: false,
                            in_place_edit: true,
                            fields: [
                                { fieldname: 'item', fieldtype: 'Link', options: 'Item', label: 'Item', read_only: 1, in_list_view: 1 },
                                { fieldname: 'uom', fieldtype: 'Link', options: 'UOM', label: 'UOM', read_only: 1, in_list_view: 1 },
                                { fieldname: 'qty', fieldtype: 'Float', label: 'Return Qty', reqd: 1, in_list_view: 1 },
                                { fieldname: 'rate', fieldtype: 'Currency', label: 'Rate', read_only: 1, in_list_view: 1 },
                                { fieldname: 'amount', fieldtype: 'Currency', label: 'Amount', read_only: 1, in_list_view: 1 },
                                { fieldname: 'discount_percentage', fieldtype: 'Float', label: 'Discount %', read_only: 1, in_list_view: 1 },
                                { fieldname: 'discount_amount', fieldtype: 'Currency', label: 'Discount Amount', read_only: 1, in_list_view: 1 },
                                { fieldname: 'net_amount', fieldtype: 'Currency', label: 'Net Amount', read_only: 1, in_list_view: 1 },
                                { fieldname: 'warehouse', fieldtype: 'Link', options: 'Warehouse', label: 'Warehouse', read_only: 1, in_list_view: 1 }
                            ],
                            data: frm.doc.items.map(i => ({
                                item: i.item,
                                uom: i.uom,
                                qty: i.qty,
                                rate: i.rate,
                                amount: i.amount,
                                discount_percentage: i.discount_percentage,
                                discount_amount: i.discount_amount,
                                net_amount: i.net_amount,
                                warehouse: i.warehouse
                            }))
                        }
                    ],
                    primary_action_label: __('Create Return'),
<<<<<<< HEAD
                    primary_action(values) {
                        let return_items = [];
                        (values.return_items || []).forEach(row => {
                            if (row.qty > 0) {
                                return_items.push({
                                    item: row.item,
                                    qty: row.qty,
                                    rate: row.rate,
                                    amount: row.amount,
                                    discount_percentage: row.discount_percentage,
                                    discount_amount: row.discount_amount,
                                    net_amount: row.net_amount,
                                    warehouse: row.warehouse
                                });
                            }
                        });
                        if (!return_items.length) {
                            frappe.msgprint(__('Please enter at least one item with Return Qty'));
                            return;
                        }
=======
                    primary_action: function(values) {
                        let return_items = values.return_items.map(i => ({
                            item: i.item,
                            qty: i.qty
                        }));

>>>>>>> 89e478fc14c46d7bd5b06004156e4fd5f5ff778b
                        frappe.call({
                            method: "books.books.doctype.sales_invoice.sales_invoice.create_sales_return",
                            args: {
                                invoice_name: frm.doc.name,
                                return_items
                            },
                            callback: function(r) {
                                if (r.message) {
                                    frappe.msgprint(__('Sales Return {0} created', [r.message]));
                                    frappe.set_route('Form', 'Sales Invoice', r.message);
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


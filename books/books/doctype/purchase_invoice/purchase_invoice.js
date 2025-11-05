// Copyright (c) 2025, Praveen
// For license information, please see license.txt

frappe.ui.form.on("Purchase Invoice", {
    refresh(frm) {
        if (!frm.is_new() && frm.doc.docstatus === 1) {
            frm.add_custom_button(__('Create Payment Entry'), function () {
                frappe.call({
                    method: "books.books.doctype.purchase_invoice.purchase_invoice.create_payment_entry",
                    args: { invoice_name: frm.doc.name },
                    callback: function (r) {
                        if (r.message) {
                            frappe.msgprint(`Payment Entry <b>${r.message}</b> created successfully.`);

                            frappe.db.get_value("Purchase Invoice", frm.doc.name,
                                ["paid_amount", "outstanding_amount", "payment_entry"],
                                function (res) {
                                    if (res) {
                                        frm.set_value("paid_amount", res.paid_amount);
                                        frm.set_value("outstanding_amount", res.outstanding_amount);
                                        frm.set_value("payment_entry", res.payment_entry);
                                        frm.refresh_fields(["paid_amount", "outstanding_amount", "payment_entry"]);
                                    }
                                }
                            );

                            frappe.set_route("Form", "Payment Entry", r.message);
                        }
                    }
                });
            }, __("Create"));

            frm.add_custom_button(__('Return Items'), function () {
                let dialog = new frappe.ui.Dialog({
                    title: __('Return Purchase Items'),
                    size: 'large',
                    fields: [
                        {
                            fieldname: 'return_items',
                            fieldtype: 'Table',
                            label: 'Items to Return',
                            cannot_add_rows: true,
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
                            frappe.msgprint(__('Please enter at least one item.'));
                            return;
                        }

                        frappe.call({
                            method: "books.books.doctype.purchase_invoice.purchase_invoice.create_purchase_return",
                            args: {
                                invoice_name: frm.doc.name,
                                return_items
                            },
                            callback: function (r) {
                                if (r.message) {
                                    frappe.msgprint(__('Purchase Return {0} created successfully.', [r.message]));
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


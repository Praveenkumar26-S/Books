// Copyright (c) 2025, Praveen and contributors
// For license information, please see license.txt


frappe.ui.form.on("Payment Entry", {
    reference_name: function(frm) {
        if (frm.doc.reference_invoice && frm.doc.reference_name) {
            frappe.call({
                method: "books.books.doctype.payment_entry.payment_entry.get_reference_details",
                args: {
                    reference_invoice: frm.doc.reference_invoice,
                    reference_name: frm.doc.reference_name
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value("party_type", r.message.party_type);
                        frm.set_value("party", r.message.party);
                        frm.set_value("reference_amount", r.message.reference_amount);
                        frm.set_value("outstanding_amount", r.message.outstanding_amount);
                        frm.set_value("amount_paid", r.message.outstanding_amount || 0);
                        frm.refresh_field("amount_paid");
                    } else {
                        frappe.msgprint("No details found for the selected reference.");
                    }
                }
            });
        }
    },
});

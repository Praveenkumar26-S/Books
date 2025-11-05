# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt


import frappe
from frappe import _

def execute(filters=None):
    filters = frappe._dict(filters or {})

    date = filters.get("date")
    based_on = filters.get("based_on")

    data = []

    if based_on == "Item":
        data = frappe.db.sql("""
            SELECT
                'Item' AS based_on_type,
                sii.item AS based_on_value,
                SUM(sii.qty) AS sales_qty,
                SUM(sii.amount) AS sales_amount,
                COALESCE(SUM(pii.qty), 0) AS purchase_qty,
                COALESCE(SUM(pii.amount), 0) AS purchase_amount
            FROM `tabSales Invoice Items` sii
            JOIN `tabSales Invoice` si ON sii.parent = si.name
            LEFT JOIN `tabPurchase Invoice Items` pii
                ON pii.item = sii.item
                AND pii.parent IN (
                    SELECT name FROM `tabPurchase Invoice`
                    WHERE docstatus = 1 AND posting_date = %(date)s
                )
            WHERE si.docstatus = 1 AND si.posting_date = %(date)s
            GROUP BY sii.item
        """, {"date": date}, as_dict=True)

    elif based_on == "Customer":
        data = frappe.db.sql("""
            SELECT
                'Customer' AS based_on_type,
                si.customer AS based_on_value,
                SUM(sii.qty) AS sales_qty,
                SUM(sii.amount) AS sales_amount,
                0 AS purchase_qty,
                0 AS purchase_amount
            FROM `tabSales Invoice` si
            JOIN `tabSales Invoice Items` sii ON sii.parent = si.name
            WHERE si.docstatus = 1 AND si.posting_date = %(date)s
            GROUP BY si.customer
        """, {"date": date}, as_dict=True)

    elif based_on == "Supplier":
        data = frappe.db.sql("""
            SELECT
                'Supplier' AS based_on_type,
                pi.supplier AS based_on_value,
                0 AS sales_qty,
                0 AS sales_amount,
                SUM(pii.qty) AS purchase_qty,
                SUM(pii.amount) AS purchase_amount
            FROM `tabPurchase Invoice` pi
            JOIN `tabPurchase Invoice Items` pii ON pii.parent = pi.name
            WHERE pi.docstatus = 1 AND pi.posting_date = %(date)s
            GROUP BY pi.supplier
        """, {"date": date}, as_dict=True)

    columns = [
        _("Based On Type") + "::150",
        _("Based On Value") + "::200",
        _("Sales Qty") + ":Float:120",
        _("Sales Amount") + ":Currency:150",
        _("Purchase Qty") + ":Float:120",
        _("Purchase Amount") + ":Currency:150"
    ]
    return columns, data

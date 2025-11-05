# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    doc_type = filters.get("doc_type") or "Sales Invoice"

    if doc_type == "Sales Invoice":
        parent = "Sales Invoice"
        child = "Sales Invoice Items"
        parent_alias = "si"
        child_alias = "sii"
        party_field = "si.customer"
        party_group_field = "cust.customer_group"
        join_party = "LEFT JOIN `tabCustomer` cust ON cust.name = si.customer"
        party = filters.get("customer")
        party_group = filters.get("customer_group")

    else:
        parent = "Purchase Invoice"
        child = "Purchase Invoice Items"
        parent_alias = "pi"
        child_alias = "pii"
        party_field = "pi.supplier"
        party_group_field = "supp.supplier_group"
        join_party = "LEFT JOIN `tabSupplier` supp ON supp.name = pi.supplier"
        party = filters.get("supplier")
        party_group = filters.get("supplier_group")

    sql = f"""
        SELECT
            {parent_alias}.posting_date AS date,
            {parent_alias}.name AS invoice,
            {party_field} AS party,
            {party_group_field} AS party_group,
            {child_alias}.qty AS total_qty,
            {child_alias}.amount AS total_amount,
            {child_alias}.discount_amount AS total_discount,
            {child_alias}.net_amount AS net_amount
        FROM `tab{child}` {child_alias}
        JOIN `tab{parent}` {parent_alias}
            ON {parent_alias}.name = {child_alias}.parent
            AND {parent_alias}.docstatus = 1
        {join_party}
        WHERE {parent_alias}.posting_date BETWEEN %(from_date)s AND %(to_date)s
          AND (%(party)s IS NULL OR {party_field} = %(party)s)
          AND (%(party_group)s IS NULL OR {party_group_field} = %(party_group)s)
        GROUP BY {party_field}, {party_group_field}, {parent_alias}.posting_date, {parent_alias}.name
        ORDER BY {party_field}, {parent_alias}.posting_date
    """

    data = frappe.db.sql(sql, {
        "from_date": from_date,
        "to_date": to_date,
        "party": party,
        "party_group": party_group
    }, as_dict=True)

    columns = [
        _("Date") + ":Date:120",
        _("Invoice") + ":Link/{}".format(parent) + ":150",
        _("Party") + ":Data:150",
        _("Party Group") + ":Data:120",
        _("Total Qty") + ":Float:100",
        _("Total Amount") + ":Currency:120",
        _("Total Discount") + ":Currency:120",
        _("Net Amount") + ":Currency:120",
    ]

    return columns, data

# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    if not filters:
        filters = {}

    from_date = filters.get("from_date")
    to_date = filters.get("to_date")
    item = filters.get("item")
    item_group = filters.get("item_group")
    doc_type = filters.get("doc_type") or "Sales Invoice" 

    if doc_type == "Sales Invoice":
        child_doctype = "Sales Invoice Items"
        parent = "Sales Invoice"
        parent_alias = "si"
        child_alias = "sii"
        party_field = "si.customer"
    else:
        child_doctype = "Purchase Invoice Items"
        parent = "Purchase Invoice"
        parent_alias = "pi"
        child_alias = "pii"
        party_field = "pi.supplier"

    sql = f"""
        SELECT
            {parent_alias}.posting_date AS date,
            {parent_alias}.name AS invoice,
            {party_field} AS party,
            {child_alias}.item AS item,
            it.item_name AS item_name,
            it.item_group AS item_group,
            {child_alias}.uom AS uom,
            {child_alias}.qty AS qty,
            {child_alias}.rate AS rate,
            {child_alias}.amount AS total_amount,
            {child_alias}.discount_amount AS total_discount,
            {child_alias}.net_amount AS net_amount
        FROM `tab{child_doctype}` {child_alias}
        JOIN `tab{parent}` {parent_alias} ON {parent_alias}.name = {child_alias}.parent AND {parent_alias}.docstatus = 1
        LEFT JOIN `tabItem` it ON it.name = {child_alias}.item
        WHERE {parent_alias}.posting_date BETWEEN %(from_date)s AND %(to_date)s
          AND (%(item)s IS NULL  OR {child_alias}.item = %(item)s)
          AND (%(item_group)s IS NULL OR it.item_group = %(item_group)s)
        GROUP BY {child_alias}.item, {parent_alias}.posting_date, {child_alias}.uom, {parent_alias}.name
        ORDER BY {parent_alias}.posting_date, {child_alias}.item
    """

    data = frappe.db.sql(sql, {
        "from_date": from_date,
        "to_date": to_date,
        "item": item,
        "item_group": item_group
    }, as_dict=True)

    columns = [
        _("Date") + ":Date:110",
        _("Invoice") + ":Link/{}".format(parent) + ":120",
        _("Party") + ":Data:80",
        _("Item") + ":Link/Item:80",
        _("Item Name") + "::100",
        _("Item Group") + ":Link/Item Group:120",
        _("UOM") + ":Link/UOM:60",
        _("Qty") + ":Float:70",
        _("Rate") + ":Currency:90",
        _("Total Amount") + ":Currency:120",
        _("Total Discount") + ":Currency:120",
        _("Net Amount") + ":Currency:110"
    ]

    return columns, data

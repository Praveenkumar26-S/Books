# Copyright (c) 2025, Praveen and contributors
# For license information, please see license.txt


import frappe
from frappe import _
import calendar

def execute(filters=None):
    filters = filters or {}
    company = filters.get("company")
    year = filters.get("year")

    sales_data = frappe.db.sql("""
        SELECT MONTH(posting_date) AS month, SUM(total_amount) AS total_sales
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND company = %(company)s AND YEAR(posting_date) = %(year)s
        GROUP BY MONTH(posting_date)
    """, {"company": company, "year": year}, as_dict=True)

    purchase_data = frappe.db.sql("""
        SELECT MONTH(posting_date) AS month, SUM(total_amount) AS total_purchase
        FROM `tabPurchase Invoice`
        WHERE docstatus = 1 AND company = %(company)s AND YEAR(posting_date) = %(year)s
        GROUP BY MONTH(posting_date)
    """, {"company": company, "year": year}, as_dict=True)

    sales_map = {r.month: (r.total_sales or 0) for r in sales_data}
    purchase_map = {r.month: (r.total_purchase or 0) for r in purchase_data}

    data = []
    total_sales = total_purchase = total_profit = 0

    for m in range(1, 13):
        s = sales_map.get(m, 0)
        p = purchase_map.get(m, 0)
        pl = s - p
        data.append({
            "month": calendar.month_name[m],
            "total_sales": s,
            "total_purchase": p,
            "profit_loss": pl,
        })
        total_sales += s
        total_purchase += p
        total_profit += pl

    data.append({
        "month": "<b>Total</b>",
        "total_sales": total_sales,
        "total_purchase": total_purchase,
        "profit_loss": total_profit,
    })

    columns = [
        {"label": _("Month"),         "fieldname": "month",         "fieldtype": "Data",     "width": 120},
        {"label": _("Total Sales"),   "fieldname": "total_sales",   "fieldtype": "Currency", "width": 150},
        {"label": _("Total Purchase"),"fieldname": "total_purchase","fieldtype": "Currency", "width": 150},
        {"label": _("Profit/Loss"),   "fieldname": "profit_loss",   "fieldtype": "Currency", "width": 150},
    ]
   
    return columns, data

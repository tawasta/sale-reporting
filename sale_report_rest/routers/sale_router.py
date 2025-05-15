import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from odoo import fields
from odoo.api import Environment

from odoo.addons.fastapi.dependencies import odoo_env

router = APIRouter()
_logger = logging.getLogger(__name__)


def to_date(val):
    if datetime.strptime(val, "%Y-%m-%d"):
        return val
    return None


class SaleService(BaseModel):
    id: dict
    name: dict
    line_count: dict
    state: dict
    date: dict
    commitment_date: dict
    salesperson: dict
    volume: dict
    weight: dict
    company: dict
    country: dict
    commercial_partner: dict
    margin: dict
    delay: dict
    partner: dict
    pricelist: dict
    price_subtotal: dict
    price_total: dict
    euro_total: dict
    untaxed_amount_invoiced: dict
    untaxed_amount_to_invoice: dict
    discount: dict
    discount_amount: dict
    qty_delivered: dict
    qty_invoiced: dict
    qty_to_invoice: dict
    product: dict
    product_template: dict
    category: dict
    sale_type: dict
    uom: dict
    quantity: dict
    original_sale_id: dict
    addresses: dict
    carriers: dict
    sales_agent: dict


class SaleItems(BaseModel):
    count: int
    rows: list[SaleService]


#    @restapi.method(
#        [(["/report"], "GET")],
#        input_param=restapi.CerberusValidator(schema="_validator_report"),
#    )
#    def report(self, start, end=None):
@router.get("/sale/search", response_model=SaleItems)
async def search_sales(env: Annotated[Environment, Depends(odoo_env)], start, end=None):
    """
    GET: Get sale analysis data. No validator for return
    since it takes so long to validate with large amount.

    :param start: string, start date of return data
    :param end: string, end date of return data
    :return: JSON
    """
    _logger.info("Generating sale report")
    rows = []

    order_domain = [
        ("create_date", ">=", start),
    ]
    if end:
        order_domain.append(("create_date", "<=", end))

    orders = env["sale.order"].search(order_domain)
    _logger.info(f"Found {len(orders)} orders")

    if not orders:
        return {"error": "No sale orders found"}

    # Get data from view directly with SQL
    # pylint: disable=E8103
    sql_query = f"""
        SELECT *
        FROM sale_report
        WHERE order_id IN {tuple(orders.ids)}
    """
    env.cr.execute(sql_query)
    records = env.cr.dictfetchall()
    _logger.info(f"Found {len(records)} records")

    partners = env["res.partner"].with_context(active_test=False).search([])
    partner_dict = {part.id: part.name for part in partners}
    users = env["res.users"].with_context(active_test=False).search([])
    users_dict = {user.id: user.name for user in users}
    companies = env["res.company"].search([])
    company_dict = {comp.id: comp.name for comp in companies}
    countries = env["res.country"].search([])
    country_dict = {country.id: country.name for country in countries}
    pricelists = env["product.pricelist"].search([])
    pricelist_dict = {pricelist.id: pricelist.name for pricelist in pricelists}
    products = env["product.product"].with_context(active_test=False).search([])
    product_dict = {product.id: product.display_name for product in products}
    templates = env["product.template"].with_context(active_test=False).search([])
    template_dict = {tmpl.id: tmpl.display_name for tmpl in templates}
    categories = env["product.category"].with_context(active_test=False).search([])
    category_dict = {categ.id: categ.name for categ in categories}
    uoms = env["uom.uom"].search([])
    uom_dict = {uom.id: uom.name for uom in uoms}

    _logger.info("Generating order dict")

    order_dict = {}
    for order in orders:
        order_dict[order.id] = {
            "partner": {
                "name": order.partner_id.name or "",
                "street": order.partner_id.street or "",
                "city": order.partner_id.city or "",
                "zip": order.partner_id.zip or "",
                "country": order.partner_id.country_id.name or "",
            },
            "invoice": {
                "name": order.partner_invoice_id.name or "",
                "street": order.partner_invoice_id.street or "",
                "city": order.partner_invoice_id.city or "",
                "zip": order.partner_invoice_id.zip or "",
                "country": order.partner_invoice_id.country_id.name or "",
            },
            "shipping": {
                "name": order.partner_shipping_id.name or "",
                "street": order.partner_shipping_id.street or "",
                "city": order.partner_shipping_id.city or "",
                "zip": order.partner_shipping_id.zip or "",
                "country": order.partner_shipping_id.country_id.name or "",
            },
            "carriers": [],
        }
        for car in order.picking_ids:
            if car.carrier_id:
                if car.carrier_id.is_default_carrier:
                    carrier_id = car.carrier_id.id
                    carrier_name = car.carrier_id.name
                else:
                    other_carrier = env["delivery.carrier"].search(
                        [("is_alternative_carrier", "=", True)], limit=1
                    )
                    if other_carrier:
                        carrier_name = other_carrier.name
                        carrier_id = other_carrier.id

            else:
                other_carrier = env["delivery.carrier"].search(
                    [("is_alternative_carrier", "=", True)], limit=1
                )
                if other_carrier:
                    carrier_name = other_carrier.name
                    carrier_id = other_carrier.id

            order_dict[order.id]["carriers"].append(
                {
                    "id": carrier_id,
                    "name": carrier_name,
                }
            )
        if not order.picking_ids:
            order_dict[order.id]["carriers"].append(
                {
                    "id": 0,
                    "name": "",
                }
            )

        order_dict[order.id]["sales_agent"] = {
            "id": order.sales_agent.id or 0,
            "name": order.sales_agent.name or "",
            "invoicing": order.sales_agent.customer_default_invoice_address or "",
        }

    _logger.info("Order dict generated")

    _logger.info("Generating response")
    for rec in records:
        # Skip records that aren't in time range
        if not order_dict.get(rec.get("order_id")):
            continue

        # Valuutan käsittely: Tarkistetaan ja muunnetaan tarvittaessa
        order_currency = env["res.currency"].browse(
            rec.get("currency_id")
        )  # Tilauksenrivin valuutta
        company_currency = (
            env["res.company"].browse(rec.get("company_id")).currency_id
        )  # Yrityksen valuutta
        euro_currency = env.ref("base.EUR")  # Kohdevaluutta EUR

        converted_amount = (
            rec.get("price_subtotal") or 0.0
        )  # Oletusarvo: alkuperäinen summa

        # Jos tilauksenrivin valuutta != yrityksen valuutta, muunna yrityksen valuuttaan
        if order_currency and order_currency != company_currency:
            converted_amount = order_currency._convert(
                converted_amount,
                company_currency,
                env["res.company"].browse(rec.get("company_id")),
                rec.get("date") or fields.Date.today(),
                round=True,
            )

        # Jos yrityksen valuutta != EUR, muunna EUR:ksi
        if company_currency and company_currency != euro_currency:
            converted_amount = company_currency._convert(
                converted_amount,
                euro_currency,
                env["res.company"].browse(rec.get("company_id")),
                rec.get("date") or fields.Date.today(),
                round=True,
            )

        rows.append(
            {
                "id": rec.get("id"),
                "name": rec.get("name"),
                "line_count": rec.get("nbr") or 0,
                "state": rec.get("state"),
                "date": rec.get("date") and rec.get("date").isoformat() or "",
                "commitment_date": rec.get("commitment_date")
                and rec.get("commitment_date").isoformat()
                or "",
                "salesperson": users_dict.get(rec.get("user_id"), ""),
                "volume": rec.get("volume"),
                "weight": rec.get("weight"),
                "company": company_dict.get(rec.get("company_id"), ""),
                "country": country_dict.get(rec.get("country_id"), ""),
                "commercial_partner": partner_dict.get(
                    rec.get("commercial_partner_id"), ""
                ),
                "margin": rec.get("margin"),
                "delay": rec.get("delay"),
                "partner": partner_dict.get(rec.get("partner_id"), ""),
                "pricelist": pricelist_dict.get(rec.get("pricelist_id"), ""),
                "price_subtotal": rec.get("price_subtotal") or 0.0,
                "price_total": rec.get("price_total") or 0.0,
                "euro_total": converted_amount,
                "untaxed_amount_invoiced": rec.get("untaxed_amount_invoiced") or 0.0,
                "untaxed_amount_to_invoice": rec.get("untaxed_amount_to_invoice")
                or 0.0,
                "discount": rec.get("discount") or 0.0,
                "discount_amount": rec.get("discount_amount") or 0.0,
                "qty_delivered": rec.get("qty_delivered") or 0.0,
                "qty_invoiced": rec.get("qty_invoiced") or 0.0,
                "qty_to_invoice": rec.get("qty_to_invoice") or 0.0,
                "product": product_dict.get(rec.get("product_id"), ""),
                "product_template": template_dict.get(rec.get("product_tmpl_id"), ""),
                "category": category_dict.get(rec.get("categ_id"), ""),
                "sale_type": env["sale.order"]
                .browse(rec.get("order_id"))
                .sale_type.name
                if rec.get("order_id")
                and env["sale.order"].browse(rec.get("order_id")).sale_type
                else None,
                "uom": uom_dict.get(rec.get("product_uom"), ""),
                "quantity": rec.get("product_uom_qty") or 0.0,
                "original_sale_id": env["sale.order"]
                .sudo()
                .browse(rec["original_sale_id"])
                .name
                if rec.get("original_sale_id")
                else "",
                "addresses": {
                    "partner": order_dict.get(rec.get("order_id"), {}).get(
                        "partner", {}
                    ),
                    "invoice": order_dict.get(rec.get("order_id"), {}).get(
                        "invoice", {}
                    ),
                    "shipping": order_dict.get(rec.get("order_id"), {}).get(
                        "shipping", {}
                    ),
                },
                "carriers": order_dict.get(rec.get("order_id"), {}).get("carriers", []),
                "sales_agent": order_dict.get(rec.get("order_id"), {}).get(
                    "sales_agent", {}
                ),
            }
        )

    _logger.info("Response generated")

    res = {
        "count": len(rows),
        "rows": rows,
    }
    _logger.info(f"Sale REST API: JSON with {len(rows)} rows about sale reports")
    return res

    # Validators


# def _validator_report(self):
#     """Validator for report endpoint"""
#     schema = {
#         "start": {
#             "type": "string",
#             "nullable": False,
#             "required": True,
#             "coerce": to_date,
#         },
#         "end": {
#             "type": "string",
#             "nullable": True,
#             "required": False,
#             "coerce": to_date,
#         },
#     }
#     return schema

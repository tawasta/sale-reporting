.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Sale reports REST API
=====================

This Odoo module provides REST API endpoints for sales and invoice analysis using FastAPI.

Key Features
============

* REST API endpoints for `sale.order` and `account.move.line` data
* Includes converted monetary values in euros
* Detailed partner, carrier, and address information
* Tag and sales agent metadata
* Enforces single default and alternative delivery carriers
* Access controlled via FastAPI groups and users

Endpoints
=========

The module registers two FastAPI endpoints:

* ``GET /sale_rest_api/invoice/report`` – Returns invoice line reports
* ``GET /sale_rest_api/sale/report`` – Returns sales order line reports

All endpoints require valid authentication and appropriate user permissions.

Installation
============

Dependencies:

* `fastapi`
* `pydantic`

Ensure the following Odoo modules are installed:

* `fastapi`
* `sale_pivot_report_sh_product_tag`
* `account_invoice_pivot_report_delivery_address`
* `account_invoice_pivot_report_delivery_address_country`
* `account_invoice_pivot_report_product_template`
* `sales_agent`
* `stock_picking_invoice_link`

Configuration
=============

1. Create an integration user (e.g. *Sale Reports API User*)
2. Assign the user to the *Sale Reports FastAPI Group*
3. Create a FastAPI Endpoint record:
   * App: `sale_reports`
   * Root path: `/sale_rest_api`
   * User: integration user

Optional fields for delivery carriers:

* `Is Default Carrier`: Only one carrier can be marked as default.
* `Is Alternative Carrier`: Only one carrier can be marked as alternative.

Usage
=====

Send HTTP GET requests with required query parameters (`start`, optionally `end`) to the configured endpoints. You must authenticate using Odoo's FastAPI authentication mechanism (e.g. API keys or session-based).

Example:
::

    GET /sale_rest_api/sale/report?start=2024-01-01&end=2024-01-31

Response:
::

    {
        "count": 42,
        "rows": [
            {
                "id": 123,
                "name": "SO0001",
                ...
            },
            ...
        ]
    }

Known Issues / Roadmap
======================

* Currently supports only read access
* More endpoints and filtering options may be added in future

Credits
=======

Contributors
------------

* Aleksi Savijoki <aleksi.savijoki@tawasta.fi>
* Timo Kekäläinen <timo.kekalainen@tawasta.fi>
* Valtteri Lattu <valtteri.lattu@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Sale reports REST API
=====================

This Odoo module provides **secured REST API endpoints** for sales and invoice
analysis using **FastAPI**.

The API is **not public**. All endpoints require authentication using **API keys**
provided via HTTP headers.

Key Features
============

* REST API endpoints for ``sale.order`` and ``account.move.line`` data
* API key based authentication using ``fastapi_auth_api_key``
* Endpoint-level access control via API key groups
* Includes converted monetary values in euros (EUR)
* Detailed partner, carrier, address, tag, and sales agent information
* Enforces single default and alternative delivery carriers
* Read-only access (no write operations)

Endpoints
=========

The module registers two FastAPI endpoints under the root path ``/sale_rest_api``:

* ``GET /sale_rest_api/invoice/report``  
  Returns invoice line level reporting data.

* ``GET /sale_rest_api/sale/report``  
  Returns sales order line level reporting data.

All endpoints require a valid API key.

Installation
============

Python dependencies:

* ``fastapi``
* ``pydantic``

Ensure the following Odoo modules are installed:

* ``fastapi``
* ``fastapi_auth_api_key``
* ``auth_api_key``
* ``sale_pivot_report_sh_product_tag``
* ``account_invoice_pivot_report_delivery_address``
* ``account_invoice_pivot_report_delivery_address_country``
* ``account_invoice_pivot_report_product_template``
* ``sales_agent``
* ``stock_picking_invoice_link``

Configuration
=============

After installing the module, configure access as follows:

1. **Integration User**

   The module creates a technical user:

   * ``Sale Report REST API User``

   This user is used to execute API requests.

2. **API Key Group**

   The module defines an API key group:

   * ``Sale Report REST API Keys``

   Only API keys belonging to this group are allowed to access the endpoints.

3. **FastAPI Endpoint**

   A FastAPI endpoint record is created with the following configuration:

   * App: ``sale_reports``
   * Root path: ``/sale_rest_api``
   * User: ``Sale Report REST API User``
   * API key group: ``Sale Report REST API Keys``

4. **API Key**

   Create an API key in Odoo:

   * User: ``Sale Report REST API User``
   * Group: ``Sale Report REST API Keys``

   Store the generated key securely. It will be required for all API requests.

Optional fields for delivery carriers:

* ``Is Default Carrier``: Only one carrier can be marked as default.
* ``Is Alternative Carrier``: Only one carrier can be marked as alternative.

Usage
=====

All requests must include an API key in the HTTP headers.

Default header name::

    HTTP-API-KEY

Required query parameters:

* ``start`` – Start date in ``YYYY-MM-DD`` format
* ``end`` – Optional end date in ``YYYY-MM-DD`` format

Example::

    GET /sale_rest_api/invoice/report?start=2025-01-01&end=2025-01-31

Known Issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Aleksi Savijoki <aleksi.savijoki@futural.fi>
* Timo Kekäläinen <timo.kekalainen@futural.fi>
* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: http://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: http://futural.fi/

This module is maintained by Futural Oy

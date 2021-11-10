.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================================
Sale Report - Group by SH product tags
======================================

Sale order line sh_product_tag_ids values are computed automatically and
stored in to the database. This enable grouping by those tags in the Sale
Analysis, which can be found in Sale --> Reporting --> Sales and clicking
on the pivot view. There a grouping by sale order lines' product Tags is
possible by choosing the Tags option.

Configuration
=============
OCA's sh_product_variant_tags module needs to be installed also to use this
module.

Usage
=====
Install the module from Apps.

Known issues / Roadmap
======================
Note that sale order line's sh_product_tag_ids field is a computed field
and it stores only the first value from sale order line's product's
sh_product_tag_ids field. This is because product's sh_product_tag_ids
field is a many2many field, which is rather bothersome to use to group things.

Credits
=======

Contributors
------------

* Timo Kekäläinen <timo.kekalainen@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.

.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=============================
Show my sale order by default
=============================

This module restricts visibility of the **Confirm** button on sale orders to users belonging to a specific security group.

It is useful in cases where only certain roles (e.g., managers or team leads) should be allowed to confirm sales.

Configuration
=============

After installing the module:

- Go to **Settings > Users & Companies > Groups**
- Assign the group **"Can Confirm Sale Orders"** to the appropriate users or roles.

Usage
=====

- Open a sale order.
- Only users in the **"Can Confirm Sale Orders"** group will see the **Confirm** button.


Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.

.. module:: doapi

Library
=======

.. toctree::
   library/doapi
   library/droplets
   library/domain
   library/misc
   library/extra
   library/examples

Generators producing objects always yield them in whatever order the API
endpoint returns them in.

All public non-magic methods perform API requests and may raise a `DOAPIError`.

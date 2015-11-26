.. module:: doapi

Library
=======

.. toctree::
   library/doapi
   library/droplets
   library/domain

Generators producing objects always yield them in whatever order the API
endpoint returns them in.

All public non-magic methods perform API requests and may raise a `DOAPIError`.

Other Resources
---------------

.. autoclass:: Account

.. autoclass:: Action

.. autoclass:: FloatingIP

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action

.. autoclass:: Image

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action
   .. automethod:: fetch_droplet

.. autoclass:: Region

.. autoclass:: Size

.. autoclass:: SSHKey

Non-Resource Classes
--------------------

.. autoexception:: DOAPIError
   :no-inherited-members:

.. autoclass:: DOEncoder
   :no-inherited-members:

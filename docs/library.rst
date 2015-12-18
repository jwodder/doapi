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

Account
^^^^^^^

.. autoclass:: Account

Action
^^^^^^

.. autoclass:: Action

FloatingIP
^^^^^^^^^^

.. autoclass:: FloatingIP

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action

Image
^^^^^

.. autoclass:: Image

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action
   .. automethod:: fetch_droplet

Region
^^^^^^

.. autoclass:: Region

Size
^^^^

.. autoclass:: Size

SSHKey
^^^^^^

.. autoclass:: SSHKey

Non-Resource Classes
--------------------

DOAPIError
^^^^^^^^^^

.. autoexception:: DOAPIError
   :no-inherited-members:

DOEncoder
^^^^^^^^^

.. autoclass:: DOEncoder
   :no-inherited-members:

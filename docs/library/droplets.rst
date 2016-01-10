.. module:: doapi

Droplets
--------

Droplet
^^^^^^^

.. autoclass:: Droplet()

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action
   .. automethod:: __int__

DropletUpgrade
^^^^^^^^^^^^^^

.. autoclass:: DropletUpgrade()

Kernel
^^^^^^

.. autoclass:: Kernel()

   .. automethod:: fetch_droplet
   .. automethod:: __int__

Networks
^^^^^^^^

.. autoclass:: Networks()

   .. automethod:: fetch_droplet

NetworkInterface
^^^^^^^^^^^^^^^^

.. autoclass:: NetworkInterface()
   :special-members: __str__

   .. automethod:: fetch_droplet

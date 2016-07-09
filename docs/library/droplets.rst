.. module:: doapi

Droplets
--------

Droplet
^^^^^^^

.. autoclass:: Droplet()

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait_for_action
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action
   .. automethod:: __int__
   .. automethod:: tag
   .. automethod:: untag

.. [APIDocs] https://developers.digitalocean.com/documentation/v2/

BackupWindow
^^^^^^^^^^^^

.. autoclass:: BackupWindow()

Kernel
^^^^^^

.. autoclass:: Kernel()

   .. automethod:: __int__

Networks
^^^^^^^^

.. autoclass:: Networks()

NetworkInterface
^^^^^^^^^^^^^^^^

.. autoclass:: NetworkInterface()
   :special-members: __str__

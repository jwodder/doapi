.. module:: doapi

Other Resources
---------------

Account
^^^^^^^

.. autoclass:: Account()

Action
^^^^^^

.. autoclass:: Action()

   .. automethod:: __int__

FloatingIP
^^^^^^^^^^

.. autoclass:: FloatingIP()
   :special-members: __str__

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action

Image
^^^^^

.. autoclass:: Image()
   :special-members: __str__

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: wait
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action
   .. automethod:: fetch_droplet
   .. automethod:: __int__

Region
^^^^^^

.. autoclass:: Region()
   :special-members: __str__

Size
^^^^

.. autoclass:: Size()
   :special-members: __str__

SSHKey
^^^^^^

.. autoclass:: SSHKey()
   :special-members: __str__

   .. automethod:: __int__

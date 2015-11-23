Library
=======

.. module:: doapi

Generators producing objects always yield them in whatever order the API
endpoint returns them in.

Client Class
------------

.. autoclass:: doapi

Droplets and Their Fields
-------------------------

.. autoclass:: Droplet

   .. autoattribute:: action_url
   .. automethod:: act
   .. automethod:: fetch_all_actions
   .. automethod:: fetch_last_action
   .. automethod:: fetch_current_action

.. autoclass:: DropletUpgrade

   .. automethod:: fetch_droplet

.. autoclass:: Kernel

   .. automethod:: fetch_droplet

.. autoclass:: Networks

   .. automethod:: fetch_droplet

.. autoclass:: NetworkInterface

   .. automethod:: fetch_droplet

Other Resources
---------------

.. autoclass:: Account

.. autoclass:: Action

.. autoclass:: Domain

.. autoclass:: DomainRecord

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

Additional Classes
------------------

.. autoclass:: DOAPIError
   :no-inherited-members:

.. autoexception:: DOEncoder
   :no-inherited-members:

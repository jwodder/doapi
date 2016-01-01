.. module:: doapi

``doapi-floating-ip``
---------------------

Synopsis
^^^^^^^^

.. Add ``doapi-floating-ip [<universal options>]`` once "implicit show" is supported

::

    doapi-floating-ip show [<ip> ...]

    doapi-floating-ip new [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] -D|--droplet <droplet>
    doapi-floating-ip new [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] -R|--region <region>

    doapi-floating-ip assign [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] <ip> <droplet>
    doapi-floating-ip unassign [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] <ip> ...
    doapi-floating-ip delete <ip> ...

    doapi-floating-ip act [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] [-p|--params <JSON dict> | -P|--param-file <file>] <type> <ip> ...
    doapi-floating-ip actions [--last | --current] <ip> ...
    doapi-floating-ip wait [--wait-time <seconds>] [--wait-interval <seconds>] <ip> ...

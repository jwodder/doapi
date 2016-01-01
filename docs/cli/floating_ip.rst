.. module:: doapi

``doapi-floating-ip``
---------------------

Synopsis
^^^^^^^^

.. Add ``doapi-floating-ip [<universal options>]`` once "implicit show" is supported

::

    doapi-floating-ip show [<ip> ...]

    doapi-floating-ip new -D|--droplet <droplet>
    doapi-floating-ip new -R|--region <region>

    doapi-floating-ip assign <ip> <droplet>
    doapi-floating-ip unassign <ip> ...
    doapi-floating-ip delete <ip> ...

    doapi-floating-ip act [-p|--params <JSON dict> | -P|--param-file <file>] <type> <ip> ...
    doapi-floating-ip actions [--last | --current] <ip> ...
    doapi-floating-ip wait [--wait-time <seconds>] [--wait-interval <seconds>] <ip> ...

.. currentmodule:: doapi

:program:`doapi-droplet`
------------------------

NAME
^^^^

:program:`doapi-droplet` — manage DigitalOcean droplets

SYNOPSIS
^^^^^^^^

.. Add ``doapi-droplet [<universal options>]`` once "implicit show" is supported

::

    doapi-droplet new
            -I|--image <image>
            -S|--size <size>
            -R|--region <region>
            [-B|--backups]
            [-6|--ipv6]
            [-P|--private-networking]
            [-U|--user-data <string|@file>]
            [-K|--ssh-key <key>] ...
            [--unique]
            [-w|--wait] [--wait-time <seconds>] [--wait-interval <seconds>]
            <name> ...

    doapi-droplet show [-M|--multiple] [--tag <tag> | <droplet> ...]

    doapi-droplet enable-backups [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet disable-backups [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet reboot [<wait options>] [-M|--multiple] <droplet> ...
    doapi-droplet power-cycle [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet shutdown [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet power-off [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet power-on [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet password-reset [<wait options>] [-M|--multiple] <droplet> ...
    doapi-droplet enable-ipv6 [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet enable-private-networking [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}

    doapi-droplet show-snapshots [-M|--multiple] <droplet> ...
    doapi-droplet backups [-M|--multiple] <droplet> ...
    doapi-droplet kernels [-M|--multiple] <droplet> ...
    doapi-droplet delete [-M|--multiple] {--tag <tag> | <droplet> ...}

    doapi-droplet neighbors
    doapi-droplet neighbors [-M|--multiple] <droplet> ...

    doapi-droplet restore [<wait options>] <droplet> <backup>

    doapi-droplet resize [<wait options>] [--disk] [-M|--multiple] <size> <droplet> ...

    doapi-droplet rebuild [<wait options>] [-I|--image <image>] [-M|--multiple] <droplet> ...

    doapi-droplet rename [<wait options>] [--unique] <droplet> <new name>
    doapi-droplet snapshot [<wait options>] [--unique] <name> {--tag <tag> | <droplet> ...}
    doapi-droplet change-kernel [<wait options>] [-M|--multiple] <kernel> <droplet> ...

    doapi-droplet act [<wait options>] [-p|--params <JSON|@file>] [-M|--multiple] <type> {--tag <tag> | <droplet> ...}
    doapi-droplet actions [--last | --in-progress] [-M|--multiple] <droplet> ...
    doapi-droplet wait [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] [-S|--status <status> | --locked | --unlocked] <droplet> ...

    doapi-droplet tag [-M|--multiple] <tag> <droplet> ...
    doapi-droplet untag [-M|--multiple] <tag> <droplet> ...

:program:`doapi-droplet` also takes the :ref:`universal options <universal>`
common to all :program:`doapi` commands.

Droplets can be specified by ID number or name.  A name that is also a valid ID
is interpreted as such rather than as a name (and so droplets with such names
must be referred to by their actual ID instead).


:command:`new`
^^^^^^^^^^^^^^

::

    doapi-droplet new
            -I|--image <image>
            -S|--size <size>
            -R|--region <region>
            [-B|--backups]
            [-6|--ipv6]
            [-P|--private-networking]
            [-U|--user-data <string|@file>]
            [-K|--ssh-key <key>] ...
            [--unique]
            [-w|--wait] [--wait-time <seconds>] [--wait-interval <seconds>]
            <name> ...


:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-droplet show [-M|--multiple] [--tag <tag> | <droplet> ...]


Simple Actions
^^^^^^^^^^^^^^

::

    doapi-droplet enable-backups [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet disable-backups [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet reboot [<wait options>] [-M|--multiple] <droplet> ...
    doapi-droplet power-cycle [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet shutdown [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet power-off [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet power-on [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet password-reset [<wait options>] [-M|--multiple] <droplet> ...
    doapi-droplet enable-ipv6 [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}
    doapi-droplet enable-private-networking [<wait options>] [-M|--multiple] {--tag <tag> | <droplet> ...}


:command:`show-snapshots`
^^^^^^^^^^^^^^^^^^^^^^^^^

::

    doapi-droplet show-snapshots [-M|--multiple] <droplet> ...


:command:`backups`
^^^^^^^^^^^^^^^^^^

::

    doapi-droplet backups [-M|--multiple] <droplet> ...


:command:`kernels`
^^^^^^^^^^^^^^^^^^

::

    doapi-droplet kernels [-M|--multiple] <droplet> ...


:command:`neighbors`
^^^^^^^^^^^^^^^^^^^^

::

    doapi-droplet neighbors
    doapi-droplet neighbors [-M|--multiple] <droplet> ...


:command:`restore`
^^^^^^^^^^^^^^^^^^

::

    doapi-droplet restore [<wait options>] <droplet> <backup>


:command:`resize`
^^^^^^^^^^^^^^^^^

::

    doapi-droplet resize [<wait options>] [--disk] [-M|--multiple] <size> <droplet> ...


:command:`rebuild`
^^^^^^^^^^^^^^^^^^

::

    doapi-droplet rebuild [<wait options>] [-I|--image <image>] [-M|--multiple] <droplet> ...


:command:`rename`
^^^^^^^^^^^^^^^^^

::

    doapi-droplet rename [<wait options>] [--unique] <droplet> <new name>

:command:`snapshot`
^^^^^^^^^^^^^^^^^^^

::

    doapi-droplet snapshot [<wait options>] [--unique] <name> {--tag <tag> | <droplet> ...}


:command:`change-kernel`
^^^^^^^^^^^^^^^^^^^^^^^^

::

    doapi-droplet change-kernel [<wait options>] [-M|--multiple] <kernel> <droplet> ...


:command:`act`
^^^^^^^^^^^^^^

::

    doapi-droplet act [<wait options>] [-p|--params <JSON|@file>] [-M|--multiple] <type> {--tag <tag> | <droplet> ...}


:command:`actions`
^^^^^^^^^^^^^^^^^^

::

    doapi-droplet actions [--last | --in-progress] [-M|--multiple] <droplet> ...


:command:`wait`
^^^^^^^^^^^^^^^

::

    doapi-droplet wait [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] [-S|--status <status> | --locked | --unlocked] <droplet> ...


:command:`delete`
^^^^^^^^^^^^^^^^^

::

    doapi-droplet delete [-M|--multiple] {--tag <tag> | <droplet> ...}


:command:`tag`
^^^^^^^^^^^^^^

::

    doapi-droplet tag [-M|--multiple] <tag> <droplet> ...


:command:`untag`
^^^^^^^^^^^^^^^^^

::

    doapi-droplet untag [-M|--multiple] <tag> <droplet> ...

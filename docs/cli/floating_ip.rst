.. module:: doapi

:program:`doapi-floating-ip`
----------------------------

NAME
^^^^

:program:`doapi-floating-ip` — manage DigitalOcean floating IP addresses

SYNOPSIS
^^^^^^^^

.. Add ``doapi-floating-ip [<universal options>]`` once "implicit show" is supported

::

    doapi-floating-ip new      [<wait options>] -D|--droplet <droplet>
    doapi-floating-ip new      [<wait options>] -R|--region <region>

    doapi-floating-ip show     [<ip> ...]

    doapi-floating-ip assign   [<wait options>] <ip> <droplet>
    doapi-floating-ip unassign [<wait options>] <ip> ...

    doapi-floating-ip act      [<wait options>] [-p|--params <JSON|@file>] <type> <ip> ...
    doapi-floating-ip actions  [--in-progress | --last] <ip> ...
    doapi-floating-ip wait     [--wait-interval <seconds>] [--wait-time <seconds>] <ip> ...

    doapi-floating-ip delete   <ip> ...

:program:`doapi-floating-ip` also takes the :ref:`universal options
<universal>` common to all :program:`doapi` commands.

Floating IPs can be specified in either dotted-quad notation (e.g.,
``127.0.0.1``) or as 32-bit integers (e.g., ``2130706433``).

:command:`new`
^^^^^^^^^^^^^^

::

    doapi-floating-ip new [<wait options>] -D|--droplet <droplet>
    doapi-floating-ip new [<wait options>] -R|--region <region>

Create a new floating IP assigned to a droplet or reserved to a region.  The
new IP is output as a `FloatingIP` object converted to JSON.

Options
'''''''

In addition to the :ref:`waiting options <waitopts>`, the :command:`new`
subcommand takes the following:

.. program:: doapi-floating-ip new

.. option:: -D <droplet>, --droplet <droplet>

    Assign the new floating IP to the specified droplet (identified by ID or
    name).  The floating IP will also be reserved to the droplet's region.

.. option:: -R <region>, --region <region>

    Reserve the floating IP to the specified region (identified by slug).

:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-floating-ip show [<ip> ...]

Show floating IPs.  If no IPs are specified, all IPs allocated to the account
are shown.  The IPs are output as a list of `FloatingIP` objects converted to
JSON.

:command:`assign`
^^^^^^^^^^^^^^^^^

::

    doapi-floating-ip assign [<wait options>] <ip> <droplet>

Assign the given floating IP to a given droplet (identified by ID or name).
The `Action` object thus produced is output as JSON.

The :command:`assign` subcommand only takes the :ref:`waiting options
<waitopts>`.

:command:`unassign`
^^^^^^^^^^^^^^^^^^^

::

    doapi-floating-ip unassign [<wait options>] <ip> ...

Unassign the given floating IP(s) from their droplet(s).  The `Action` objects
thus produced are output as a JSON list.

The :command:`unassign` subcommand only takes the :ref:`waiting options
<waitopts>`.

:command:`act`
^^^^^^^^^^^^^^

::

    doapi-floating-ip act [<wait options>] [-p|--params <JSON|@file>] <type> <ip> ...

Perform an arbitrary action of type ``<type>`` (``assign``, ``unassign``, or
something otherwise not implemented here) on one or more floating IPs.  The
`Action` objects thus produced are output as a JSON list.

Options
'''''''

In addition to the :ref:`waiting options <waitopts>`, the :command:`act`
subcommand takes the following:

.. program:: doapi-floating-ip act

.. option:: -p <data>, --params <data>

    A JSON object/dictionary of parameters to the action.  If ``<data>`` begins
    with "``@``", the rest of the argument (if there is any) is treated as a
    file from which to read the JSON; a filename of ``-`` causes data to be
    read from standard input.

:command:`actions`
^^^^^^^^^^^^^^^^^^

::

    doapi-floating-ip actions [--in-progress | --last] <ip> ...

List all of the actions that have ever been performed on the given floating
IP(s).  The results are output as a JSON list containing a sublist of `Action`
objects for each IP specified on the command line, in order.

Options
'''''''

.. program:: doapi-floating-ip actions

.. option:: --in-progress

    Show only the currently in-progress action on each floating IP instead of a
    list of all actions.  If there is currently no in-progress action on an IP,
    show ``null``.

.. option:: --last

    Show only the most recent action on each floating IP instead of a list of
    all actions.  If multiple actions on a single IP were triggered
    simultaneously, the choice of which to return is undefined.


:command:`wait`
^^^^^^^^^^^^^^^

::

    doapi-floating-ip wait [--wait-interval <seconds>] [--wait-time <seconds>] <ip> ...

Wait for the currently in-progress actions on the given floating IP(s) to
either complete or error out.  The finished actions are output as a list of
`Action` objects converted to JSON, with each action output (roughly) as soon
as it finishes.

Options
'''''''

.. program:: doapi-floating-ip wait

.. option:: --wait-interval <seconds>

    How often to poll the server for the actions' current statuses; default
    value: 5 seconds

.. option:: --wait-time <seconds>

    The maximum number of seconds to wait for all actions to complete.  After
    this much time has passed since program invocation, any remaining
    in-progress actions will be output immediately without waiting for them to
    finish.

    If this option is not specified, :command:`wait` will wait indefinitely.

:command:`delete`
^^^^^^^^^^^^^^^^^

::

    doapi-floating-ip delete <ip> ...

Delete floating IPs.  There is no output.

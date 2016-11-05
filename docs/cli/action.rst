.. currentmodule:: doapi

:program:`doapi-action`
-----------------------

NAME
^^^^

:program:`doapi-action` — manage DigitalOcean API actions

SYNOPSIS
^^^^^^^^

.. Add ``doapi-action [<universal options>]`` once "implicit show" is supported

::

    doapi-action show [<action> ...]
    doapi-action show {--in-progress | --last}
    doapi-action wait [--wait-time <seconds>] [--wait-interval <seconds>] [<action> ...]
    doapi-action resource <action> ...
    doapi-action resource {--in-progress | --last}

:program:`doapi-action` also takes the :ref:`universal options <universal>`
common to all :program:`doapi` commands.

Actions are specified by ID number.


:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-action show [<action> ...]
    doapi-action show {--in-progress | --last}

Show the given actions.  If no actions or flags are specified, all actions ever
performed on the account are shown.  The actions are output as a list of
`Action` objects converted to JSON.

Options
'''''''

.. program:: doapi-action show

.. option:: --in-progress

    Show only the currently in-progress actions

.. option:: --last

    Show only the most recent action performed on the account instead of a list
    of all actions.  If multiple actions were triggered simultaneously, the
    choice of which to display is undefined.


:command:`wait`
^^^^^^^^^^^^^^^

::

    doapi-action wait [--wait-time <seconds>] [--wait-interval <seconds>] [<action> ...]

Wait for the given actions to either complete or error out.  The finished
actions are output as a list of `Action` objects converted to JSON, with each
action output (roughly) as soon as it finishes.  If no actions are specified,
:command:`wait` will wait for all currently in-progress actions to complete.

Options
'''''''

.. program:: doapi-action wait

.. option:: --wait-interval <seconds>

    How often to poll the server for the actions' current statuses; default
    value: 5 seconds

.. option:: --wait-time <seconds>

    The maximum number of seconds to wait for all actions to complete.  After
    this much time has passed since program invocation, any remaining
    in-progress actions will be output immediately without waiting for them to
    finish.

    If this option is not specified, :command:`wait` will wait indefinitely.


:command:`resource`
^^^^^^^^^^^^^^^^^^^

::

    doapi-action resource <action> ...
    doapi-action resource {--in-progress | --last}

Show the resources that the specified actions operated on.  The resources are
output as a list of `Droplet`, `Image`, and/or `FloatingIP` objects converted
to JSON.  Resources that no longer exist are output as ``null``.

Options
'''''''

.. program:: doapi-action resource

.. option:: --in-progress

    Show only the resources currently being acted upon

.. option:: --last

    Show only the resource operated on by the account's most recent action.  If
    multiple actions were triggered simultaneously, the choice of which to
    display is undefined.  If no actions have ever been performed on the
    account, the output is ``null``.

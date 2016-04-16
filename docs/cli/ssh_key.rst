.. module:: doapi

:program:`doapi-ssh-key`
------------------------

NAME
^^^^

:program:`doapi-ssh-key` — manage SSH public keys on DigitalOcean

SYNOPSIS
^^^^^^^^

.. Add ``doapi-ssh-key [<universal options>]`` once "implicit show" is supported

::

    doapi-ssh-key new    [--unique]      <name> [<file>]
    doapi-ssh-key show   [-M|--multiple] [<ssh key> ...]
    doapi-ssh-key update [--unique]      <ssh key> <new name>
    doapi-ssh-key delete [-M|--multiple] <ssh key> ...

:program:`doapi-ssh-key` also takes the :ref:`universal options <universal>`
common to all :program:`doapi` commands.

SSH keys can be specified by ID number, fingerprint, or name.  A name that is
also a valid ID or fingerprint is interpreted as such rather than as a name
(and so SSH keys with such names must be referred to by their ID or fingerprint
instead).


:command:`new`
^^^^^^^^^^^^^^

::

    doapi-ssh-key new [--unique] <name> [<file>]

Register the contents of ``<file>`` (or standard input if no file is specified)
as a new SSH public key with name ``<name>``.  The new key is output as an
`SSHKey` object converted to JSON.

Options
'''''''

.. program:: doapi-ssh-key new

.. option:: --unique

    If ``<name>`` is already in use by another key, fail with an error.
    Without this option, a warning will still be generated if ``<name>`` is
    already in use.


:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-ssh-key show [-M|--multiple] [<ssh key> ...]

Show SSH keys.  If no keys are specified, all keys registered to the account
are shown.  The keys are output as a list of `SSHKey` objects converted to
JSON.

Options
'''''''

.. program:: doapi-ssh-key show

.. option:: -M, --multiple

    Arguments that could refer to multiple SSH keys are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.


:command:`update`
^^^^^^^^^^^^^^^^^

::

    doapi-ssh-key update [--unique] <ssh key> <new name>

Update (i.e., rename) an SSH key.  The updated key is output as an `SSHKey`
object converted to JSON.

Options
'''''''

.. program:: doapi-ssh-key update

.. option:: --unique

    If ``<new name>`` is already in use by another key, fail with an error.
    Without this option, a warning will still be generated if ``<new name>`` is
    already in use.


:command:`delete`
^^^^^^^^^^^^^^^^^

::

    doapi-ssh-key delete [-M|--multiple] <ssh key> ...

Delete SSH keys.  There is no output.

Options
'''''''

.. program:: doapi-ssh-key delete

.. option:: -M, --multiple

    Arguments that could refer to multiple SSH keys are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.

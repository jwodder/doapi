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

    doapi-ssh-key show   [-M|--multiple] [<ssh key> ...]
    doapi-ssh-key new    [--unique]      <name> [<infile>]
    doapi-ssh-key delete [-M|--multiple] <ssh key> ...
    doapi-ssh-key update [--unique]      <ssh key> <new name>

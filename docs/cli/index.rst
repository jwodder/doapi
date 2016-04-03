.. module:: doapi

Command-Line Programs
=====================

.. toctree::
   :maxdepth: 1

   account
   action
   domain
   droplet
   floating_ip
   image
   region
   request
   size
   sshkey

TODO

[Document the plain :program:`doapi` command]

----

In order to perform API requests, an OAuth token must be supplied to
:program:`doapi` so that it can authenticate with the DigitalOcean server.  You
can generate an OAuth token for your account via the `"Apps & API" section
<https://cloud.digitalocean.com/settings/applications>`_ of your DigitalOcean
account's control panel.

The :program:`doapi` commands will look for an OAuth token in the following
locations, in order:

1. Specified on the command line with :samp:`--api-token {token}` or
   :samp:`--api-token-file {file}`
2. The value of the :envvar:`DO_API_TOKEN` environment variable
3. The contents of a :file:`.doapi` file in your home directory

----

.. _universal:

Universal Options
-----------------

All commands take the following options in addition to those listed in their
individual documentation:

.. option:: --api-token <token>

    Use ``<token>`` as an OAuth token for authentication with the API; mutually
    exclusive with ``--api-token-file``

.. option:: --api-token-file <file>

    Use the contents of ``<file>`` as an OAuth token for authentication with
    the API; mutually exclusive with ``--api-token``

.. option:: --endpoint <URL>

    Use ``<URL>`` as the base URL for all API requests; default value:
    ``https://api.digitalocean.com`` (the official DigitalOcean API endpoint)

.. option:: --help

    Show command usage and exit

.. option:: --timeout <seconds>

    The maximum number of seconds to wait when attempting to connect to or read
    from the remote endpoint; default value: no timeout

.. option:: --version

    Show doapi version and exit

Note that these options (other than :option:`--help`) cannot be attached to
subcommands::

    doapi-droplet --timeout 1000 show  # Good
    doapi --timeout 1000 droplet show  # Good
    doapi-droplet show --timeout 1000  # Bad!


.. _waitopts:

Waiting Options
---------------

All subcommands that perform non-atomic actions on resources can take the
following options in order to wait for the actions to complete before
returning:

.. option:: --wait

    Periodically poll the server for the current status of all actions until
    they all complete or error out or until the time limit specified by
    :option:`--wait-time` is exceeded.  If this action is not specified, the
    subcommand will exit immediately after initiating the actions.

.. option:: --wait-interval <seconds>

    How often to poll the server for the actions' current statuses; default
    value: 5 seconds

.. option:: --wait-time <seconds>

    The maximum number of seconds to wait for all actions to complete.  After
    this much time has passed since program invocation, any remaining
    in-progress actions will be output immediately without waiting for them to
    finish.

    If :option:`--wait` is specified but this option is not, the subcommand
    will wait indefinitely.

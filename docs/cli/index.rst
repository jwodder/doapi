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
   ssh_key

..
    Document the plain :program:`doapi` command
    [All commands output pretty-printed (sans colors) JSON]

Common CLI Behavior
-------------------

API Authentication
''''''''''''''''''

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


Handling Non-Uniqueness of Identifiers
''''''''''''''''''''''''''''''''''''''

Most resources in the API are referred to by only a single identifier each, but
droplets, images, and SSH keys can be referred to by either a unique ID number,
a unique slug (for certain images), a unique fingerprint (for SSH keys), or a
(potentially) *non*-unique name.

When the user specifies an object identifier that could be an ID, slug,
fingerprint, or name, the order of resolution is as follows:

1. If the identifier is an integer and there is an object of the relevant type
   with that integer as its ID number, :program:`doapi` uses that object.

2. For images, if there is an image whose slug equals the identifier,
   :program:`doapi` uses that image.

3. For SSH keys, if the identifier is in the form of an SSH public key
   fingerprint (16 colon-separated two-digit hexadecimal integers) and there is
   an SSH key with that fingerprint registered with the user's DigitalOcean
   account, :program:`doapi` uses that SSH key.

4. Otherwise, the identifier is assumed to be a name, and if there exists
   exactly one object of the relevant type with that name, :program:`doapi`
   uses that object.  If the name is shared by multiple objects, by default
   :program:`doapi` will exit without taking any action, displaying an error
   message that includes the ID numbers of all of the objects with that name.
   For subcommands that operate on lists of objects, this behavior can be
   changed by passing the :option:`--multiple` option to the subcommand,
   causing any names that refer to more than one object to be interpreted as a
   list of all of those objects in unspecified order.

In all cases, if the same object is specified more than once on the command
line, all occurrences after the first are ignored with a warning.


.. _universal:

Universal Options
'''''''''''''''''

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
'''''''''''''''

By default, all subcommands that perform non-atomic actions return immediately
after initiating the action, without waiting for it to complete.  They can be
made to instead wait until completion with the :option:`--wait` option, which
can be configured further with :option:`--wait-interval` and
:option:`--wait-time`, as described below:

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

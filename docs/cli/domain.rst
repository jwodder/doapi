.. currentmodule:: doapi

:program:`doapi-domain`
-----------------------

NAME
^^^^

:program:`doapi-domain` — manage DigitalOcean domains & domain records

SYNOPSIS
^^^^^^^^

.. Add ``doapi-domain [<universal options>]`` once "implicit show" is supported

::

    doapi-domain new <domain> <ip address>
    doapi-domain show [<domain> ...]
    doapi-domain delete <domain> ...

    doapi-domain new-record [--priority <int>] [--port <int>] [--weight <int>]
                            [--delete] <domain> <type> <name> <data>

    doapi-domain show-record <domain> [<record id> ...]

    doapi-domain update-record [--type <type>]
                               [--name <name>]
                               [--data <data>]
                               [--port     <int> | --no-port]
                               [--priority <int> | --no-priority]
                               [--weight   <int> | --no-weight]
                               <domain> <record id>

    doapi-domain delete-record <domain> <record id> [<record id> ...]

:program:`doapi-domain` also takes the :ref:`universal options <universal>`
common to all :program:`doapi` commands.

Domains are specified as the base domain name without any subdomains (e.g.,
``example.com``, never ``www.example.com``).  Records of a given domain are
specified by ID number.


:command:`new`
^^^^^^^^^^^^^^

::

    doapi-domain new <domain> <ip address>

Set up a domain name ``<domain>`` pointing to ``<ip address>``.  The new domain
is output as a `Domain` object converted to JSON.

Note that this command does not actually register a new domain name; it merely
configures DigitalOcean's nameservers to provide DNS resolution for the domain.
See `How To Set Up a Host Name with DigitalOcean
<https://www.digitalocean.com/community/tutorials/how-to-set-up-a-host-name-with-digitalocean>`_
for more information.


:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-domain show [<domain> ...]

Show domains.  If no domains are specified, all domains registered to the
account are shown.  The domains are output as a list of `Domain` objects
converted to JSON.


:command:`delete`
^^^^^^^^^^^^^^^^^

::

    doapi-domain delete <domain> ...

Delete domains.  If any of the given domains do not exist, nothing is deleted.
There is no output.


:command:`new-record`
^^^^^^^^^^^^^^^^^^^^^

::

    doapi-domain new-record [--priority <int>] [--port <int>] [--weight <int>]
                            [--delete] <domain> <type> <name> <data>

Add a new domain record with the given type, name, & data to domain
``<domain>``.  The new record is output as a `DomainRecord` object converted to
JSON.

Options
'''''''

.. program:: doapi-domain new-record

.. option:: --delete

    After creating the new record, delete any old records with the same type &
    name.

.. option:: --port <int>

    Specify the port on which the service is available (SRV records only)

.. option:: --priority <int>

    Specify the priority for the new record (SRV and MX records only)

.. option:: --weight <int>

    Specify the weight for the new record (SRV records only)


:command:`show-record`
^^^^^^^^^^^^^^^^^^^^^^

::

    doapi-domain show-record <domain> [<record id> ...]

Show records for domain ``<domain>``.  If no records are specified, all records
for the domain are shown.  The records are output as a list of `DomainRecord`
objects converted to JSON.


:command:`update-record`
^^^^^^^^^^^^^^^^^^^^^^^^

::

    doapi-domain update-record [--type <type>]
                               [--name <name>]
                               [--data <data>]
                               [--port     <int> | --no-port]
                               [--priority <int> | --no-priority]
                               [--weight   <int> | --no-weight]
                               <domain> <record id>

Modify one or more fields of a domain record.  The updated record is output as
a `DomainRecord` object converted to JSON.

Options
'''''''

.. program:: doapi-domain update-record

.. option:: --data <data>

    Set the record's data to ``<data>``

.. option:: --name <name>

    Set the record's name to ``<name>``

.. option:: --no-port

    Unset the record's port field

.. option:: --no-priority

    Unset the record's priority field

.. option:: --no-weight

    Unset the record's weight field

.. option:: --port <int>

    Set the record's port to ``<int>``

.. option:: --priority <int>

    Set the record's priority to ``<int>``

.. option:: --type <type>

    Set the record's type to ``<type>``

.. option:: --weight <int>

    Set the record's weight to ``<int>``


:command:`delete-record`
^^^^^^^^^^^^^^^^^^^^^^^^

::

    doapi-domain delete-record <domain> <record id> [<record id> ...]

Delete records of the given domain.  If any of the given records do not exist,
nothing is deleted.  There is no output.

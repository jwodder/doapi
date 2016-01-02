.. module:: doapi

``doapi-domain``
----------------

NAME
^^^^

``doapi-domain`` — manage DigitalOcean domains & domain records

SYNOPSIS
^^^^^^^^

.. Add ``doapi-domain [<universal options>]`` once "implicit show" is supported

::

    doapi-domain show [<domain> ...]
    doapi-domain new <domain> <ip address>
    doapi-domain delete <domain> ...

    doapi-domain show-record <DOMAIN> [<record id> ...]
    doapi-domain new-record [--priority <number>] [--port <number>] [--weight <number>] <domain> <type> <name> <data>
    doapi-domain set-record [--priority <number>] [--port <number>] [--weight <number>] <domain> <type> <name> <data>
        # `set` is like `new` but deletes any & all pre-existing records with
        # the same type & name.
    doapi-domain update-record [--type TYPE] [--name NAME] [--data DATA] [--priority PRIORITY | --no-priority] [--port PORT | --no-port] [--weight WEIGHT | --no-weight] <domain> <record id>
    doapi-domain delete-record <domain> <record id> ...

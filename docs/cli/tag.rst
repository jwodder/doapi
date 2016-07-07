.. module:: doapi

:program:`doapi-tag`
--------------------

NAME
^^^^

:program:`doapi-tag` — manage DigitalOcean tags

SYNOPSIS
^^^^^^^^

.. Add ``doapi-tag [<universal options>]`` once "implicit show" is supported

::

    doapi-tag new    <tag> ...
    doapi-tag show   [<tag> ...]
    doapi-tag update <tag> <new name>
    doapi-tag delete <tag> ...

:program:`doapi-tag` also takes the :ref:`universal options <universal>` common
to all :program:`doapi` commands.


:command:`new`
^^^^^^^^^^^^^^

::

    doapi-tag new <tag> ...

Create one or more new tags with the given names.  The new tags are output as
`Tag` objects converted to JSON.


:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-tag show [<tag> ...]

Show tags.  If no tags are specified, all tags registered to the account are
shown.  The tags are output as a list of `Tag` objects converted to JSON.

To list the individual resources with a given tag, use the :command:`show`
subcommand for the relevant resource type; e.g., to list all of the droplets
with a given tag, run :samp:`doapi-droplet show --tag={tag}`.


:command:`update`
^^^^^^^^^^^^^^^^^

::

    doapi-tag update <tag> <new name>

Update (i.e., rename) a tag.  The updated tag is output as a `Tag` object
converted to JSON.


:command:`delete`
^^^^^^^^^^^^^^^^^

::

    doapi-tag delete <tag> ...

Delete tags.  There is no output.

.. currentmodule:: doapi

:program:`doapi-image`
----------------------

NAME
^^^^

:program:`doapi-image` — manage DigitalOcean droplet images

SYNOPSIS
^^^^^^^^

.. Add ``doapi-image [<universal options>]`` once "implicit show" is supported

::

    doapi-image show     [-M|--multiple] [<image> ...]
    doapi-image show     {--application|--distribution|--type=<type>|--private}

    doapi-image update   [--unique] <image> <new name>

    doapi-image convert  [<wait options>] [-M|--multiple] <image> ...
    doapi-image transfer [<wait options>] [-M|--multiple] <region> <image> ...

    doapi-image act      [<wait options>] [-p|--params <JSON|@file>] [-M|--multiple] <type> <image> ...
    doapi-image actions  [--in-progress | --last] [-M|--multiple] <image> ...
    doapi-image wait     [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] <image> ...

    doapi-image delete   [-M|--multiple] <image> ...

:program:`doapi-image` also takes the :ref:`universal options <universal>`
common to all :program:`doapi` commands.

Images can be specified by ID number, slug (if any), or name.  A name that is
also a valid ID or slug is interpreted as such rather than as a name (and so
images with such names must be referred to by their ID instead).


:command:`show`
^^^^^^^^^^^^^^^

::

    doapi-image show [-M|--multiple] [<image> ...]
    doapi-image show {--application|--distribution|--type=<type>|--private}

Show images.  If no images or flags are specified, all images available to the
account are shown.  The images are output as a list of `Image` objects
converted to JSON.

Options
'''''''

.. program:: doapi-image show

.. option:: --application

    Only show application images

.. option:: --distribution

    Only show distribution images

.. option:: -M, --multiple

    Arguments that could refer to multiple images are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.

.. option:: --private

    Only show the user's private images

.. option:: --type=<type>

    Only show images of type ``<type>`` (``application``, ``distribution``, or
    something not otherwise implemented here)


:command:`update`
^^^^^^^^^^^^^^^^^

::

    doapi-image update [--unique] <image> <new name>

Update (i.e., rename) an image.  The updated image is output as an `Image`
object converted to JSON.

Options
'''''''

.. program:: doapi-image update

.. option:: --unique

    If ``<new name>`` is already in use by another image, fail with an error.
    Without this option, a warning will still be generated if ``<new name>`` is
    already in use.


:command:`convert`
^^^^^^^^^^^^^^^^^^

::

    doapi-image convert [<wait options>] [-M|--multiple] <image> ...

Convert one or more images to snapshots.  The `Action` objects thus produced
are output as a JSON list.

Options
'''''''

In addition to the :ref:`waiting options <waitopts>`, the :command:`convert`
subcommand takes the following:

.. program:: doapi-image convert

.. option:: -M, --multiple

    Arguments that could refer to multiple images are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.


:command:`transfer`
^^^^^^^^^^^^^^^^^^^

::

    doapi-image transfer [<wait options>] [-M|--multiple] <region> <image> ...

Transfer one or more images to another region (identified by its slug).  The
`Action` objects thus produced are output as a JSON list.

Options
'''''''

In addition to the :ref:`waiting options <waitopts>`, the :command:`transfer`
subcommand takes the following:

.. program:: doapi-image transfer

.. option:: -M, --multiple

    Arguments that could refer to multiple images are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.


:command:`act`
^^^^^^^^^^^^^^

::

    doapi-image act [<wait options>] [-p|--params <JSON|@file>] [-M|--multiple] <type> <image> ...

Perform an arbitrary action of type ``<type>`` (``convert``, ``transfer``, or
something otherwise not implemented here) on one or more images.  The `Action`
objects thus produced are output as a JSON list.

Options
'''''''

In addition to the :ref:`waiting options <waitopts>`, the :command:`act`
subcommand takes the following:

.. program:: doapi-image act

.. option:: -M, --multiple

    Arguments that could refer to multiple images are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.

.. option:: -p <data>, --params <data>

    A JSON object/dictionary of parameters to the action.  If ``<data>`` begins
    with "``@``", the rest of the argument (if there is any) is treated as a
    file from which to read the JSON; a filename of ``-`` causes data to be
    read from standard input.


:command:`actions`
^^^^^^^^^^^^^^^^^^

::

    doapi-image actions [--in-progress | --last] <image> ...

List all of the actions that have ever been performed on the given image(s).
The results are output as a JSON list containing a sublist of `Action` objects
for each image specified on the command line, in order.

Options
'''''''

.. program:: doapi-image actions

.. option:: --in-progress

    Show only the currently in-progress action on each image instead of a list
    of all actions.  If there is currently no in-progress action on an image,
    show ``null``.

.. option:: --last

    Show only the most recent action on each image instead of a list of all
    actions.  If multiple actions on a single image were triggered
    simultaneously, the choice of which to return is undefined.  If no actions
    were ever performed on an image, show ``null``.


:command:`wait`
^^^^^^^^^^^^^^^

::

    doapi-image wait [--wait-interval <seconds>] [--wait-time <seconds>] <image> ...

Wait for the currently in-progress actions on the given image(s) to either
complete or error out.  The finished actions are output as a list of `Action`
objects converted to JSON, with each action output (roughly) as soon as it
finishes.  If there are no actions currently in progress on a given image,
nothing will be output for it.

Options
'''''''

.. program:: doapi-image wait

.. option:: --wait-interval <seconds>

    How often to poll the server for the actions' current statuses; default
    value: 2 seconds

.. option:: --wait-time <seconds>

    The maximum number of seconds to wait for all actions to complete.  After
    this much time has passed since program invocation, any remaining
    in-progress actions will be output immediately without waiting for them to
    finish.

    If this option is not specified, :command:`wait` will wait indefinitely.


:command:`delete`
^^^^^^^^^^^^^^^^^

::

    doapi-image delete [-M|--multiple] <image> ...

Delete images.  If any of the given images do not exist, nothing is deleted.
There is no output.

Options
'''''''

.. program:: doapi-image delete

.. option:: -M, --multiple

    Arguments that could refer to multiple images are interpreted as such
    rather than using the default resolution rules; see :ref:`multiple` for
    more information.

.. module:: doapi

``doapi-image``
---------------

NAME
^^^^

``doapi-image`` — manage DigitalOcean droplet images

SYNOPSIS
^^^^^^^^

.. Add ``doapi-image [<universal options>]`` once "implicit show" is supported

::

    doapi-image show [-M|--multiple] [<image> ...]
    doapi-image show {--type=TYPE|--distribution|--application|--private}
    doapi-image update [--unique] <image> <new name>
    doapi-image delete [-M|--multiple] <image> ...
    doapi-image transfer [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] <region> <image> ...
    doapi-image convert [--wait] [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] <image> ...

    doapi-image act [--wait] [-p|--params <JSON dict> | -P|--param-file <file>] [-M|--multiple] <type> <image> ...
    doapi-image actions [--last | --in-progress] [-M|--multiple] <image> ...
    doapi-image wait [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] <image> ...

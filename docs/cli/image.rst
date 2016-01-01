.. module:: doapi

``doapi-image``
---------------

Synopsis
^^^^^^^^

.. Add ``doapi-image [<universal options>]`` once "implicit show" is supported

::

    doapi-image show [-M|--multiple] [<image> ...]
    doapi-image show {--type=TYPE|--distribution|--application|--private}
    doapi-image update [--unique] <image> <new name>
    doapi-image delete [-M|--multiple] <image> ...
    doapi-image transfer [-M|--multiple] <region> <image> ...
    doapi-image convert [-M|--multiple] <image> ...

    doapi-image act [-p|--params <JSON dict> | -P|--param-file <file>] [-M|--multiple] <type> <image> ...
    doapi-image actions [--last | --current] [-M|--multiple] <image> ...
    doapi-image wait [--wait-time <seconds>] [--wait-interval <seconds>] [-M|--multiple] <image> ...

.. module:: doapi

``doapi-action``
----------------

Synopsis
^^^^^^^^

.. Add ``doapi-action [<universal options>]`` once "implicit show" is supported

::

    doapi-action show [<id> ...]
    doapi-action show {--last | --current}
    doapi-action wait [--wait-time <seconds>] [--wait-interval <seconds>] [<id> ...]
        # Not specifying any arguments means "wait on all in-progress actions"
    doapi-action resource <id> ...  # fetch resource
    doapi-action resource {--last | --current}

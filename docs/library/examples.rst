Examples
========

::

    # Shut.
    # Down.
    # EVERYTHING.

    actions = []

    for drop in manager.fetch_all_droplets():
        if drop.active:
            actions.append(drop.shutdown())

    # `list` forces the generator returned by `wait_actions` to be fully
    # evaluated, thereby making Python wait until all of the shutdown actions
    # have completed.
    list(manager.wait_actions(actions))

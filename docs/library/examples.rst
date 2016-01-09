Examples
========

::

    # Shut.
    # Down.
    # EVERYTHING.

    actions = []

    for droplet in manager.fetch_all_droplets():
        if droplet.active:  # Only droplets that are already up can be shut down.
            actions.append(droplet.shutdown())

    # `list` forces the generator returned by `wait_actions` to be fully
    # evaluated, thereby making Python wait until all of the shutdown actions
    # have completed.
    list(manager.wait_actions(actions))

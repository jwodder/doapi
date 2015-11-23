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
    list(manager.wait_actions(actions))

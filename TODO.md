- Document everything!
- Bring the code in line with PEP 8?
- Add tests
- A lot of the code relies on the assumptions that an object cannot have more
  than one in-progress action running on it at a time and that, if there is an
  in-progress action, it the most recent and the first listed.  Confirm this.
    - Creating a floating IP assigned to a droplet produces two actions (create
      & assign) that (always?) have the same start time and can be listed with
      the 'assign' (which completes later and has a greater ID) coming after
      the 'create'.

# Command-Line Interface

- Decide on a name uniqueness policy
- Implement `doapi-domain`
- Add error handling
- Use docopt instead of argparse?
- Add checks to mutating commands to ensure that the same object isn't listed
  on the command line twice
- Add metavars and other --help data
- Confirm the assumption that private images are the only kind of images that
  can be acted on
- Handle fetching actions of objects that are being deleted

# Library

- Add a class for droplets' `next_backup_window` fields
- Look into the correctness of the naïve implementation of `fetch_last_action`
- Look into whether I should be relying on the fetchability of
  `/v2/floating_ips/$IP_ADDR/actions`
- If an error occurs inside `_wait`, it should return the remaining objects
  somehow (by yielding them? by attaching them to the exception?) before
  letting the error propagate out
- Look into whether fetching an action via `/v2/actions/$ACTION_ID` is always
  equivalent to fetching via
  `/v2/$RESOURCE_TYPE/$RESOURCE_ID/actions/$ACTION_ID`

## Naming things

- Rename the `doapi` class to `Manager`?

- Document everything!
    - Write a README
    - Stop listing `DOAPIError` under (almost) every method and just say once
      that it can be thrown by anything that uses the API?
- Add tests
    - Test giving non-ASCII names to things
- Figure out the minimum requests & six versions required and add them to
  setup.py
    - doapi was developed using requests v.2.2.1 and six v.1.5.2.

# Command-Line Interface

- Decide on a name uniqueness policy
- Use docopt or argh instead of argparse?
- Add checks to mutating commands to ensure that the same object isn't listed
  on the command line twice
- Add metavars and other --help data
- Handle fetching actions of objects that are being deleted
- `doapi-droplet new`:
    - When a new SSH key is automatically created from a file, should only the
      file's basename be used for the key name?
        - Doing this would then bring up the issue of whether `--unique` should
          make SSH key creation --unique as well
    - Whenever a new SSH key is created, a message should be printed to stderr
    - If an error occurs in the middle of creating droplets (e.g., if the
      user's droplet limit is exceeded), print out the droplets that have been
      created so far
- Give `doapi-domain update-record` a way to set priority, port, & weight to
  `null`?
- Warn whenever the user creates a droplet, image, or SSH key with a name
  that's already in use (with an option to turn off the warnings?)

# Library

- Look into BCP for naming of REST API "manager" objects like `doapi`
- Add a class for droplets' `next_backup_window` fields
    - These objects apparently consist of just `"start"` and `"end"` fields
      containing timestamps.
- If an error occurs inside `_wait`, it should return the remaining objects
  somehow (by yielding them? by attaching them to the exception?) before
  letting the error propagate out
- Should `doapi` objects send all their requests through a `requests.Session`?
  Should the user be able to supply their own `Session` object to use?
- Wait operations should take into account the amount of time elapsed between
  `yield`s when deciding how long to sleep
- Add constants for the possible droplet statuses for passing to
  `wait_droplets` and `Droplet.wait`
- The `region` field of `Actions` should be stored as a `Region` object

# API Compatibility & Correctness

- A lot of the code relies on the assumptions that an object cannot have more
  than one in-progress action running on it at a time and that, if there is an
  in-progress action, it the most recent and the first listed.  Confirm this.
    - Creating a floating IP assigned to a droplet produces two actions (create
      & assign) that (always?) have the same start time and can be listed with
      the 'assign' (which completes later and has a greater ID) coming after
      the 'create'.
- [For the CLI] Confirm the assumption that private images are the only kind of
  images that can be acted on
- Look into whether priority and/or weight of domain records can be nonintegral
- Look into the correctness of the naïve implementation of `fetch_last_action`
- Look into whether I should be relying on the fetchability of
  `/v2/floating_ips/$IP_ADDR/actions`
- Look into whether fetching an action via `/v2/actions/$ACTION_ID` is always
  equivalent to fetching via
  `/v2/$RESOURCE_TYPE/$RESOURCE_ID/actions/$ACTION_ID`

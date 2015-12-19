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
- When `doapi-droplet` automatically creates a new SSH key from a file, should
  it only use the file's basename for the key name?
    - Doing this would then bring up the issue of whether passing `--unique` to
      `doapi-droplet new` should cause SSH key creation to be --unique as well
- Give `doapi-domain update-record` a way to set priority, port, & weight to
  `null`?

# Library

- Look into BCP for naming of REST API "manager" objects like `doapi`
- Add a class for droplets' `next_backup_window` fields
    - These objects apparently consist of just `"start"` and `"end"` fields
      containing timestamps.
- Rename `JSObject` etc. to `Resource` or `DOResource`?
- If an error occurs inside `_wait`, it should return the remaining objects
  somehow (by yielding them? by attaching them to the exception?) before
  letting the error propagate out
- Should `doapi` objects send all their requests through a `requests.Session`?
- Wait operations should take into account the amount of time elapsed between
  `yield`s when deciding how long to sleep
- Add constants for the possible droplet statuses for passing to
  `wait_droplets` and `Droplet.wait`
- Add a public function/static method for getting the user's API token using
  the same rules as the command-line programs?
- The `region` field of `Actions` should be stored as a `Region` object
- I don't think request URLs will be constructed correctly when the API
  endpoint has a nonempty path component.  Address this.

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

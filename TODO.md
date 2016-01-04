- Document everything!
    - Write a README
    - Add a separate section to the documentation for private/internal methods
      & classes
- Add tests
    - Test giving non-ASCII names to things

# Command-Line Interface

- Use docopt or argh instead of argparse?
- Add checks to mutating commands to ensure that the same object isn't listed
  on the command line twice
- Add metavars and other `--help` data
- Handle fetching actions of objects that are being deleted
- `doapi-droplet new`:
    - When automatically creating SSH keys, use the key's comment field (when
      it exists) instead of the filename for the key name
        - This brings up the issue of whether `--unique` should make SSH key
          creation --unique as well
    - If an error occurs in the middle of creating droplets (e.g., if the
      user's droplet limit is exceeded), print out the droplets that have been
      created so far
- `doapi-image show`: Forbid using `--multiple` with `--type`, `--private`,
  etc.
- Come up with a better name for `--multiple`?
- When `--multiple` is in effect, should image slugs that are also names of
  available images be interpreted as both? (and likewise for SSH keys &
  fingerprints?)
    - What about IDs that are also valid names for droplets/images/SSH keys?
      Are such names even allowed?
- Eliminate `doapi-domain set-record` and give `doapi-domain new-record` an
  option for enabling `set-record`'s behavior instead?

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
- Rename `doapi.create_droplets` to `doapi.create_multiple_droplets`?

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
- Look into whether fetching an action via `/v2/actions/$ACTION_ID` is always
  equivalent to fetching via
  `/v2/$RESOURCE_TYPE/$RESOURCE_ID/actions/$ACTION_ID`

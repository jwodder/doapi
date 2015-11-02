- Document everything!
- Handle all items marked with "`TODO`" or "`###`" in the code
- Bring the code in line with PEP 8
- Add tests
- A lot of the code relies on the assumption that an object cannot have more
  than one in-progress action running on it at a time.  Confirm this.

# Command-Line Interface

- Add error handling
- Use docopt instead of argparse?
- Add checks to mutating commands to ensure that the same object isn't listed
  on the command line twice
- Add metavars and other --help data

# Library

- Add a class for droplets' `next_backup_window` fields
- Look into the correctness of the naïve implementation of `fetch_last_action`
- Look into whether I should be relying on the fetchability of
  `/v2/floating_ips/$IP_ADDR/actions`
- Prevent classes without IDs from being initialized with an int
    - Add a `JSObjectWithID` class that handles all initialization from ints
      and defines `__int__`
- If an error occurs inside `_wait`, it should return the remaining objects
  somehow (by yielding them? by attaching them to the exception?) before
  letting the error propagate out
- Rethink the utility/design sense of having `_meta_attrs` for anything other
  than `doapi_manager`
- Should `url()` and `action_url()` methods automatically use
  `self.doapi_manager.endpoint` as an endpoint when `self.doapi_manager` is
  defined?  Should they then be properties?
- Get rid of `JSObject._asdict`?

- Try to be more consistent regarding when deep copies of objects are created.
    - Passing an image, region, etc. object to `Droplet` (e.g., when copying a
      droplet) causes it to be deep-copied.
    - The droplet reference passed to a network, kernel, backup, or snapshot
      object is not deep-copied.

## Naming things

- Look into more appropriate/standard names for `_asdict`
- Rename the `doapi` class to `Manager`?
- Should the `Network` class be renamed `Interface` or something like that?

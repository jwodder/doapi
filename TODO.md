- Document everything!
- Handle all items marked with "`TODO`" or "`###`" in the code
- Bring the code in line with PEP 8?
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
- If an error occurs inside `_wait`, it should return the remaining objects
  somehow (by yielding them? by attaching them to the exception?) before
  letting the error propagate out

## Naming things

- Rename the `doapi` class to `Manager`?
- Should the `Network` class be renamed `Interface` or something like that?

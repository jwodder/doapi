# Externals

- Add arguments for controlling pagination

- Add a command for waiting for the most recent action on each droplet in a
  given list to finish
    - Idea: The command for waiting on droplet actions can take arguments as
      either "`<DROPLET>:<ACTION>`" or "`<DROPLET>:`" (or just "`<DROPLET>`"?),
      the latter indicating the most recent action.

- Droplet action commands that require the droplet to be off should have a flag
  for ensuring the droplet is off beforehand

# Internals

- If a `wait_*` method receives a KeyboardInterrupt, it should return
  immediately

- Rethink how the `wait_*` commands return their results; options:
    - Current: Return a tuple of (finished, [errored,] unfinished) objects with
      the first two being in the order they ended
    - Yield each object as it finishes
    - Return a list of objects in the same order as passed to the function

- Look into more appropriate/standard names for `_asdict`

- Try to find a way to return `meta` fields and the `RateLimit-*` headers
  returned in responses
    - Give `doapi` attributes for storing these values as of the most recent
      HTTP request?

- Rename `wait_droplets_status` to `wait_droplets`, default `status` to `None`,
  and wait for the most recent action on each droplet to complete/error when
  `status is None`

- Make the code work in both Python 2 and Python 3
- Bring in line with PEP 8

- Add methods to `doapi` for fetching SSH keys by name

- Add the ability to fetch images by slug

- Give `droplet` and `image` (and `doapi`?) methods for fetching the most
  recent action

- `doapi`: Add the ability to configure pagination

- Should all JSON objects (kernels, droplet upgrades, etc.) have corresponding
  classes?

- Should JSObject be made into a Mapping (that skips `doapi_manager`)?  It
  would allow `dict(instance)` to work, eliminating the need for `_asdict`
    - Should JSObject store all of its non-`doapi_manager` attributes in a
      dedicated dict attribute?

- Rename all of the `fetch_foos` methods to `fetch_all_foos`?

- Change the arguments of `JSObject.__init__` to `(self, state=None, **attrs)`,
  thereby simplifying `doapi.droplet` etc. a bit?

- Replace `minibin/*` with unit tests that just invoke the command-line client

- There's something wrong with fetching a droplet's neighbors.

- Implement accounts, domain records, and domains

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

## Features

- `doapi`: Add the ability to configure pagination
- Implement accounts, domain records, and domains
- Add methods to `doapi` for fetching SSH keys by name
- Add the ability to fetch images by slug
- Give `droplet` and `image` (and `doapi`?) methods for fetching the most
  recent action
- Try to find a way to return `meta` fields and the `RateLimit-*` headers
  returned in responses
    - Give `doapi` attributes for storing these values as of the most recent
      HTTP request?
- There's something wrong with fetching a droplet's neighbors.

## Structure

- Should all JSON objects (kernels, droplet upgrades, etc.) have corresponding
  classes?

- Should JSObject be made into a Mapping (that skips `doapi_manager`)?  It
  would allow `dict(instance)` to work, eliminating the need for `_asdict`
    - Should JSObject store all of its non-`doapi_manager` attributes in a
      dedicated dict attribute?

- Change the arguments of `JSObject.__init__` to `(self, state=None, **attrs)`,
  thereby simplifying `doapi.droplet` etc. a bit?

## Other

- Document everything!
- If a `wait_*` method receives a KeyboardInterrupt, it should return
  immediately
- Look into more appropriate/standard names for `_asdict`
- Rename all of the `fetch_foos` methods to `fetch_all_foos`?
- Bring in line with PEP 8
- Make the code work in both Python 2 and Python 3
- Replace `minibin/*` with unit tests that just invoke the command-line client
- Should `doapi.__init__` take a default `maxwait` value?

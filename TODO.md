# Externals

- Add arguments for controlling pagination

- Add a command for waiting for the most recent action on each droplet in a
  given list to finish
    - Idea: The command for waiting on droplet actions can take arguments as
      either "`<DROPLET>:<ACTION>`" or "`<DROPLET>:`" (or just "`<DROPLET>`"?),
      the latter indicating the most recent action.

- Droplet action commands that require the droplet to be off should have a flag
  for ensuring the droplet is off beforehand

- Add a way to get the current rate limit

- Add an option (for non-raw commands) for printing the response headers to
  stderr?

# Internals

## Features

- Add methods to `doapi` for fetching SSH keys by name
- Add the ability to fetch images by slug
- There's something wrong with fetching a droplet's neighbors.

## Structure

- Should the "networks" field of droplets have its own class?

- Should JSObject be made into a Mapping (that skips `doapi_manager`)?  It
  would allow `dict(instance)` to work, eliminating the need for `_asdict`
    - Should JSObject store all of its non-`doapi_manager` attributes in a
      dedicated dict attribute?
    - cf. <https://github.com/kennethreitz/requests/blob/8b5e457b756b2ab4c02473f7a42c2e0201ecc7e9/requests/packages/urllib3/_collections.py#L107> for how to subclass `dict`

- Give `doapi` `account`, `kernel`, etc. methods?

- Give Kernel & Image `fetch_droplet` methods
- Give DomainRecord a `fetch_domain` method

## Other

- Document everything!
- If a `wait_*` method receives a KeyboardInterrupt, it should return
  immediately
- Look into more appropriate/standard names for `_asdict`
- Bring in line with PEP 8
- Make the code work in both Python 2 and Python 3
- Replace `minibin/*` with unit tests that just invoke the command-line client
- Should `doapi.__init__` take a default `maxwait` value?
- Define `Image.__str__` to return the slug?
- Define `SSHKey.__str__` to return the fingerprint?
- Should any classes have `__str__` methods that return `name` attributes?
- Rename `action.done` to `action.ended`?
- Should the `url` methods be renamed to avoid confusion with droplet upgrades'
  "url" fields?

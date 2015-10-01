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
- Add methods to `doapi` for fetching images by name?

## Structure

- Should the "networks" field of droplets have its own class(es)?

- Should JSObject be made into a Mapping (that skips `doapi_manager`)?  It
  would allow `dict(instance)` to work, eliminating the need for `_asdict`
    - Should JSObject store all of its non-`doapi_manager` attributes in a
      dedicated dict attribute?
    - cf. <https://github.com/kennethreitz/requests/blob/8b5e457b756b2ab4c02473f7a42c2e0201ecc7e9/requests/packages/urllib3/_collections.py#L107> for how to subclass `dict`
    - Idea: Attributes are divided into two groups, "API" (which are preserved
      when converted to JSON and show up in iteration) and "meta" (which are
      not).  `foo.x` fetches a meta attribute if it exists, an API attribute
      otherwise.  `foo['x']` always fetches an API attribute.  `foo.x = y`
      always(?) sets a meta attribute; to set an API attribute, do `foo['x'] =
      y`.

- Give `doapi` `account`, `kernel`, etc. methods?

- Should the `fetch_all_*` methods return generators instead of lists?

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
- Should slugs be allowed as alternative identifiers for images the same way
  fingerprints are for SSH keys?  (This depends on the circumstances under
  which the API will allow a slug in place of an ID in the first place.)

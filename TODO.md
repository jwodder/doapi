- Double-check DO's official term for API keys/tokens

# Externals

- Droplet action commands that require the droplet to be off should have a flag
  for ensuring the droplet is off beforehand
- Add a way to get the current rate limit
- When getting lists of objects for multiple items (e.g., getting the snapshots
  for a list of more than one droplet), should the output be a list of lists of
  objects?
- Add `--all` options for everything that takes a list of objects to operate
  on? (except the "delete" commands; that'd be bad)
- All operations should be doable in batches via an option (mutually exclusive
  with positional arguments) for reading a JSON list of objects (specifying
  what to operate on and any arguments; instead of an object, one can use a
  string or int, which is treated like an object ID given on the command line)
  from a file.

- After everything else is done, implement config files for specifying default
  values for:
    - API key
    - file containing API key
    - timeout
    - endpoint
    - wait time
    - wait interval
    - whether to wait/what operations to wait on?
    - whether to enforce name uniqueness among droplets, SSH keys, and/or images
    - parameters to pass when creating a droplet

# Internals

- Handle all items marked with "`TODO`" or "`###`" in the code

## Structure

- Make JSObject into a Mapping/MutableMapping that skips "meta" attributes,
  eliminating the need for `_asdict`
    - Attributes are divided into two groups, "API" (which are preserved when
      converted to JSON and show up in iteration) and "meta" (which are not).
      `foo.x` fetches a meta attribute if it exists, an API attribute
      otherwise.  `foo['x']` always fetches an API attribute.  `foo.x = y`
      always(?) sets a meta attribute; to set an API attribute, do `foo['x'] =
      y`.
    - API attributes are stored in a private dict meta attribute
    - cf. <https://github.com/kennethreitz/requests/blob/8b5e457b756b2ab4c02473f7a42c2e0201ecc7e9/requests/packages/urllib3/_collections.py#L107> for how to subclass `dict` instead

- Give `doapi` `account`, `kernel`, etc. methods?
- Should the `fetch_all_*` methods return generators instead of lists?
- Define `__int__` in `JSObject`?
- Give `Network` a meta attribute for the IP version
- Add a class for droplets' `next_backup_window` fields

- Try to be more consistent regarding when deep copies of objects are created.
    - Passing an image, region, etc. object to `Droplet` (e.g., when copying a
      droplet) causes it to be deep-copied.
    - The droplet reference passed to a network, kernel, backup, or snapshot
      object is not deep-copied.

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

- Handle all items marked with "`TODO`" or "`###`" in the code
- Double-check DO's official term for API keys/tokens
- Bring the code in line with PEP 8 and pylint
- Make the code work in both Python 2 and Python 3
- Add support for floating IPs

# Command-Line Interface

- Add error handling
    - When creating/operating on multiple objects and one produces an error,
      there should be an option for continuing with the rest (including
      waiting?).
- Droplet action commands that require the droplet to be off should have a flag
  for ensuring the droplet is off beforehand
- Add a way to get the current rate limit
- Add `--all` options for everything that takes a list of objects to operate
  on? (except the "delete" commands; that'd be bad)
- Make `doapi-TYPE` a synonym for `doapi-TYPE show`, which should list all
  objects of the given type
- Give `doapi-regions` and `doapi-sizes` "`show`" commands for fetching only
  specific regions/sizes (and change the names of the commands to singular?)
- `doapi-droplet`:
    - Add an option (`--ignore`?) for not creating any droplets that already
      exist but printing out the pre-existing droplets anyway
    - Add synonyms for some actions:
        - `on` = `power-on`
        - `off` = `power-off`
        - `backups-off` = `disable-backups`
        - `set-kernel` = `change-kernel`
        - `rekernel` = `change-kernel` ?
        - `chkernel` = `change-kernel` ?
        - [SOMETHING shorter than "enable-private-networking"]
        - [others?]
    - Rename the `upgrades` and `snapshots` commands so as to eliminate
      confusion with `upgrade` and `snapshot`
- Use docopt instead of argparse?
- Prevent creation of objects whose name could be confused with an ID,
  fingerprint (for SSH keys), or slug (for images) unless some option
  (`--force`?) is given.
- `doapi-sshkey`:
    - Add an option for only creating if there isn't already a key with the
      same fingerprint (and another for returning the pre-existing key in that
      case?)
        - Do the same thing for key names?
    - Add an option for passing the entire key as a string

- For second release: All operations should be doable in batches via an option
  (mutually exclusive with positional arguments) for reading a JSON list of
  objects (specifying what to operate on and any arguments; instead of an
  object, one can use a string or int, which is treated like an object ID given
  on the command line) from a file.
    - cf. the intended `--json` option to `doapi-droplet new`

- For third release: implement config files for specifying default values for:
    - API key
    - file containing API key
    - timeout
    - endpoint
    - wait time
    - wait interval
    - whether to wait/what operations to wait on?
    - whether to enforce name uniqueness among droplets, SSH keys, and/or
      images?
    - default parameters to pass when creating a droplet

# Library

- Fix `JSObject.__repr__`'s handling of meta attributes
    - Show `doapi_manager` and DomainRecord's `domain`
        - Should `doapi_manager` be omitted from nested objects?
    - Do not show `_meta_attrs` (which isn't supposed to be in `vars()` anyway)
      or Network's `ip_version`
    - Do not show `droplet` when recursing inside a droplet
        - Only show `droplet` as an int?
- Rethink giving `doapi` a `__repr__` method (Showing the API key is bad,
  right?)
- Add the ability to wait for a droplet to become unlocked (or locked?)

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
    - cf. UserDict

- Try to be more consistent regarding when deep copies of objects are created.
    - Passing an image, region, etc. object to `Droplet` (e.g., when copying a
      droplet) causes it to be deep-copied.
    - The droplet reference passed to a network, kernel, backup, or snapshot
      object is not deep-copied.

- Give `doapi` `account`, `kernel`, etc. methods?
- Should the `fetch_all_*` methods return generators instead of lists?
- Add a class for droplets' `next_backup_window` fields

## Other

- Document everything!
- Look into more appropriate/standard names for `_asdict`
- Replace `minibin/*` with unit tests that just invoke the command-line client
- Should `doapi.__init__` take a default `maxwait` value?
- Should any classes have `__str__` methods that return `name` attributes?
- Rename `action.done` to `action.ended`?
- Should the `url` methods be renamed to avoid confusion with droplet upgrades'
  "url" fields?
- Should slugs be allowed as alternative identifiers for images the same way
  fingerprints are for SSH keys?  (This depends on the circumstances under
  which the API will allow a slug in place of an ID in the first place.)
- Look into the correctness of the naïve implementation of `fetch_last_action`
- Should the `Network` class be renamed `Interface` or something like that?
- Make `DomainRecord` more robust with regards to potentially lacking a
  `doapi_manager` and/or `domain` object (cf. `JSObjectWithDroplet`)
- Rename the `doapi` class to `Manager`?

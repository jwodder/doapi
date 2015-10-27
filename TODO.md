- Document everything!
- Handle all items marked with "`TODO`" or "`###`" in the code
- Bring the code in line with PEP 8 and pylint
- Replace `minibin/*` with unit tests that just invoke the command-line client

# Command-Line Interface

- Add error handling
- Use docopt instead of argparse?
- Add `--wait` options to `doapi-floating-ip`'s actions
- Add a `-V`/`--version` option

# Library

- Should the `fetch_all_*` methods return generators instead of lists?
- Add a class for droplets' `next_backup_window` fields
- Look into the correctness of the naïve implementation of `fetch_last_action`
- Look into whether I should be relying on the fetchability of
  `/v2/floating_ips/$IP_ADDR/actions`
- Prevent classes without IDs from being initialized with an int
- If an error occurs inside `_wait`, it should return the remaining objects
  somehow (by yielding them? by attaching them to the exception?) before
  letting the error propagate out
- Rethink the utility/design sense of having `_meta_attrs` for anything other
  than `doapi_manager`
- Add a function (or method?) for recursively converting a JSObject to a `dict`
    - name: `.primitive()`?
    - The resulting dicts will lack any meta attributes.

- Try to be more consistent regarding when deep copies of objects are created.
    - Passing an image, region, etc. object to `Droplet` (e.g., when copying a
      droplet) causes it to be deep-copied.
    - The droplet reference passed to a network, kernel, backup, or snapshot
      object is not deep-copied.

- Fix `JSObject.__repr__`'s handling of meta attributes
    - Show `doapi_manager` and DomainRecord's `domain`
        - Should `doapi_manager` be omitted from nested objects?
    - Do not show `_meta_attrs` (which isn't supposed to be in `vars()` anyway)
      or Network's `ip_version`
    - Do not show `droplet` when recursing inside a droplet
        - Only show `droplet` as an int?

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
    - Making JSObject a subclass of `dict` will lead to subtle bugs when an
      object is passed to a constructor of a different type and used
      successfully to update the new object's state

## Naming things

- Look into more appropriate/standard names for `_asdict`
- Should the `url` methods be renamed to avoid confusion with droplet upgrades'
  "url" fields?
- Rename the `doapi` class to `Manager`?
- Should the `Network` class be renamed `Interface` or something like that?

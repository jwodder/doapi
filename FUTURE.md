# Features for Future Releases

- Make the code work in both Python 2 and Python 3
- Add the ability to wait for a droplet to become unlocked (or locked?)

## Command-Line Interface

- When creating/operating on multiple objects and one produces an error, there
  should be an option for continuing with the rest (including waiting?)

- Droplet action commands that require the droplet to be off should have a flag
  for ensuring it's off beforehand

- Give `doapi-droplet` commands that simply ensure that their arguments are
  on/off

- Add `--all` options for everything that takes a list of objects to operate
  on? (except the "delete" commands; that'd be bad)
    - At the very least, this should be done for all of the commands that
      simply fetch data without changing anything.
    - Instead of having an `--all` option, just fetch everything when no
      objects are specified?

- Running just `doapi-TYPE` (or `doapi TYPE`) should be equivalent to
  `doapi-TYPE show`.

- `doapi-droplet new`: Add an option for not creating a droplet if the name is
  already in use but instead returning the pre-existing droplet
    - Only do this when there's only one pre-existing object (erroring
      otherwise) ?

- `doapi-droplet`: Add synonyms for some actions:
    - `on` = `power-on`
    - `off` = `power-off`
    - `backups-on` = `enable-backups`
    - `backups-off` = `disable-backups`
    - `set-kernel` = `change-kernel`
    - `rekernel` = `change-kernel` ?
    - `chkernel` = `change-kernel` ?
    - [SOMETHING shorter than "enable-private-networking"]
    - [others?]

- `doapi-<ssh-key/image>`: Allow `rename` as a synonym of `update`?
- `doapi-droplet`: Allow `update` as a synonym of `rename`?

- Prevent creation of objects whose name could be confused with an ID,
  fingerprint (for SSH keys), or slug (for images) unless some option
  (`--force`?) is given

- `doapi-ssh-key`:
    - Add an option for only creating if there isn't already a key with the
      same fingerprint (and another for returning the pre-existing key in that
      case?)
        - Do the same thing for key names?
    - Add an option for passing the entire key as a string

- All operations should be doable in batches via an option (mutually exclusive
  with positional arguments) for reading a JSON list of objects (specifying
  what to operate on and any arguments; instead of an object, one can use a
  string or int, which is treated like an object ID given on the command line)
  from a file.
    - Also give plain `doapi` a batch mode for executing arbitrary actions on
      arbitrary objects
    - better idea: Instead of giving every command & subcommand a batch option,
      add a `doapi-batch` command for performing batch operations
    - cf. the draft `--json <file>` option to `doapi-droplet new`:

        > A JSON array (or an object, which is treated as an array of one) is
        > read from <file> (which may be '-'), the -i/-s/-r values are applied
        > to those objects that are missing them, and the droplets are created
        > from the objects.  When --json is given, no `name` arguments should
        > be given.

- Implement config files for specifying default values for:
    - API token
    - file containing API token
    - timeout
    - endpoint
    - wait time
    - wait interval
    - whether to wait/what operations to wait on?
    - whether & when to enforce name uniqueness among droplets, SSH keys, &
      images
        - This will necessitate also adding (or overloading?) command-line
          options for overriding the config file's uniqueness policies and
          setting the policies back to their defaults.
            - Make `--unique` also set fetch & operate commands back to
              erroring on duplicate names
            - Make `--multiple`(?) also set creation commands back to allowing
              non-unique names
    - default parameters to pass when creating a droplet
    - whether to allow misleading-looking names for objects

- For `doapi-<droplet/image>`, allow the user to specify individual actions of
  an object by writing `object@num`, where `num` is `0` (`1`?) for the most
  recent action, `1` (`-1`? `2`?) for the action before that, etc.

- For `doapi-droplet restore`, allow the user to specify a backup by how many
  backups back to go; e.g., `@0` (`@1`?) is the most recent backup, `@1` is the
  one before that, etc.

- Let the user specify an unknown status to `doapi-droplet wait` if the
  `--force`(?) option is used

- Give `doapi-region` and `doapi-size` "`show`" commands for fetching only
  specific regions/sizes

- Give the `show` commands an `--ignore` option for skipping objects that don't
  exist?

- Give the `delete` commands an `--ignore` option for skipping objects that
  don't exist

- Give all commands that either have `--wait` (except 'new') or are 'wait' an
  option for dumping the manipulated objects instead of the completed actions
    - Because fetching objects while an action is still in progress on them
      doesn't seem that useful/meaningful, this will only be available to
      "waiters" and will imply `--wait`.

- Give `doapi-<droplet/image/floating-ip> delete` waiting options for waiting
  on each object's "destroy" action

- Add a single-character abbreviation for `--api-token-file`

- `doapi-droplet`: Give `shutdown`, `power-off`, and `power-on` options to make
  them skip over any droplets that are already off/on (or should that be the
  default behavior?)
    - Add similar idempotency for `enable-backups`, `disable-backups`,
      `enable-ipv6`, and `enable-private-networking`?

- Give `doapi-domain` commands for only showing records with a given type or
  name?

- Add a way to force `-K` arguments to `doapi-droplet new` to always be
  interpreted as filenames

- Add an option to cause error results to be returned alongside non-errors in
  output lists?

### Internals

- When not all objects of a type have been cached, labels that are valid IDs
  (or fingerprints or potential slugs) should not cause everything to be
  fetched (but the result should still be cached)

## Library

- Should slugs be allowed as alternative identifiers for images the same way
  fingerprints are for SSH keys?  (This depends on the circumstances under
  which the API will allow a slug in place of an ID in the first place.)
- Make `DomainRecord` more robust with regards to potentially lacking a
  `doapi_manager` and/or `domain` object or having a string for a `domain`
  object (cf. `ResourceWithDroplet`)
- Give `doapi` `account`, `kernel`, etc. methods?
- Give `doapi` a `wait_objects` method that fetches each input object's last
  action, waits for it to complete, and returns the object fetched anew?
    - Add special handling for Actions that just waits on & returns them
      normally?
- Add a function (or method?) for recursively converting a Resource to a `dict`
    - name: `.primitive()`? `to_json`?
    - The resulting dicts should lack any meta attributes.
- Fix `Resource.__repr__`'s handling of meta attributes
    - Show `doapi_manager` and DomainRecord's `domain`
        - Should `doapi_manager` be omitted from nested objects?
    - Do not show `_meta_attrs` (which isn't supposed to be in `vars()` anyway)
      or Network's `ip_version`
    - Do not show `droplet` when recursing inside a droplet
        - Only show `droplet` as an int?
- Give `fetch_<specific object>` methods an argument to make them return `None`
  when the object doesn't exist/returns a 404 instead of erroring?
- Store timestamps as `datetime` objects?
- Add a public function/static method for getting the user's API token using
  the same rules as the command-line programs?
- Give `Droplet` methods for simply ensuring that the droplet is on/off? (i.e.,
  that don't error if it's already on/off)
- Give `Droplet` one or more methods that combine a "power off/on" action with
  a regular droplet action so that the user can execute the latter action
  properly without too much code
    - Doing this on multiple droplets in parallel _must_ be supported

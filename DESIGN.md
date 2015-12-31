# Design Decisions Made for the CLI

- There are no options for controlling pagination.  The only instance where
  pagination should have an effect on the outcome is for raw requests, and for
  those the user can just append `?per_page=` to the path.
- When getting lists of objects for multiple items (e.g., getting the snapshots
  for a list of more than one droplet), the output is a list of lists of
  objects.
- Operations that take mandatory arguments beyond just the objects to operate
  on (e.g., renaming a droplet) should only allow the user to specify one
  object to operate on at a time, as the other positional arguments are needed
  for the extra arguments.
    - `doapi-droplet new` gets a pass because (a) there's no obvious order to
      put the image, region, & size in, and (b) future features are planned
      that would allow the user to leave out some or all of these arguments.
- `doapi-droplet`: `show-upgrades` and `show-snapshots` are named as such
  (instead of "`upgrades`" and "`snapshots`") in order to avoid confusion with
  `upgrade` and `snapshot`.
- Regions & sizes specified on the command line will not be checked for
  validity before using them; you'd get an error either way, and performing the
  check on the client side just adds more work and API requests.
- Operations that take mandatory extra arguments (e.g., renaming &
  snapshotting) and thus only allow you to specify one object on the command
  line should not be given `--multiple` options.

# Design Decisions Made for the Library

- The following should be regarded as private:
    - constructors for everything other than `doapi`
    - `Resource`
    - `Resource._meta_attrs`
    - `Resource._url`
    - `Resource.data`?
    - `ResourceWithDroplet`
    - `ResourceWithID`
    - `Actionable`
    - the `droplet`, `action`, `ssh_key`, `image`, `region`, `size`, `domain`,
      and `floating_ip` methods of `doapi`
    - `doapi._wait()`
    - `Domain.record()`
    - `SSHKey.id_or_fingerprint`?
- Classes are given `__str__` methods if & only if the resulting strings are
  usable in API requests (except `NetworkInterface`, which gets a `__str__`
  method that returns the IP address because that's probably all you want from
  it anyway).
- The result of mixing different `doapi` objects and their resources is
  undefined.
- Documentation:
    - Only document exceptions that are expected to be raised under
      non-pathological circumstances.
    - Documentation for the non-private methods & attributes will assume that
      all objects were created using public interfaces and will not list all
      the ways that things could go wrong with "raw" objects.

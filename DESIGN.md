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

## On handling duplicated names

- Possible responses to being given a duplicated name to fetch or operate on:
    - `E` — Error out
    - `F` — Fetch/operate on all objects with that name

- Possible responses to being asked to create an object with a name already in
  use:
    - `E` — Error out
    - `N` — Create the object normally
    - `F` — Don't create anything, but do return all of the preexisting objects
      with that name
        - only do this when there's only one preexisting object?

- Possible duplicate name policies are here represented by the letter for the
  "fetch" policy, the letter for the "operate" policy, and the letter for the
  "create" policy; e.g., the current policy is `FEN`.

- Ignoring any non-unique names given on the command line is a bad idea.

- When fetching or operating with the `F` policy, should the output be a list
  of lists of objects (each sublist containing the results for all objects with
  a given name) instead of a list of objects?
    - This would lead to problems when trying to operate with a wait.

- When fetching or operating with the `F` policy, should nonexistent names be
  ignored without an error (and represented by `[]` in list-of-list output)?

- Options for manipulating the duplicate name policy:
    - `--unique` — sets the policy to `EEE`
    - `--multiple` [Come up with something better] — sets the fetch & operate
      policies to `F`
    - `--mkmany` [Come up with something better] — sets the creation policy to
      `N`
    - Merge `--multiple` and `--mkmany` into a `FFN` switch?
    - `--new-or-old` [Come up with something better] — sets the creation policy
      to `F` (but still errors when there's more than one pre-existing
      namesake?)

- **What should the default policy be?**
    - The default creation policy should not be `F`.

- Operations that take mandatory extra arguments (e.g., renaming &
  snapshotting) and thus only allow you to specify one object on the command
  line should always follow policy `E`.

# Design Decisions Made for the Library

- The following should be regarded as private:
    - constructors for everything other than `doapi`
    - `JSObject`
    - `JSObject._meta_attrs`
    - `JSObject._url`
    - `JSObject.data`?
    - `JSObjectWithDroplet`
    - `JSObjectWithID`
    - `Actionable`
    - the `droplet`, `action`, `sshkey`, `image`, `region`, `size`, `domain`,
      and `floating_ip` methods of `doapi`
    - `doapi._wait()`
    - `Domain.record()`
- Classes are given `__str__` methods if & only if the resulting strings are
  usable in API requests (except `NetworkInterface`, which gets a `__str__`
  method that returns the IP address because that's probably all you want from
  it anyway).
- The result of mixing different `doapi` objects and their resources is
  undefined.

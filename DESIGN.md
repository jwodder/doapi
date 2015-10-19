# Design Decisions Made for the CLI

- *[Rethink this]* There is no filtering of result lists by region, image,
  etc.; the only query filters available are those directly supported by the
  API.  For everything else, use `jq`.
- There are no options for controlling pagination.  The only instance where
  pagination should have an effect on the outcome is for raw requests, and for
  those the user can just append `?per_page=` to the path.
- When getting lists of objects for multiple items (e.g., getting the snapshots
  for a list of more than one droplet), the output is a list of lists of
  objects.

## On handling duplicated names

- Possible responses to being given a duplicated name:
    - error out
    - ignore it
    - (when creating) use it
    - (when creating) fetch all of the preexisting objects with that name
        - only do this when there's only one preexisting object?
    - (when not creating) fetch/operate on all objects with that name

- When fetching objects by name, should the output be a list of lists of
  objects (each sublist being all objects with a given name) instead of a list
  of objects?

### Option 1

Options common to all operations on droplets, SSH keys, & images:

- `--unique` —  enforces uniqueness among names
- `--ignore` — with `--unique`, don't error on nonunique names

### Option 2

`--unique` is always on by default; to create an object with a duplicate name,
a `--force` option is required.  Using a non-unique name in a command raises an
error unless some option is specified to make the name expand to all matching
objects.

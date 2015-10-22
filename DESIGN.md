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

## Actions

- Raw action:

        doapi-<droplet/image> act [-P <params as JSON object>] <type> <obj>...
        # or?
        doapi-<droplet/image> act [--param name=value]* <type> <obj>...

- Getting actions:

        doapi-<droplet/image> actions [--latest | --in-progress] [<obj> ...]
        doapi-action [<id> ...]
        doapi-action {--latest | --in-progress}

- Waiting for actions (These assume that an object can't have more than one
  in-progress action on it at a time):

        doapi-droplet wait <wait options> [--status STATUS] [<droplet> ...]
        doapi-image   wait <wait options>                   [<image> ...]
        doapi-action  wait <wait options>                   [<id> ...]

    Rethink whether omitting positional arguments — and thus waiting for all
    in-progress actions on the given objects — should be allowed.

- Idea: For `doapi-<droplet/image>`, one can specify individual actions of an
  object by writing `object@num`, where `num` is `0` (`1`?) for the most recent
  action, `1` (`-1`? `2`?) for the action before that, etc.

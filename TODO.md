# Externals

- Add arguments for controlling pagination

- Add a command for waiting for the most recent action on each droplet in a
  given list to finish
    - Idea: The command for waiting on droplet actions can take arguments as
      either "`<DROPLET>:<ACTION>`" or "`<DROPLET>:`" (or just "`<DROPLET>`"?),
      the latter indicating the most recent action.

- Droplet action commands that require the droplet to be off should have a flag
  for ensuring the droplet is off beforehand

# Internals

- If a `wait_*` method receives a KeyboardInterrupt, it should return
  immediately

- Rethink how the `wait_*` commands return their results; options:
    - Current: Return a tuple of (finished, [errored,] unfinished) objects with
      the first two being in the order they ended
    - Yield each object as it finishes
    - Return a list of objects in the same order as passed to the function

- Look into more appropriate/standard names for `_asdict`

- Try to find a way to return `meta` fields?

- Rename `wait_droplets_status` to `wait_droplets`, default `status` to `None`,
  and wait for the most recent action on each droplet to complete/error when
  `status is None`

- Give the DO classes `copy`/`__copy__` methods and implement "copy
  constructing"

- Each DO object class must have the following methods:
    - `fetch` (accompanied by `doapi.fetch_<TYPE>`)
    - `url`
    - `__int__` (Move to JSObject?)
    - `__format__` ?????
    - `__str__` ????? (shows `name`?)

- Add a mutating equivalent of `fetch` named `update`?

- Should `doapi.fetch_*` call `<TYPE>.fetch()` instead of the other way around?
  This would eliminate duplication of URL construction logic.

- Make the code work in both Python 2 and Python 3
- Bring in line with PEP 8

- Prepend "`fetch_`" to `all_droplets` and `all_sshkeys`?
    - Alternatively, remove the "`fetch_`" in `fetch_droplets_by_name` and
      `fetch_all_droplets_by_name`?

- Add methods to `doapi` for fetching SSH keys by name & fingerprint?

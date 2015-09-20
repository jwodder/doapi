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

- Replace `wait_actions` with `wait_droplet_actions` and `wait_image_actions`
  methods.  The droplet/image ID can be found in the `resource_id` field of the
  action objects (though this means the method arguments must be full objects,
  not just IDs).

- Rethink how the `wait_*` commands return their results; options:
    - Current: Return a tuple of (finished, [errored,] unfinished) objects with
      the first two being in the order they ended
    - Yield each object as it finishes
    - Return a list of objects in the same order as passed to the function

- Idea: Make all DO object classes (Droplet, Action, etc.; i.e., not `doapi`)
  contain a reference to their manager and then make all of the methods for
  operating on them into methods of the classes themselves rather than of
  `doapi`
    - In order to allow operating on an object whose ID I already have and
      whose other information I don't want to fetch, give `doapi` type-specific
      methods (named just `droplet`, `action`, etc.?) for constructing DO
      objects from just an ID and document that most operations won't work on
      the results
        - These methods should also be able to take an instance of the
          respective type instead of an ID, in which case they return either
          the argument itself or a copy

    - JSONification will become more involved:
        - When the base class does not inherit `dict`, give it the method:

                def _asdict(self):
                    data = vars(self).copy()
                    data.pop("doapi_manager", None)
                    return data

        - When the base class _does_ inherit `dict`, either set `__slots__ =
          ('doapi_manager',)` or else add the method:

                def _asdict(self):
                    data = dict(self)
                    data.pop("doapi_manager", None)
                    return data

        - Look into more appropriate/standard names for the method than
          "`_asdict`"
        - Define a custom subclass of `json.JSONEncoder` for this

    - Give each DO class a (non-mutating) `fetch` method for querying &
      returning the current state of the object
        - Also add mutating equivalents named `update`?
        - Rename `doapi.get_droplet` to `doapi.fetch_droplet` etc.

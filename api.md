# Known errors in the API documentation

- The docs state that paginated results are 25 per page by default; it is
  actually 20 per page.
- The input attribute table for the "Snapshot a Droplet" action omits the
  "name" attribute
- Descriptions for accounts are missing.
- The example response for fetching an account omits the relatively-recently
  added "status" and "status_message" fields.
- The curl examples include an "available" field in droplet objects that is not
  documented and doesn't seem to actually exist.
- The "neighbor" requests are underdocumented.
- The curl (and Ruby and Go) example for "List all Droplet Neighbors" shows the
  API returning an array of objects instead of just an object.
- The path for getting a droplet's neighbors is actually
  `/v2/droplets/$DROPLET_ID/neighbors` (note forward slash in place of
  backslash and lack of colon).
- The documentation claims that the API accepts HEAD requests, but actually
  making such requests seems to always result in a 404.

# Unanswered questions about the API

- Can a droplet or image have more than one in-progress action on it at a time?
    - The docs say "If a Droplet action is uncompleted it **may** block the
      creation of a subsequent action for that Droplet" (emphasis added).
- Is fetching an action via `/v2/actions/$ACTION_ID` always equivalent to
  fetching via `/v2/$RESOURCE_TYPE/$RESOURCE_ID/actions/$ACTION_ID`?
- Is there any guarantee about the order actions (or anything else, really) are
  returned in when fetching more than one?  They appear to be returned in
  reverse chronological order.
- Can a non-error response object ever contain keys other than
  `droplet`/`action`/etc., `links`, and `meta`?
- Can an image slug take the place of an image ID in all URLs that use the
  latter, or is this only allowed when retrieving a single image?
- What are all of the `resource_type`s that action objects can be associated
  with?
- When creating a domain record, can non-required attributes for the record
  type be omitted?  Can non-required attributes always be present anyway, and
  if so, must they then be null?
- Exactly which droplet actions can only be carried out when the droplet is
  already off?
- What happens if two droplets both named `foo.managed.domain` are created?
- How are error responses structured?

# Other notes

- When results are paginated, any URL query string parameters that were set in
  the initial request (except "page", of course) will be present in all of the
  link URLs, even meaningless parameters added by the user.
- The follow droplet actions can only be performed when the droplet is already
  on:
    - power_off
    - ???
- The follow droplet actions can only be performed when the droplet is already
  off:
    - snapshot
    - rebuild
    - power_on
    - ???

    These actions all seem to turn the droplet on after completing; look into.

- There appear to be no constraints on having two or more droplets, images, or
  SSH keys with the same name.
- Snapshots are allowed to have the same name as an image slug.
- It appears that a droplet is "locked" iff there is currently an action in
  progress on it.
- If you attempt to create an SSH key that is already registered, you get a 422
  response (Unprocessable Entity) with the body:

        {
            "id": "unprocessable_entity",
            "message": "SSH Key is already in use on your account"
        }

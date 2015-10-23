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
- The "locked" field of floating IP objects is not documented.

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
- Droplet names can only contain alphanumeric characters, `.`, and `-`.
- An action associated with a floating IP has a `resource_type` of
  `"floating_ip"` and a `resource_id` equal to the IP address interpreted as
  bytes of a big-endian integer.
- Actions to assign & unassign floating IPs are only associated with the IPs,
  not the droplets.
- Deleting an assigned floating IP causes an "unassign" action to automatically
  happen first.

## Observed error responses

- If you attempt to create an SSH key that is already registered, you get a 422
  response (Unprocessable Entity) with the body:

        {
            "id": "unprocessable_entity",
            "message": "SSH Key is already in use on your account"
        }

- If you attempt to fetch a droplet that does not exist (or a droplet that
  *does* exist but belongs to another account), you get a 404 response with the
  body:

        {
            "id": "not_found",
            "message": "The resource you were accessing could not be found."
        }

- Attempting to create a droplet with an invalid name produces a 422 response
  with the body:

        {
            "id": "unprocessable_entity",
            "message": "Name Only valid hostname characters are allowed. (a-z, A-Z, 0-9, . and -)"
        }

- Attempting to create an SSH key with an invalid pubkey produces a 422
  response with the body:

    {
        "id": "unprocessable_entity",
        "message": "Key invalid type, we support 'ssh-rsa', 'ssh-dss', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384', or 'ecdsa-sha2-nistp521'"
    }

- Attempting to register an SSH key that has already been registered produces a
  422 with:

    {
        "id": "unprocessable_entity",
        "message": "SSH Key is already in use on your account"
    }

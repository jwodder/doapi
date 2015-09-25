# Known errors in the API documentation

- The docs state that paginated results are 25 per page by default; it is
  actually 20 per page.
- The input attribute table for the "Snapshot a Droplet" action omits the
  "name" attribute
- Descriptions for accounts are missing.
- The curl examples include an "available" field in droplet objects that is not
  documented and doesn't seem to actually exist.
- The curl (and Ruby and Go) example for "List all Droplet Neighbors" shows the
  API returning an array of objects instead of just an object.
- The "neighbor" requests are underdocumented.
- The example response for "List Neighbors for a Droplet" is wrong.  The actual
  object returned is as follows:
    - a "droplet" field containing the droplet object whose neighbors were
      requested
    - ???
- The path for getting a droplet's neighbors should be written as
  `/v2/droplets/$DROPLET_ID\neighbors` (also, note lack of colon).
- Accounts are underdocumented.
- The example response for fetching an account omits the relatively-recently
  added "status" and "status_message" fields.

# Unanswered questions about the API

- Can a droplet have more than one in-progress action on it at a time?
- Is fetching an action via `/v2/actions/$ACTION_ID` always equivalent to
  fetching via `/v2/$RESOURCE_TYPE/$RESOURCE_ID/actions/$ACTION_ID`?
- Is there any guarantee about the order actions (or anything else, really) are
  returned in when fetching more than one?  They appear to be returned in
  reverse chronological order.
- Can a non-error response object ever contain keys other than
  `droplet`/`action`/etc., `links`, and `meta`?
- Can an image slug take the place of an image ID in all URLs that use the
  latter, or is this only allowed when retrieving a single image?
- What happens if you try to create a new SSH key with a key whose fingerprint
  has already been registered?
- What are all of the `resource_type`s that action objects can be associated
  with?

# Other notes

- Yes, the URL path for getting a droplet's neighbors is really
  `/v2/droplets/$DROPLET_ID\neighbors" with a `r'\n'`.

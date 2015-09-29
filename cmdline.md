# Add options to non-`new` commands for filtering by image/size/region?

# Look into the 'parents' argument to `argparse.ArgumentParser`

# All JSON output is pretty.

doapi droplet [show]
doapi droplet show [name|id] ...

doapi droplet new
    [-i | --image] image
    [-s | --size] size
    [-r | --region] region
    --json
     # A JSON array (or an object, which is treated as an array of one) is read
     # from standard input, the -i/-s/-r values are applied to those objects
     # that are missing them, and the droplets are created from the objects.
     # When --json is given, no `name` arguments should be given.
    --json-file FILE
    --wait
    --wait-time seconds
    --wait-interval seconds
    --user-data data
    # ipv6, backups, etc.
    name ...

doapi droplet delete [name|id] ...

doapi droplet <action name> [--wait ...] [name|id] ...

# Add a command for raw actions

doapi raw [-X method] [-f | --json-file FILE] URL|PATH < data
# Add an option for printing headers to stderr
# Instead of "raw" and an "-X method" option, have commands named "get",
#   "post", "put", and "delete" (and "head"?) ?
# Add a `--paginate KEY` argument?

doapi sshkey [show [id|fingerprint|name] ...]
doapi sshkey new name [file default:stdin]
 # Add an option for only creating if the public key isn't already present
doapi sshkey delete [id|fingerprint|name] ...
doapi sshkey update id|fingerprint|name newname

doapi image show [--type TYPE|--distribution|--application] [--private] ...

### Wait for a droplet to reach a given state

### Wait for an action to complete; if a droplet can have no more than one
### pending action at a time, this can be replaced with "Wait for the latest
### action on a droplet to complete"


Options common to all commands:
    --api-key key
    --api-key-file file
    --timeout int
    --endpoint URL

Options common to all actions (including creating droplets):
    --wait
    --wait-time seconds
    --wait-interval seconds

Options common to all operations on droplets:
    --unique  # enforces uniqueness among droplet names
    --ignore ?  # with `--unique`, don't error on nonunique names

API key sources, in order of precedence:
 - API key or keyfile specified on the command-line (mutually exclusive)
 - DO_API_KEY environment variable
 - DO_API_TOKEN environment variable
 - ~/.doapi file [Rethink name]

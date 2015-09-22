### Add `--unique` options for enforcing uniqueness among droplet names (and
### then add an `--ignore` option for not erroring on nonunique names)

# Add options to non-`new` commands for filtering by image/size/region?

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

doapi raw [-X method] [-f | --json-file FILE] URL|PATH < json

doapi sshkey [show [id|fingerprint|name] ...]
doapi sshkey new name [file default:stdin]
 # Add an option for only creating if the public key isn't already present
doapi sshkey delete [id|fingerprint|name] ...
doapi sshkey update id|fingerprint|name newname

### Wait for a droplet to reach a given state

### Wait for an action to complete; if a droplet can have no more than one
### pending action at a time, this can be replaced with "Wait for the latest
### action on a droplet to complete"



API key sources, in order of precedence:
 - API key or keyfile specified on the command-line (mutually exclusive)
 - DO_API_KEY environment variable
 - DO_API_TOKEN environment variable
 - ~/.doapi file [Rethink name]

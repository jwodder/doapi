Command-Line Programs
=====================

.. toctree::
   cli/account
   cli/action
   cli/domain
   cli/droplet
   cli/floating_ip
   cli/image
   cli/region
   cli/request
   cli/size
   cli/sshkey

TODO

[Document the plain ``doapi`` command]

Universal options common to all commands::

    --api-token token
    --api-token-file file
    --timeout int
    --endpoint URL

Options common to all actions (including creating droplets)::

    --wait
    --wait-time seconds
    --wait-interval seconds

API token sources, in order of precedence:

- API token or tokenfile specified on the command-line (mutually exclusive)
- ``DO_API_TOKEN`` environment variable
- ``~/.doapi`` file

::

    <droplet> := ID or name
    <sshkey>  := ID, fingerprint, or name
                 # When creating a droplet, it should be possible to specify files
                 # as SSH keys, causing them to be automatically registered with DO
    <image>   := ID, slug, or name (slugs take precedence)
    <action>  := ID
    <ip>      := IP address in x.x.x.x form or as an integer

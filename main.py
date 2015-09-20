import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key')
    #parser.add_argument('--api-key-file', type=argparse.FileType('r'))
    ### Make --api-key and --api-key-file mutually exclusive
    parser.add_argument('--timeout', type=int)
    parser.add_argument('--pretty', action='store_true')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_droplet = cmds.add_parser('droplet')
    subcmd_droplet = cmd_droplet.add_subparsers(title='subcommand', dest='subcmd')
    subcmd_droplet_get = subcmd_droplet.add_parser('get')
    subcmd_droplet_new = subcmd_droplet.add_parser('new')

    args = parser.parse_args()

    if args.api_key is None:
        try:
            api_key = os.environ["DO_API_KEY"]
        except KeyError:
            try:
                api_key = os.environ["DO_API_TOKEN"]
            except KeyError:
                raise SystemExit('No DigitalOcean API key supplied\n'
                                 'Specify your API key with the --api-key'
                                 ' option or the DO_API_KEY environment\n'
                                 'variable')
    else:
        api_key = args.api_key
    client = doapi(api_key)


    # ssh_key show arg ...
    keyids = []
    byname = False
    for arg in args:
        try:
            x = int(arg)
        except ValueError:
            if ### is fingerprint ###:
                keyids.append(("fingerprint", arg))
            else:
                keyids.append(("name", arg))
                byname = True
        else:
            keyids.append("id", x)
    output = []
    if byname:
        keys = client.all_ssh_keys()
        for field, val in keyids:
            output.extend(k for k in keys if k[field] == val)
    else:
        for _, val in keyids:
            try:
                output.append(client.get_ssh_key, val)
            except ### 404 error ### :
                pass
    ### Dump `output`

if __name__ == '__main__':
    main()

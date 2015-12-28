import argparse
from   six.moves import map
from   .         import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-domain')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show')
    cmd_show.add_argument('domain', nargs='*')

    cmd_new = cmds.add_parser('new')
    cmd_new.add_argument('domain')
    cmd_new.add_argument('ip_address')

    cmd_delete = cmds.add_parser('delete')
    cmd_delete.add_argument('domain', nargs='+')

    cmd_showrec = cmds.add_parser('show-record')
    cmd_showrec.add_argument('domain')
    cmd_showrec.add_argument('record_id', type=int, nargs='*')

    cmd_newrec = cmds.add_parser('new-record')
    cmd_newrec.add_argument('--priority', type=int)  ### float instead?
    cmd_newrec.add_argument('--port', type=int)
    cmd_newrec.add_argument('--weight', type=int)  ### float instead?
    cmd_newrec.add_argument('domain')
    cmd_newrec.add_argument('type')
    cmd_newrec.add_argument('name')
    cmd_newrec.add_argument('data')

    cmd_setrec = cmds.add_parser('set-record')
    # `set` is like `new` but deletes any & all pre-existing records with the
    # same type & name.
    cmd_setrec.add_argument('--priority', type=int)  ### float instead?
    cmd_setrec.add_argument('--port', type=int)
    cmd_setrec.add_argument('--weight', type=int)  ### float instead?
    cmd_setrec.add_argument('domain')
    cmd_setrec.add_argument('type')
    cmd_setrec.add_argument('name')
    cmd_setrec.add_argument('data')

    cmd_modrec = cmds.add_parser('update-record')
    cmd_modrec.add_argument('--type')
    cmd_modrec.add_argument('--name')
    cmd_modrec.add_argument('--data')
    modrec_priority = cmd_modrec.add_mutually_exclusive_group()
    modrec_priority.add_argument('--priority', type=int)  ### float instead?
    modrec_priority.add_argument('--no-priority', action='store_true')
    modrec_port = cmd_modrec.add_mutually_exclusive_group()
    modrec_port.add_argument('--port', type=int)
    modrec_port.add_argument('--no-port', action='store_true')
    modrec_weight = cmd_modrec.add_mutually_exclusive_group()
    modrec_weight.add_argument('--weight', type=int)  ### float instead?
    modrec_weight.add_argument('--no-weight', action='store_true')
    cmd_modrec.add_argument('domain')
    cmd_modrec.add_argument('record_id', type=int)

    cmd_delrec = cmds.add_parser('delete-record')
    cmd_delrec.add_argument('domain')
    cmd_delrec.add_argument('record_id', type=int, nargs='+')

    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)

    if args.cmd == 'show':
        if args.domain:
            util.dump(map(client.fetch_domain, args.domain))
        else:
            util.dump(client.fetch_all_domains())

    elif args.cmd == 'new':
        util.dump(client.create_domain(args.domain, args.ip_address))

    elif args.cmd == 'delete':
        domains = list(map(client.fetch_domain, args.domain))
        for d in domains:
            d.delete()

    elif args.cmd == 'show-record':
        domain = client.fetch_domain(args.domain)
        if args.record_id:
            util.dump(map(domain.fetch_record, args.record_id))
        else:
            util.dump(domain.fetch_all_records())

    elif args.cmd == 'new-record':
        domain = client.fetch_domain(args.domain)
        util.dump(domain.create_record(args.type, args.name, args.data,
                                       args.priority, args.port, args.weight))

    elif args.cmd == 'set-record':
        domain = client.fetch_domain(args.domain)
        newrec = domain.create_record(args.type, args.name, args.data,
                                      args.priority, args.port, args.weight)
        recs = [r for r in domain.fetch_all_records()
                  if r.type == args.type and r.name == args.name and \
                     r.id != newrec.id]
        for r in recs:
            r.delete()
        util.dump(newrec)

    elif args.cmd == 'update-record':
        rec = client.fetch_domain(args.domain).fetch_record(args.record_id)
        attrs = {}
        for a in 'type name data priority port weight'.split():
            if getattr(args, a, None) is not None:
                attrs[a] = getattr(args, a)
        for a in 'priority port weight'.split():
            if getattr(args, 'no_' + a, None):
                attrs[a] = None
        util.dump(rec.update_record(**attrs))

    elif args.cmd == 'delete-record':
        domain = client.fetch_domain(args.domain)
        recs = list(map(domain.fetch_record, args.record_id))
        for r in recs:
            r.delete()

    else:
        raise RuntimeError('No path defined for command %r' % (args.cmd,))

if __name__ == '__main__':
    main()

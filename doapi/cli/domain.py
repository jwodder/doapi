import argparse
from   six.moves import map  # pylint: disable=redefined-builtin
from   .         import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-domain',
                                     description='Manage DigitalOcean domains'
                                                 ' & domain records')
    cmds = parser.add_subparsers(title='command', dest='cmd')

    cmd_show = cmds.add_parser('show', help='List domains',
                               description='List domains')
    cmd_show.add_argument('domain', nargs='*',
                          help='a domain name; omit to list all')

    cmd_new = cmds.add_parser('new', help='Add a new domain name to account',
                              description='Add a new domain name to account')
    cmd_new.add_argument('domain', help='the domain name to add')
    cmd_new.add_argument('ip_address',
                         help='the IP address to which the domain should point')

    cmd_delete = cmds.add_parser('delete', help='Delete a domain',
                                 description='Delete a domain')
    cmd_delete.add_argument('domain', nargs='+', help='a domain name')

    cmd_showrec = cmds.add_parser('show-record',
                                  help='List the DNS records for a domain',
                                  description='List the DNS records for a'
                                              ' domain')
    cmd_showrec.add_argument('domain',
                             help='the domain name to show the records for')
    cmd_showrec.add_argument('record_id', type=int, nargs='*',
                             help='ID of a record to show; omit to list all')

    cmd_newrec = cmds.add_parser('new-record',
                                 help='Add a new DNS record to a domain',
                                 description='Add a new DNS record to a domain')
    cmd_newrec.add_argument('--delete', action='store_true',
                            help='Delete any pre-existing records with the same'
                                 ' type & name')
    cmd_newrec.add_argument('--priority', type=int,
                            help='priority for the new record')
    cmd_newrec.add_argument('--port', type=int,
                            help='port on which a SRV is accessible')
    cmd_newrec.add_argument('--weight', type=int,
                            help='weight of the new record')
    cmd_newrec.add_argument('domain', help='domain name to add a record to')
    cmd_newrec.add_argument('type', help='type of DNS record to add')
    cmd_newrec.add_argument('name', help='name of the new record')
    cmd_newrec.add_argument('data', help='value of the new record')

    cmd_modrec = cmds.add_parser('update-record', help='Modify a DNS record',
                                 description='Modify a DNS record')
    cmd_modrec.add_argument('--type', help='new type for the record')
    cmd_modrec.add_argument('--name', help='new name for the record')
    cmd_modrec.add_argument('--data', help='new value for the record')
    modrec_priority = cmd_modrec.add_mutually_exclusive_group()
    modrec_priority.add_argument('--priority', type=int,
                                 help='new priority for the record')
    modrec_priority.add_argument('--no-priority', action='store_true',
                                 help="Unset the record's priority")
    modrec_port = cmd_modrec.add_mutually_exclusive_group()
    modrec_port.add_argument('--port', type=int, help='new port for the record')
    modrec_port.add_argument('--no-port', action='store_true',
                             help="Unset the record's port")
    modrec_weight = cmd_modrec.add_mutually_exclusive_group()
    modrec_weight.add_argument('--weight', type=int,
                               help='new weight for the record')
    modrec_weight.add_argument('--no-weight', action='store_true',
                               help="Unset the record's weight")
    cmd_modrec.add_argument('domain',
                            help='domain name of the record to modify')
    cmd_modrec.add_argument('record_id', type=int,
                            help='ID of the record to modify')

    cmd_delrec = cmds.add_parser('delete-record', help='Delete a DNS record',
                                 description='Delete a DNS record')
    cmd_delrec.add_argument('domain', help='domain name to delete records from')
    cmd_delrec.add_argument('record_id', type=int, nargs='+',
                            help='ID of the record to delete')

    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)

    if args.cmd == 'show':
        if args.domain:
            util.dump(util.rmdups(map(client.fetch_domain, args.domain),
                                  'domain', 'name'))
        else:
            util.dump(client.fetch_all_domains())

    elif args.cmd == 'new':
        util.dump(client.create_domain(args.domain, args.ip_address))

    elif args.cmd == 'delete':
        domains = util.rmdups(map(client.fetch_domain, args.domain), 'domain',
                              'name')
        for d in domains:
            d.delete()

    elif args.cmd == 'show-record':
        domain = client.fetch_domain(args.domain)
        if args.record_id:
            util.dump(util.rmdups(map(domain.fetch_record, args.record_id),
                                  'record'))
        else:
            util.dump(domain.fetch_all_records())

    elif args.cmd == 'new-record':
        domain = client.fetch_domain(args.domain)
        newrec = domain.create_record(args.type, args.name, args.data,
                                      args.priority, args.port, args.weight)
        if args.delete:
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
        recs = util.rmdups(map(domain.fetch_record, args.record_id), 'record')
        for r in recs:
            r.delete()

    else:
        assert False, 'No path defined for command {0!r}'.format(args.cmd)

if __name__ == '__main__':
    main()

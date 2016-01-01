import argparse
import sys
from   . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-request')
    parser.add_argument('-X', '--request', type=str.upper, default='GET',
                        choices=['GET', 'POST', 'PUT', 'DELETE'])
    parser.add_argument('-d', '--data', metavar='string|@file')
    parser.add_argument('-D', '--dump-header', type=argparse.FileType('w'))
    parser.add_argument('--paginate', metavar='key')
    parser.add_argument('path', metavar='URL|path')
    args = parser.parse_args(argv, parsed)
    if args.paginate is not None and args.request != 'GET':
        util.die('--paginate can only be used with the GET method')
    if args.data is not None:
        if args.request not in ('POST', 'PUT'):
            util.die('--data can only be used with the POST and PUT methods')
        if args.data.startswith("@"):
            if args.data[1:] == '-':
                extra = {"data": sys.stdin.read()}
            else:
                with open(args.data[1:]) as fp:
                    extra = {"data": fp.read()}
        else:
            extra = {"data": args.data}
    else:
        extra = {}
    client, _ = util.mkclient(args)
    if args.paginate is None:
        response = client.request(args.path, method=args.request, **extra)
    else:
        response = client.paginate(args.path, args.paginate)
    if args.dump_header:
        # Using "with" would cause `args.dump_header` to close afterwards,
        # which would cause problems if it was stdout.  "with" technically
        # doesn't provide any benefit here anyway.
        util.dump(dict(client.last_response.headers), fp=args.dump_header)
    if args.request != 'DELETE':
        util.dump(response)


if __name__ == '__main__':
    main()

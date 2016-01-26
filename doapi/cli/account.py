import argparse
from   . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-account',
                                     description='Fetch DigitalOcean account'
                                                 ' data')
    parser.add_argument('-R', '--rate-limit', action='store_true',
                        help='Fetch current rate limit statistics instead of'
                             ' account data')
    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)
    me = client.fetch_account()
    if args.rate_limit:
        util.dump(client.last_rate_limit)
    else:
        util.dump(me)

if __name__ == '__main__':
    main()

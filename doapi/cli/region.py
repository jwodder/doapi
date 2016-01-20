import argparse
from   . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-region',
                                     description='List available DigitalOcean'
                                                 ' droplet regions')
    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)
    util.dump(client.fetch_all_regions())

if __name__ == '__main__':
    main()

from . import _util as util

def main(argv=None, parsed=None):
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-sizes')
    args = parser.parse_args(argv, parsed)
    client, _ = util.mkclient(args)
    util.dump(client.fetch_all_sizes())

if __name__ == '__main__':
    main()

from . import _util as util

def main():
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-sizes')
    args = parser.parse_args()
    client, _ = util.mkclient(args)
    util.dump(client.fetch_all_sizes())

if __name__ == '__main__':
    main()

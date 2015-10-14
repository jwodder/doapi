from . import _util as util

def main():
    parser = argparse.ArgumentParser(parents=[util.universal],
                                     prog='doapi-account')
    args = parser.parse_args()
    client, _ = util.mkclient(args)
    util.dump(client.fetch_account())

if __name__ == '__main__':
    main()

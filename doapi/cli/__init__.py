import os.path
import sys
from   . import _util as util

if __name__ == '__main__':
    argv0 = os.path.splitext(os.path.basename(sys.argv[0]))[0]
    if argv0 == 'doapi' and len(sys.argv) > 1:
        argv0 += '-' + sys.argv.pop(1)
    if argv0 == 'doapi-droplet':
        from .droplet import main
    elif argv0 == 'doapi-image':
        from .image import main
    elif argv0 == 'doapi-action':
        from .action import main
    elif argv0 == 'doapi-domain':
        from .domain import main
    elif argv0 == 'doapi-sshkey':
        from .sshkey import main
    elif argv0 == 'doapi-regions':
        from .regions import main
    elif argv0 == 'doapi-sizes':
        from .sizes import main
    elif argv0 == 'doapi-account':
        from .account import main
    elif argv0 == 'doapi-request':
        from .request import main
    else:
        util.die('Available commands:\n'
                 '    account action domain droplet image regions request'
                 ' sizes sshkey')
    main()

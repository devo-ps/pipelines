#!/usr/bin/env python
'''
Usage:
    pipelines (--version|--help)
    pipelines server --workspace=<workspace> [--title=<title>] [--cookie-secret=<cookie-secret>] [--host=<host>] [--port=<port>] [--username=<username>] [--password=<password>] [--ask-password] [--github-auth=<Org/Team>] [--debug] [--history-limit=<history-limit>]

Options:
    --host=<host>                       Bind address [default: 127.0.0.1]
    --port=<port>                       Bind port [default: 8888]
    --cookie-secret=<cookie-secret>     Cookie Secret
    --username=<username>               Admin Username
    --password=<password>               Admin Password
    --ask-password                      Ask to type in password manually
    --github-auth=<Org/Team>            Enable Github Authentication (OAuth). Allow specific Team.
    --workspace=<workspace>             Location of the pipelines and runs [default: /var/lib/pipelines/workspace]
    --title=<title>                     Title on tab
    --debug                             Set log level to debug
    --history-limit=<history-limit>     Limit run history loading for pipelines

Help:
    pipelines server            Starts pipelines' server (API + UI)
'''
import logging
import sys
import os
import os.path
import pprint

import docopt
from getpass import getpass

from pipelines import __version__, PipelinesError
from pipelines.api import server
from pipelines.pipeline.utils import random_secret

MIN_PASSWORD_LEN = 12

def _get_username(args):
    if args['--username']:
        return args['--username']
    if 'USERNAME' in os.environ:
        return os.environ['USERNAME']
    return None

def _get_password(args):
    if args['--password']:
        return args['--password']
    if args['--ask-password']:
        return getpass()
    if 'PASSWORD' in os.environ:
        return os.environ['PASSWORD']
    return None

def _get_cookie_secret(args):
    if args['--cookie-secret']:
        return args['--cookie-secret']
    if 'COOKIE_SECRET' in os.environ:
        return os.environ['COOKIE_SECRET']
    return None

def _get_title(args):
    if args['--title']:
        return args['--title']
    if 'TITLE' in os.environ:
        return os.environ['TITLE']
    return 'Pipelines'

def main():
    args = docopt.docopt(
        __doc__,
        version="version "+ __version__,
        help=True
    )

    logging.error(pprint.pformat(args))

    if args.get('server'):
        options = {
            'workspace': os.path.realpath(os.path.expanduser(args.get('--workspace'))),
            'title': _get_title(args),
            'host': args.get('--host'),
            'port': args.get('--port')
        }

        username = _get_username(args)
        password = _get_password(args)
        cookie_secret = _get_cookie_secret(args)
        ghauth = args.get('--github-auth')

        options['cookie_secret']  = cookie_secret if cookie_secret else random_secret()

        if ghauth:
            teams = []
            for allowed_team in ghauth.split(','):
                if not '/' in allowed_team:
                    raise PipelinesError('github-auth requires organization and team in format of "(org)/(team)"')
                org, team = allowed_team.split('/', 1)
                teams.append((org, team))
            options['auth'] = ('gh', teams)
        elif username and password:
            if len(password) < MIN_PASSWORD_LEN:
                raise PipelinesError('Too short password')
            options['auth'] = ('static', username, password)

        options['debug'] = args.get('--debug')
        options['history_limit'] = int(args.get('--history-limit') or 30)
        try:
            server.main(options)
        except KeyboardInterrupt:
            print('Exiting')
    else:
        print(__doc__.strip('\n'))
        sys.exit(0)


if __name__ == '__main__':
    main()

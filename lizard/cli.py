import argparse
from lizard import LOG

NAME = 'lizard'
DESC = 'distributed concurrent data processing platform'

DEFAULT_PORT_NO = 5000
DEFAULT_BIND_ADDR = '0.0.0.0'

ARG_SETS = {
    'CONNECT': (
        (('-p', '--port'),
         {'help': 'server port', 'required': True,
          'metavar': 'INT', 'type': int, 'action': 'store'}),
        (('-a', '--addr'),
         {'help': 'server address', 'required': True,
          'metavar': 'ADDR', 'action': 'store'}),),
    'LOG': (
        (('-v', '--verbose'),
         {'help': 'enable debug messages', 'action': 'store_true',
          'default': False}),),
    'SERVER': (
        (('--port',),
         {'help': 'server bind port', 'default': DEFAULT_PORT_NO,
          'action': 'store', 'type': int, 'metavar': 'INT'}),
        (('--host',),
         {'help': 'server bind address', 'default': DEFAULT_BIND_ADDR,
          'action': 'store', 'metavar': 'ADDR'}),),
}
SUBCMDS = {
    'client': ('run client program', ('CONNECT', 'LOG')),
    'server': ('run server program', ('LOG', 'SERVER')),
}


def configure_parser():
    """
    configure the argument parser
    :returns: argparse.ArgumentParser
    """
    # configure parser
    parser = argparse.ArgumentParser(description=DESC, prog=NAME)
    subparsers = parser.add_subparsers(dest="subcmd")
    subparsers.required = True

    def add_subparser(name, desc, arg_sets):
        subparser = subparsers.add_parser(name, help=desc)
        for (_args, _kwargs) in (a for arg_set in arg_sets for a in arg_set):
            subparser.add_argument(*_args, **_kwargs)

    # configure subparsers
    for (name, (desc, arg_sets)) in SUBCMDS.items():
        add_subparser(name, desc, [ARG_SETS[a] for a in arg_sets])

    return parser


def _empty_normalizer(args):
    """placeholder normalizer that does nothing"""
    return args


def _normalize_server_args(args):
    """normalize server arguments"""
    # ensure port number is valid
    if args.port > 65535:
        LOG.error('port number invalid: %s', args.port)
        return None
    elif args.port < 1024:
        LOG.warning('port number requires root priv: %s', args.port)

    # NOTE: does not support ipv6 bind addrs and may allow some invalid addrs
    if len(args.host.split('.')) != 4:
        LOG.error('invalid bind addr: %s', args.host)
        return None

    return args


def normalize_args(args):
    """
    normalize parsed arguments
    :returns: normalized args if successful else None
    """
    normalizers = {
        'CONNECT': _empty_normalizer,
        'LOG': _empty_normalizer,
        'SERVER': _normalize_server_args,
    }

    # call the normalizer for every arg set used
    (_, arg_sets) = SUBCMDS[args.subcmd]
    for normalizer in [normalizers[arg_set] for arg_set in arg_sets]:
        args = normalizer(args)
        if args is None:
            break

    return args
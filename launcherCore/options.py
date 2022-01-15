"""
import argparse

parser = argparse.ArgumentParser(description='Launcher command line agr')

parser.add_argument("-u", "--username", dest="username", default=None,
                    help="username to log in with")

parser.add_argument("-p", "--password", dest="password", default=None,
                    help="password to log in with")

parser.add_argument("-s", "--server", dest="server", default=None,
                    help="server host or host:port "
                         "(enclose IPv6 addresses in square brackets)")

parser.add_argument("-o", "--offline", dest="offline", action="store_true",
                    help="connect to a server in offline mode "
                         "(no password required)")

parser.add_argument("-d", "--dump-packets", dest="dump_packets",
                    action="store_true",
                    help="print sent and received packets to standard error")

parser.add_argument("-v", "--dump-unknown-packets", dest="dump_unknown",
                    action="store_true",
                    help="include unknown packets in --dump-packets output")

(options, args) = parser.parse_args()
"""
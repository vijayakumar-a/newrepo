#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: Wed Sep 13 13:58:21 CEST 2017
#
#  https://github.com/HariSekhon/DevOps-Python-tools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn
#  and optionally send me feedback to help steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

Tool to return the active HBase Master from an argument list of hosts

Can mix and match between a comma separated list of hosts (--host server1,server2 or contents of the $HOST
environment variable if not specified) and general free-form space separated arguments, which is useful if piping
a host list through xargs.

Multi-threaded for speed and exits upon first available host response to minimize delay to ~ 1 second or less.

Useful for simplying scripting or generically extending tools that don't support HBase High Availability directly

By default checks the same --port on all servers. Hosts may have optional :<port> suffixes added to individually
override each one.

Exits with return code 1 and NO_AVAILABLE_SERVER if none of the namenodes are active, --quiet mode will not print
NO_AVAILABLE_SERVER.

Tested on HBase 1.1.2 on HDP 2.6.1 and Apache HBase 0.96, 0.98, 1.0, 1.1, 1.2, 1.3

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
#from __future__ import unicode_literals

import os
import sys
import traceback
#from random import shuffle
srcdir = os.path.abspath(os.path.dirname(__file__))
libdir = os.path.join(srcdir, 'pylib')
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from find_active_server import FindActiveServer
except ImportError as _:
    print(traceback.format_exc(), end='')
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.7.1'


class FindActiveHBaseMaster(FindActiveServer):

    def __init__(self):
        # Python 2.x
        super(FindActiveHBaseMaster, self).__init__()
        # Python 3.x
        # super().__init__()
        self.default_port = 16010
        self.protocol = 'http'
        self.url_path = '/jmx?qry=Hadoop:service=HBase,name=Master,sub=Server'
        self.default_num_threads = 2
        self.regex = r'"tag.isActiveMaster" : "true"'

    def add_options(self):
        self.add_hostoption(name='HBase Master', default_port=self.default_port)
        self.add_ssl_opt()
        self.add_common_opts()

    def process_options(self):
        self.validate_common_opts()


if __name__ == '__main__':
    FindActiveHBaseMaster().main()

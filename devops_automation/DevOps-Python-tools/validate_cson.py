#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2019-10-07 10:23:31 +0100 (Mon, 07 Oct 2019)
#
#  https://github.com/HariSekhon/DevOps-Python-tools
#
#  License: see accompanying Hari Sekhon LICENSE file
#
#  If you're using my code you're welcome to connect with me on LinkedIn and optionally send me feedback
#  to help improve or steer this or other code I publish
#
#  https://www.linkedin.com/in/HariSekhon
#

"""

Simple CSON file validator

Validates each file passed as an argument

Directories are recursed, checking all files ending in a .cson suffix.

Works like a standard unix filter program - if no files are passed as arguments or '-' is given then reads
from standard input

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import re
import sys
import tempfile
import cson
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import die, log, log_option, validate_regex
    from validate_ini import IniValidatorTool
except ImportError as _:
    print('module import failed: %s' % _, file=sys.stderr)
    print("Did you remember to build the project by running 'make'?", file=sys.stderr)
    print("Alternatively perhaps you tried to copy this program out without it's adjacent libraries?", file=sys.stderr)
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.1.0'


class CsonValidatorTool(IniValidatorTool):

    def __init__(self):
        # Python 2.x
        super(CsonValidatorTool, self).__init__()
        # Python 3.x
        # super().__init__()
        self.re_suffix = re.compile(r'.*\.cson$', re.I)
        self.valid_cson_msg = '<unknown> => CSON OK'
        self.invalid_cson_msg = '<unknown> => CSON INVALID'

    def add_options(self):
        self.add_opt('-i', '--include', metavar='regex', default=os.getenv('INCLUDE'),
                     help='Regex of file / directory paths to check only ones that match ($INCLUDE, case insensitive)')
        self.add_opt('-e', '--exclude', metavar='regex', default=os.getenv('EXCLUDE'),
                     help='Regex of file / directory paths to exclude from checking, ' + \
                          '($EXCLUDE, case insensitive, takes priority over --include)')

    def process_options(self):
        self.include = self.get_opt('include')
        self.exclude = self.get_opt('exclude')
        if self.include:
            validate_regex(self.include, 'include')
            self.include = re.compile(self.include, re.I)
        if self.exclude:
            validate_regex(self.exclude, 'exclude')
            self.exclude = re.compile(self.exclude, re.I)
        for key in self.opts:
            log_option(key, self.opts[key])

    @staticmethod
    def check_cson(filehandle):
        try:
            _ = cson.load(filehandle)
            if _:
                return True
        except ValueError:
            return False
        return False

    def check_file(self, filename):
        self.filename = filename
        if self.filename == '-':
            self.filename = '<STDIN>'
        self.valid_cson_msg = '%s => CSON OK' % self.filename
        self.invalid_cson_msg = '%s => CSON INVALID' % self.filename
        if self.filename == '<STDIN>':
            log.debug('cson stdin')
            tmp = tempfile.NamedTemporaryFile()
            log.debug('created tmp file from stdin: %s', tmp.name)
            tmp.write(sys.stdin.read())
            tmp.seek(0)
            self.check_cson(tmp.name)
            tmp.close()
        else:
            if self.is_excluded(filename):
                return
            if not self.is_included(filename):
                return
            log.debug('checking %s', self.filename)
            try:
                #with open(filename) as filehandle:
                if self.check_cson(filename):
                    print(self.valid_cson_msg)
                else:
                    print(self.invalid_cson_msg)
                    sys.exit(2)
            except IOError as _:
                die("ERROR: %s" % _)


if __name__ == '__main__':
    CsonValidatorTool().main()

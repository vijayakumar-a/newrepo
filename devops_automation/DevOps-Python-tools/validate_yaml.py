#!/usr/bin/env python
#  vim:ts=4:sts=4:sw=4:et
#
#  Author: Hari Sekhon
#  Date: 2015-12-22 23:25:25 +0000 (Tue, 22 Dec 2015)
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

YAML Validator Tool

Validates each file passed as an argument

Directories are recursed, checking all files ending in a .yml / .yaml suffix.

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
import yaml
libdir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'pylib'))
sys.path.append(libdir)
try:
    # pylint: disable=wrong-import-position
    from harisekhon.utils import log, die, ERRORS, isYaml, log_option, uniq_list_ordered, validate_regex
    from harisekhon import CLI
except ImportError as _:
    print('module import failed: %s' % _, file=sys.stderr)
    print("Did you remember to build the project by running 'make'?", file=sys.stderr)
    print("Alternatively perhaps you tried to copy this program out without it's adjacent libraries?", file=sys.stderr)
    sys.exit(4)

__author__ = 'Hari Sekhon'
__version__ = '0.9.3'


class YamlValidatorTool(CLI):

    def __init__(self):
        # Python 2.x
        super(YamlValidatorTool, self).__init__()
        # Python 3.x
        # super().__init__()
        self.re_yaml_suffix = re.compile(r'.*\.ya?ml$', re.I)
        self.valid_yaml_msg = '<unknown> => YAML OK'
        self.invalid_yaml_msg = '<unknown> => YAML INVALID'
        self.failed = False
        self.exclude = None

    def add_options(self):
        self.add_opt('-p', '--print', action='store_true',
                     help='Print the YAML document(s) if valid, else print nothing (useful for shell ' +
                     'pipelines). Exit codes are still 0 for success, or %s for failure'
                     % ERRORS['CRITICAL'])
        self.add_opt('-e', '--exclude', metavar='regex', default=os.getenv('EXCLUDE'),
                     help='Regex of file / directory paths to exclude from checking ($EXCLUDE)')

    def process_options(self):
        self.exclude = self.get_opt('exclude')
        if self.exclude:
            validate_regex(self.exclude, 'exclude')
            self.exclude = re.compile(self.exclude, re.I)

    def is_excluded(self, path):
        if self.exclude and self.exclude.search(path):
            log.debug("excluding path: %s", path)
            return True
        return False

    def check_yaml(self, content):
        if isYaml(content, safe_load_all=True):
            if self.get_opt('print'):
                print(content, end='')
            else:
                print(self.valid_yaml_msg)
        # multi-record yaml like JSON in Big Data isn't really used
        # elif self.check_multiline_yaml():
        #     pass
        else:
            self.failed = True
            if not self.get_opt('print'):
                if self.verbose > 2:
                    try:
                        yaml.safe_load_all(content)
                    except yaml.YAMLError as _:
                        print(_)
                die(self.invalid_yaml_msg)

    def run(self):
        if not self.args:
            self.args.append('-')
        args = uniq_list_ordered(self.args)
        for arg in args:
            if arg == '-':
                continue
            if not os.path.exists(arg):
                print("'%s' not found" % arg)
                sys.exit(ERRORS['CRITICAL'])
            if os.path.isfile(arg):
                log_option('file', arg)
            elif os.path.isdir(arg):
                log_option('directory', os.path.abspath(arg))
            else:
                die("path '%s' could not be determined as either a file or directory" % arg)
        for arg in args:
            self.check_path(arg)
        if self.failed:
            sys.exit(ERRORS['CRITICAL'])

    def check_path(self, path):
        if path == '-' or os.path.isfile(path):
            self.check_file(path)
        elif os.path.isdir(path):
            self.walk(path)
        else:
            die("failed to determine if path '%s' is file or directory" % path)

    # don't need to recurse when using walk generator
    def walk(self, path):
        if self.is_excluded(path):
            return
        for root, dirs, files in os.walk(path, topdown=True):
            # modify dirs in place to prune descent for increased efficiency
            # requires topdown=True
            # calling is_excluded() on joined root/dir so that things like
            #   '/tests/spark-\d+\.\d+.\d+-bin-hadoop\d+.\d+' will match
            dirs[:] = [d for d in dirs if not self.is_excluded(os.path.join(root, d))]
            for filename in files:
                file_path = os.path.join(root, filename)
                if self.re_yaml_suffix.match(file_path):
                    self.check_file(file_path)

    def check_file(self, filename):
        if filename == '-':
            filename = '<STDIN>'
        self.valid_yaml_msg = '%s => YAML OK' % filename
        self.invalid_yaml_msg = '%s => YAML INVALID' % filename
        if filename == '<STDIN>':
            self.check_yaml(sys.stdin.read())
        else:
            if self.is_excluded(filename):
                return
            try:
                with open(filename) as iostream:
                    self.check_yaml(iostream.read())
            except IOError as _:
                die("ERROR: %s" % _)


if __name__ == '__main__':
    YamlValidatorTool().main()

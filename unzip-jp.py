#!/usr/bin/env python

# Extracts a zip archive while converting file names from Shift-JIS to UTF-8.
#
# Example:
#   python unzip-jp.py archive.zip
#
#       Creates a directory `archive` and extracts the archive there.
#
from zipfile import ZipFile
import sys
import os
import errno
import codecs
import getopt


def print_error(err):
    print(err)
    usage()
    exit(2)


def usage():
    print('Usage:\t{0} [-p password] [-o output] [--] archive'
          .format(sys.argv[0]))


try:
    opts, args = getopt.getopt(sys.argv[1:],
                               'ho:p:',
                               ['help', 'output=', 'password='])
except getopt.GetoptError as err:
    print_error(err)

password = None
output = None

for o, a in opts:
    if o in ('-p', '--password'):
        password = a
    elif o in ('-o', '--output'):
        output = a
    elif o in ('-h', '-?', '--help', '--usage'):
        usage()
        print("""Help:\t-p, --password: password
\t-o, --output: output directory (default: archive name)
\t-h, --help: print help.""")
        exit()
    else:
        assert False, 'unhandled option'

if len(args) < 1:
    print_error('No archive name.')

name = args[0]

if output is None:
    output = os.path.splitext(os.path.basename(name))[0]

if not os.path.exists(output):
    os.makedirs(output)

with ZipFile(name, 'r') as z:
    if password:
        z.setpassword(password.encode('cp850', 'replace'))
    for f in z.infolist():
        bad_filename = f.filename
        if bytes != str:
            # Python 3 - decode filename into bytes
            # assume CP437 - these zip files were from Windows anyway
            bad_filename = bytes(bad_filename, 'cp437')
        try:
            uf = codecs.decode(bad_filename, 'sjis')
        except ValueError:
            uf = codecs.decode(bad_filename, 'shift_jisx0213')
        # need to print repr in Python 2 as we may encounter UnicodeEncodeError
        # when printing to a Windows console
        print(repr(uf))
        filename = os.path.join(output, uf)
        # create directories if necessary
        if not os.path.exists(os.path.dirname(filename)):
            try:
                os.makedirs(os.path.dirname(filename))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        # don't try to write to directories
        if not filename.endswith('/'):
            with open(filename, 'wb') as dest:
                dest.write(z.read(f))


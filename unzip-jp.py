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

with ZipFile(name, 'r') as z:
    if password:
        z.setpassword(password.encode('cp850', 'replace'))
    for f in z.infolist():
        # Python 3 - decode filename into bytes
        # assume CP437 - these zip files were from Windows anyway
        try:
            bad_filename = f.filename.encode('cp437')
        except UnicodeDecodeError:
            bad_filename = f.filename
        except UnicodeEncodeError:
            z.extract(f, output)
            continue
        try:
            uf = bad_filename.decode('sjis')
        except ValueError:
            uf = bad_filename.decode('shift_jisx0213')
        # need to print repr in Python 2 as we may encounter UnicodeEncodeError
        # when printing to a Windows console
        print(repr(uf))
        f.filename = uf
        z.extract(f, output)


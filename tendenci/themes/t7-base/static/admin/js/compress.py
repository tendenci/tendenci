#!/usr/bin/env python
import os
import argparse
import subprocess
import sys

here = os.path.dirname(__file__)

def main():
    usage = "usage: %prog [file1..fileN]"
    description = """With no file paths given this script will automatically
compress all jQuery-based files of the admin app. Requires the Google Closure
Compiler library and Java version 6 or later."""
    parser = argparse.ArgumentParser(usage=usage, description=description)
    parser.add_argument("-c", dest="compiler", default="~/bin/compiler.jar",
                        help="path to Closure Compiler jar file")
    parser.add_argument("-v", "--verbose",
                        action="store_true", dest="verbose")
    parser.add_argument("-q", "--quiet",
                        action="store_false", dest="verbose")
    parser.add_argument('file', nargs='*', dest="files")
    args = parser.parse_args()

    compiler = os.path.expanduser(args.compiler)
    if not os.path.exists(compiler):
        sys.exit("Google Closure compiler jar file %s not found. Please use the -c option to specify the path." % compiler)

    if not args.files:
        if args.verbose:
            sys.stdout.write("No filenames given; defaulting to admin scripts\n")
        fnames = [os.path.join(here, f) for f in [
            "actions.js", "collapse.js", "inlines.js", "prepopulate.js"]]
    else:
        fnames = args.files

    for fname in fnames:
        if not fname.endswith(".js"):
            fname = fname + ".js"
        to_compress = os.path.expanduser(fname)
        if os.path.exists(to_compress):
            to_compress_min = "%s.min.js" % "".join(fname.rsplit(".js"))
            cmd = "java -jar %s --js %s --js_output_file %s" % (compiler, to_compress, to_compress_min)
            if args.verbose:
                sys.stdout.write("Running: %s\n" % cmd)
            subprocess.call(cmd.split())
        else:
            sys.stdout.write("File %s not found. Sure it exists?\n" % to_compress)

if __name__ == '__main__':
    main()

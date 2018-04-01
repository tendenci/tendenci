#!/bin/bash

# This script downloads the latest release of Fine Uploader and installs the relevant files in the
# appropriate locations in Tendenci.  Any existing Fine Uploader files are overwritten.

cd "$(dirname "$(readlink -e "$(which "$0")")")"  # This script's location

TemplatePath='templates.t8/uploader/'
StaticPath='static.t8/uploader/'

TmpPath="$(mktemp -d --tmpdir update-fine-uploader.XXX)" || exit 2

set +e    # Make sure the commands after this subshell block are always run,
( set -e  # but exit the subshell immediately if any command in this block fails
  pushd "$TmpPath/" >/dev/null

  # Download the latest release of Fine Uploader
  eval "$(curl -sS https://api.github.com/repos/FineUploader/fine-uploader/releases/latest | \
          perl -n -e '
          if(/"tag_name": "([^"]+)"/) { print "Ver='\''$1'\''"; }
          if(/"browser_download_url": "([^"]*\/fine-uploader.zip)"/)
          { print " URL='\''$1'\''"; exit; }')"
  if [ -z "$URL" ] ; then
    echo >&2
    echo 'ERROR: Failed to obtain URL for latest release of Fine Uploader' >&2
    exit 2
  fi
  wget -O fine-uploader.zip "$URL"

  # Download the latest release of the Fine Uploader server examples
  URL="$(curl -sS https://api.github.com/repos/FineUploader/server-examples/releases/latest | \
         perl -n -e 'if(/"zipball_url": "([^""]*)"/) { print $1; exit; }')"
  if [ -z "$URL" ] ; then
    echo >&2
    echo 'ERROR: Failed to obtain URL for latest release of the Fine Uploader server examples' >&2
    exit 2
  fi
  wget -O server-examples.zip "$URL"

  popd >/dev/null  # "$TmpPath/"

  # Extract the relevant files, overwriting any existing files
  unzip -o "$TmpPath/fine-uploader.zip" \
   LICENSE fine-uploader.min.js fine-uploader.min.js.map \
   -d "$StaticPath"
  unzip -o "$TmpPath/fine-uploader.zip" \
   fine-uploader-new.min.css fine-uploader-new.min.css.map \
   -d "$StaticPath"
  unzip -o "$TmpPath/fine-uploader.zip" \
   '*.gif' \
   -d "$StaticPath"
  unzip -o -j "$TmpPath/fine-uploader.zip" \
   'placeholders/*' \
   -d "$StaticPath"
  unzip -o -j "$TmpPath/fine-uploader.zip" \
   LICENSE templates/simple-thumbnails.html \
   -d "$TemplatePath"
  unzip -o -j "$TmpPath/server-examples.zip" \
   'FineUploader-server-examples-*/license.txt' \
   'FineUploader-server-examples-*/python/django-fine-uploader/fine_uploader/*' \
   -d fine_uploader/

  # Remove HTML comments from the Fine Uploader templates
  echo
  for File in "$TemplatePath"* ; do
    echo "Removing HTML coments from $File"
    perl -0777 -i -p -e 's/<!--.*?-->\n?//sg' "$File"
  done

  # Fix imports in fine_uploader/views.py
  echo 'Fixing imports in fine_uploader/views.py'
  perl -i -p -e 's/^from fine_uploader import/import/; s/^from fine_uploader\./from /;' \
   fine_uploader/views.py

  echo
  echo "Successfully installed Fine Uploader version $Ver"
) ; RET=$?
[ $RET -ne 0 ] && echo -e '\nFailed to install Fine Uploader'

rm -rf "$TmpPath/"

exit $RET

import subprocess

subprocess.check_call(['python', 'manage.py',  'loaddata', 'themes/juniper/apps/boxes/fixtures/willow-default-boxes.json'])
subprocess.check_call(['python', 'manage.py',  'loaddata', 'themes/juniper/apps/forms-builder/forms/fixtures/willow_default_forms.json'])
subprocess.check_call(['python', 'manage.py',  'loaddata', 'themes/juniper/apps/navs/fixtures/nav.json'])

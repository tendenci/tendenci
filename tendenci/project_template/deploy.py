import subprocess

subprocess.check_call(['python', 'manage.py',  'syncdb', '--noinput'])
subprocess.check_call(['python', 'manage.py',  'migrate', '--noinput'])
subprocess.check_call(['python', 'manage.py',  'update_settings'])
subprocess.check_call(['python', 'manage.py',  'copy_themes_to_s3'])
subprocess.check_call(['python', 'manage.py',  'clear_theme_cache'])
subprocess.check_call(['python', 'manage.py',  'collectstatic', '--noinput'])
subprocess.check_call(['python', 'manage.py',  's3_replace_static_urls'])
subprocess.check_call(['python', 'manage.py',  'populate_default_entity'])
subprocess.check_call(['python', 'manage.py',  'populate_entity_and_auth_group_columns'])

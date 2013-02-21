import os

os.system('python manage.py syncdb --noinput')
os.system('python manage.py migrate --noinput')
os.system('python manage.py update_settings')
os.system('python manage.py copy_themes_to_s3')
os.system('python manage.py clear_theme_cache')
os.system('python manage.py collectstatic --noinput')
os.system('python manage.py s3_replace_static_urls')

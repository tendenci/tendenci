# Installation Instruction

Make sure you have Python 2.6 or 2.7 installed. Other versions of Python are not supported in the current build. 

## Set up environment
Our preferred way is to use virtualenv with virtualenvwrapper to create an isolated Python environment. 

+ Install virtualenv
    - `sudo pip install virtualenv`
    - `sudo pip install virtualenvwrapper`
    
+ Add the following lines to your .bashrc and restart your shell

        export WORKON_HOME=$HOME/.virtualenv
        source /usr/local/bin/virtualenvwrapper.sh
        export PIP_VIRTUALENV_BASE=$WORKON_HOME
        export PIP_RESPECT_VIRTUALENV=true

+ Make a virtualenv called `tendenci`
    - `mkvirtualenv tendenci`

+ Activate the virtual environment
    - `workon tendenci`

## Pull Tendenci code
- Clone project. This creates the Tendenci folder in you current working directory
    - `git clone git@github.com:tendenci/tendenci.git`

## Install dependencies:
    cd tendenci
    pip install reportlab==2.5
    pip install -r scripts/requirements.txt

## Setup local settings (optional)

At this point, we recommend you setup local settings. You can do this by renaming `local_settings_sample.py` to `local_settings.py` and uncommenting the necessary sections. This includes `DEBUG`, the `ADMINS` list, the root urls (which is based on the folder you install the project to), and possibly setting up a database other than the default sqlite3. We recommend MySQL.

## Create database tables
    python manage.py syncdb
    python manage.py migrate
    python manage.py update_settings

## Install and select your theme

There are multiple themes available to use in `/templates/themes/`. You can install (bulletpoints, for example), by running the following commands:

    cp -r templates/themes/bulletpoints themes/bulletpoints
    python manage.py set_theme bulletpoints

Now you can test your site by running the command locally:
    python manage.py runserver 0:8000


-----------------------------------------------------------------

## Notes on database and index search engines

- The above installation uses the `sqlite3` as the default database. For a 'large' database engine, check out django doc on how to get your database running.

- Tendenci has the django haystack search built in. You can take advantage of global search and full-text search by setting up your own search engine. For information on how to install a search engine, visit [http://django-haystack.readthedocs.org/en/latest/installing_search_engines.html](http://django-haystack.readthedocs.org/en/latest/installing_search_engines.html).

- If you get PIL imaging gcc errors you might need to install the development version of python. `sudo apt-get install python-dev`

# Installation Instruction

Make sure you have Python 2.6 or 2.7 installed. Other versions of Python are not supported in the current build. 

## Set up environment
Our preferred way is to use virtualenv with virtualenvwrapper to create an isolated Python environment. 

- Install virtualenv
    - `pip install virtualenv`
    - `pip install virtualenvwrapper`
    
- Add the following lines to your .bashrc and restart your shell
	```export WORKON_HOME=$HOME/.virtualenv
	source /usr/local/bin/virtualenvwrapper.sh
	export PIP_VIRTUALENV_BASE=$WORKON_HOME
	export PIP_RESPECT_VIRTUALENV=true```

- Make a virtualenv called `tendenci`
    - `mkvirtualenv tendenci`
- Activate the virtual environment
    - `workon tendenci`
    
## Pull Tendenci code
- Clone project. This creates the Tendenci folder in you current working directory
    - `git clone git@github.com:schipul/Tendenci-5.0.git`
    
## Install dependencies:
	cd Tendenci
	pip install -r scripts/requirements.txt

## Create database table
	python manage.py syncdb
	python manage.py migrate
	
Now you can test your site by running the command locally:
	`python manage.py runserver 0:8000`
	
	
-----------------------------------------------------------------

## Notes on database and index search engines

- The above installation uses the `sqlite3` as the default database. For a 'large' database engine, check out django doc on how to get your database running.

- Tendenci has the django haystack search built in. You can take advantage of global search and full-text search by setting up your own search engine. For information on how to install a search engine, visit 
	`http://django-haystack.readthedocs.org/en/latest/installing_search_engines.html`.  
	

# Tendenci 5.0 Installation Guide

These instructions are for a Mac, so adjust for your dev environment. 

You will need Python 2.6 or 2.7 to run Tendenci. To check the version type 'python' in Terminal.

## Set up Dev Environment
---
Tendenci is designed to use virtualenv with virtualenvwrapper to isolate the application and avoid package conflicts. From Terminal:

### Install virtualenv

    sudo pip install virtualenv
	sudo pip install virtualenvwrapper
    
    
### Edit Environment Variables
Edit your .bashrc (or .bash_profile on a Mac) with the text editor of your choice.

    nano ~/.bash_profile
    
And add the following lines to your .bashrc file.

	export WORKON_HOME=$HOME/.virtualenv
	source /usr/local/bin/virtualenvwrapper.sh
	export PIP_VIRTUALENV_BASE=$WORKON_HOME
	export PIP_RESPECT_VIRTUALENV=true`
    
Restart your shell by closing and opening it, or in terminal type:

	source ~/.bash_profile

### Configure Virtual Environment
Make a virtualenv called `tendenci` excluding site packages for a clean install

    mkvirtualenv --no-site-packages tendenci

Activate the virtual environment

    workon tendenci

Navigate to where you want to create the project locally. For example:

    cd ~/Dropbox/Code/

Verify prompt shows the virtual environment in () and your PWD (Present Working Dir)

    (tendenci)LOCAL:~/Dropbox/Code/

### Pull Tendenci code
Clone project. This will create the Tendenci-5.0 folder in you present working directory

    git clone git@github.com:schipul/Tendenci-5.0.git

### Navigate into the new directory:

    cd Tendenci-5.0

### Install dependencies. 
You may want to look at the requirements.txt file first

    pip install reportlab==2.5
    pip install -r /scripts/requirements.txt

### Create Database and Tables
By default Django and Tendenci use `sqllite3`. SQLlite is for development only and is not recommended if you plan to contribute. See notes on MySQL at the bottom of the page.

But let's get you up and running first. So onward with SQLLite!

From the command line in the root of your project (and in your 'tendenci' virtualenv of course) run:

    python manage.py syncdb
    python manage.py migrate
    python manage.py update_settings

Django will magically create the database and tables for you.

### Install and select your theme

There are multiple themes available to use in `/templates/themes/`. You can install (bulletpoints, for example), by running the following commands:

    cp -r templates/themes/bulletpoints themes/bulletpoints
    python manage.py set_theme bulletpoints

### Search Engine Integration

Determine if you want to set up a search engine for use with TomCat. If you do, you will need to set up Xapian or similar. And of course you do because everyone loves global site search. Please see notes at the bottom of the page.

### Test Your Development Server

Now you can test your site by running the site locally. From terminal run:

    python manage.py runserver 0:8000

In your web browser of choice, navigate to your site at one of these URLs:

	http://127.0.0.1:8000
	
or

	http://127.0.0.1:8000/admin/

You should now see the default homepage for the theme you installed above. Or the admin login prompt if you went straight to /admin/ above. **Sweet!** Tendenci is now up and running locally.

If not, stir and repeat and double check your steps.

Also note we make no attempt to support IE-anything prior to 8.0, and the themes will not exactly match and may not work in later versions of IE as well. YMMV.

## Notes on database and index search engines
---

### Search Engine

Tendenci is designed to use the django haystack search. To take advantage of global search and full-text search you will need to install an engine behind Haystack. But you're on your own for this one.

How to install a search engine in Django: 

[http://django-haystack.readthedocs.org/en/latest/installing_search_engines.html](http://django-haystack.readthedocs.org/en/latest/installing_search_engines.html).

#### MySQL Database Configuration

Tendenci is designed for use with MySQL. It *should* run on PostGres but has not been tested. For more on installing MySQL for Django check the docs at

[https://docs.djangoproject.com/en/dev/ref/databases/#mysql-notes](https://docs.djangoproject.com/en/dev/ref/databases/#mysql-notes)

We recommend you install MySQL **outside** of your Virtual Environment because you will likely wind up with multiple databases for various projects. Requirements.txt **does** install pyodbc but not TDS. Again see docs above and use your google foo. Your TDS `freetds.conf` file on a Mac is located at:

	/opt/local/etc/freetds/freetds.conf

So now your MySQL database is up and running, you can connect to it and do your thing, right? Great! Moving forward‚Ä¶

Django syncdb will *not* create a MySQL database for you like it does with sqllite. You need to manually create a MySQL Database. You can do this in your GUI of choice (Sequel Pro, PHPmyadmin, etc) or from the mysql command line interface as follows (use `sudo` prefix if needed to run `mysql`):

	mysql -u root -p
	<enter your password when prompted>
	mysql> create database tendenci;
	mysql> show databases;	

Now you have a blank db named `tendenci`. Or better yet use a name specific to your project.

Next configure your settings.py file to connect to mysql instead of the sqllite db. This should look something like this:

	DATABASES = {
	    'default': {
	        'ENGINE': 'django.db.backends.mysql',
	        'NAME': 'tendenci',
	        'USER': '<YOUR DATABASE USER NAME>',
	        'PASSWORD': '<YOUR DATABASE PASSWORD>',
	        'HOST': '',
	        'PORT': '',
	        'OPTIONS': {"init_command": "SET storage_engine=INNODB",}
	    }
	}

A few things to note - the tendenci database must be the `default` database in the application because of how Django middleware handles transactions. And the connection must use the `INNODB storage engine`, again because of Django requirements.

On your local development box you can leave HOST and PORTS blank in your connection. Production requires them.

Now repeat the db config steps with your new `default` database. From the command line in the root of your project (and in your 'tendenci' virtualenv of course) run:

    python manage.py syncdb
    python manage.py migrate
    python manage.py update_settings

As always the database connection is the hardest part so be sure to read the docs if you aren't successful at this point.

[https://docs.djangoproject.com/en/dev/ref/databases/#mysql-notes](https://docs.djangoproject.com/en/dev/ref/databases/#mysql-notes)
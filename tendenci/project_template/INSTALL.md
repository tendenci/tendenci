# Installation instructions

You can use the following installation instructions to install a local Tendenci site. This Django project is intended to help create a Tendenci site that you can deploy on a public hosting, but it's recommended that you install locally first in order to test your themes and designs.

## Pre-config

Install pip [http://www.pip-installer.org/](http://www.pip-installer.org/):
    
    sudo easy_install pip

Install virtualenv [http://www.virtualenv.org/](http://www.virtualenv.org/):

    pip install virtualenv
    pip install virtualenvwrapper

You'll also need to have Git set up: [https://help.github.com/articles/set-up-git](https://help.github.com/articles/set-up-git).

On Mac OSX 10.7 or higher: you will need xcode 4.4.1 (in app store) or the [osx-gcc-installer package](https://github.com/kennethreitz/osx-gcc-installer/downloads).

## Setting up the database

Tendenci is designed for use with PostgreSQL. You will need to have a PostgreSQL server running locally. If you are on OS X, we recommend Postgres.app: [http://postgresapp.com/](http://postgresapp.com/) to get up and running fast.

We recommend you install PostgreSQL **outside** of your virtual environment because you will likely wind up with multiple databases for various projects.

Django syncdb will *not* create a PostgreSQL database for you like it does with sqlite. You need to manually create a PostgreSQL database through your GUI or from the psql comand line.

With Postgres.app installed, you can create a database from Terminal:

    psql -h localhost
    CREATE DATABASE your_database_name;

You can also create a database in your GUI of choice (recommended: [http://www.pgadmin.org/](http://www.pgadmin.org/)).

For more on installing PostgreSQL for Django check the docs at:

[https://docs.djangoproject.com/en/dev/ref/databases/#postgresql-notes](https://docs.djangoproject.com/en/dev/ref/databases/#postgresql-notes)

## Downloading Tendenci

Clone the repo, then travel to its directory. You can replace "your-site-name" with whatever name you like.

    git clone git@github.com:tendenci/tendenci-site.git your-site-name
    cd !$

You should now be in `~/Dropbox/Code/your-site-name`, or whatever the path is to your project directory. Let's remove the .git so that your changes won't be tracked in the main tendenci-site repo.

    rm -rf .git

If you want to track your changes to **your app** (strongly recommended), then you can create a new git repo specific to your project by running the following command:

    git init
    git add .
    git commit -am "initial commit"

## Creating your virtual environment

It is recommended that you create your virtual environment inside this project directory. By default, the `.gitignore` file will ignore items in a directory named `venv`. We recommend you create a virtual environment with that name with the following commands (remember that you should be inside your project directory here):

    virtualenv venv
    source venv/bin/activate

You will need to run `source venv/bin/activate` from your project directory every time you are working on the project.

You will now need to populate your virtual environment by running the following command:

    pip install -r local_requirements.txt

This will download the Tendenci package, all of its dependencies, and a few additional packages. This may take a few minutes depending on your internet connection speed.

<!--- Alex note: This section to change after Ed's settings folder is committed. --->
## Creating a local environment file

Next, create your local environment. Tendenci will load a local file, `.env`, which will not be committed into your repo.

An example of this file, `.env_example`, can be copied using the following command:

    cp .env_example .env

You will now need to **edit your** `.env` **file** to change the database name:

    nano .env

 Replace the word `tendenci` with your database's name. CTRL + O and Return to save your changes. CTRL + X to quit editing.

You can add additional local environment variables to the `.env` file by defining them as `KEY='value'`. Settings that are sensitive (like passwords) or vary per environment should be added to this file. 

For example, to use Amazon's S3 service as a database backend, set the following key/value pairs in your `.env` file:

    AWS_ACCESS_KEY_ID='MY_ACCESS_KEY'
    AWS_SECRET_ACCESS_KEY='MY_SECRET_KEY'
    AWS_STORAGE_BUCKET_NAME='bucket_name'
    AWS_LOCATION='new-site-name'


## Deploying

Next, we can run the deploy script to populate the database. The theme `salonify` is used below by default, but you may create a custom theme and use `python manage.py set_theme your_theme_name` to set it to that theme.

    python deploy.py
    python manage.py set_theme salonify
    python manage.py createsuperuser
    python manage.py collectstatic --noinput

## Running and testing

Be sure that you're in your project directory and inside your virtual environment. You can now test your site by running the standard Django `runserver` management command with:

    python manage.py runserver

In your browser, navigate to your site at:

    http://127.0.0.1:8000

You should see the default homepage for the theme you have installed. Tendenci is now up and running locally.

------

# Deploying on Heroku

You do not need to be able to run tendenci locally in order to deploy to Heroku. Simply follow the steps below.

## Prerequisites

You need to have a Heroku account: [http://heroku.com](http://heroku.com) and the heroku toolbelt: [https://toolbelt.heroku.com/](https://toolbelt.heroku.com/) installed. It is also recommended that you have your payment options configured, though all of the settings below allow your site to run for free.

## Cloning and pushing to Heroku

For the instructions below, please replace `new-site-name` with the name of your site. The name can contain dashes or underscores, but not spaces.

    git clone git@github.com:tendenci/tendenci-site.git new-site-name
    cd new-site-name
    rm -rf .git

We remove the .git directory to disconnect this code from the tendenci-site main repo. You can now create a new git repo from this code that will be specific to your site.

    git init
    heroku create new-site-name
    git add .
    git commit -am "initial commit"
    git push heroku master

Your site will now be created on Heroku. The first build may take up to 10 minutes due to the initial download of all of the dependencies. Additional updates will not take as long.

## Configuring Heroku Addons

Heroku offers several addons: [https://addons.heroku.com/](https://addons.heroku.com/) for apps that include Database connections, Memcached caching, email servers, and other useful addons. We will use the database and the Memcached addons in the instructions below.

You can add on the free tier of the memcache addon: [https://addons.heroku.com/memcache](https://addons.heroku.com/memcache) by running the following command. This addon is free, but you need to have verified your account to add it:

    heroku addons:add memcache:5mb

To configure the database, we must add the database and then promote it as the main database. Database names from Heroku's Postgresql service: [https://postgres.heroku.com/](https://postgres.heroku.com/) follow the pattern `HEROKU_POSTGRESQL_COLOR` where `COLOR` is an actual color name like `TEAL` or `ORANGE`. This will vary per installation, but we can look this up by running `heroku config`. The second command below will find the default color name and use it.

To create and configure the database, run the following commands:

    heroku addons:add heroku-postgresql:dev
    heroku pg:promote `heroku config | grep POSTGRES | cut -d : -f 1`

## Setting up the database

Next, we can run the deploy script to populate the database. The theme `salonify` is used below by default, but you may create a custom theme and set your theme to that themes.

    heroku run python deploy.py
    heroku run python manage.py set_theme salonify
    heroku run python manage.py createsuperuser

## Configuring static assets

We have two options for static assets: serving them locally and loading from a remote location like Amazon S3: [http://aws.amazon.com/s3/](http://aws.amazon.com/s3/).

To load locally, we only need to set our `DEBUG` variable to True with the following command:

    heroku config:set DEBUG=True

To configure S3, set the config options with the following command:

    heroku config:set AWS_ACCESS_KEY_ID='MY_ACCESS_KEY'
    heroku config:set AWS_SECRET_ACCESS_KEY='MY_SECRET_KEY'
    heroku config:set AWS_STORAGE_BUCKET_NAME='bucket_name'
    heroku config:set AWS_LOCATION='new-site-name'

Now, run the following command:

    heroku run python manage.py collectstatic --noinput

Finally, you can open your site!

    heroku open

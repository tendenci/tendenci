# Tendenci Installation

You can use the following installation instructions to install a local Tendenci site. This Django project is intended to help create a Tendenci site that you can deploy on a public hosting, but it's recommended that you install locally first in order to test your themes and designs.

## Setting up the database

Tendenci is designed for use with PostgreSQL. You will need to have a PostgreSQL server running locally. If you are on OS X, we recommend Postgres.app: [http://postgresapp.com/](http://postgresapp.com/) to get up and running fast.

With Postgres.app installed, you can create a database from Terminal:

    psql -h localhost -c "CREATE DATABASE tendenci"

You can also create a database in your GUI of choice (recommended: [http://www.pgadmin.org/](http://www.pgadmin.org/)).

For more on installing PostgreSQL for Django check the docs at: [https://docs.djangoproject.com/en/dev/ref/databases/#postgresql-notes](https://docs.djangoproject.com/en/dev/ref/databases/#postgresql-notes)

## Downloading Tendenci

Make a folder for your site and cd into it. Replace 'sitename' with the name of your site.
 
    mkdir sitename
    cd sitename

It's best practice to make a virtual environment for your site. You will need [virtualenv](http://www.virtualenv.org/) installed for the next step. If you don't have it, you can install it with `pip install virtualenv`. Make a virtual environment called 'venv' and activate it.

    virtualenv venv
    source venv/bin/activate

Install Tendenci. This download and install step may take a few minutes.

    pip install tendenci

Once this is done, you can setup django project with the following:

    create-tendenci-project

If you created a database with a name other than 'tendenci', you will need to edit the database name 'tendenci' inside the `.env` file that is created.

Next, we install requirements for the project. We add tendenci videos as an example to use.

    pip install -r requirements/dev.txt

Now we are ready to use our deploy script.

    python deploy.py

At this point, we can load some default content into our site with the following command:

    python manage.py insert_npo_defaults

Next, we load our theme:

    python manage.py set_theme twenty-thirteen

To create your login, run the following command and fill in the prompts:

    python manage.py createsuperuser

Finally, we can use the runserver command so that we can view the site in our browser:

    python manage.py runserver

Open http://127.0.0.1:8000/ in your browser to see your tendenci site!

**Optional:** You can add additional local environment variables to the `.env` file by defining them as `KEY='value'`. Settings that are sensitive (like passwords) or vary per environment should be added to this file. For example, to use Amazon's S3 service as a file storage backend, set the following key/value pairs in your `.env` file:

    AWS_ACCESS_KEY_ID='MY_ACCESS_KEY'
    AWS_SECRET_ACCESS_KEY='MY_SECRET_KEY'
    AWS_STORAGE_BUCKET_NAME='bucket_name'
    AWS_LOCATION='new-site-name'

----------

If you are interested in deploying your site to Heroku, see our online instructions at [https://github.com/tendenci/tendenci/blob/master/docs/heroku.md](https://github.com/tendenci/tendenci/blob/master/docs/heroku.md)

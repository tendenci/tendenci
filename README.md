# Tendenci

# WAIT! HOLD ON THERE JUST A SEC. UPDATE UPDATE UPDATE! TRY TENDENCI 6!

The installation information below will still work for the master branch, but if you are considering Tendenci, I'd suggest you try the Tendenci 6 branch (not "master" but "tendenci6") and of course use the project template located here

https://github.com/tendenci/tendenci-project-template

-------------

Changes needed to upgrade tendenci 5 to tendenci 6. Programming notes from Jayjay Montalbo.

There will be some issues on the installed external module such as committees and donations on first install of the tendenci6.0 branch. To resolve this, we should update the requirements/common.txt of the client site to have this https://github.com/tendenci/tendenci/blob/tendenci6.0/tendenci/project_template/requirements/common.txt . Run 

	pip install -r requirements.txt afterwards.

Issue --- gevent/libevent.h:9:19: fatal error: event.h: No such file or directory . Solution is just run

	sudo apt-get install libevent-dev

Issue --- _pylibmcmodule.h:42:36: fatal error: libmemcached/memcached.h: No such file or directory . Solution is just run

	sudo apt-get install libmemcached-dev

Update the conf/urls.py and conf/local_urls.py files on the client site files should be updated in preparation for the update. All urls.py files inside the addons directory should be updated first. 

A sample update that we could include is this. From this code snippet, that exists on urls.py,

	from django.conf.urls.defaults import *

We update that snippet to the one shown below so that we have backward compatibilities (just preparing the site and not yet updating)

	try:
	    from django.conf.urls.defaults import *
	except:
	    from django.conf.urls import *

Update all the templates on the custom addons that has templates that used the old url resolvers. Add the quotation marks so that there will no rendering issues of the template.

	from {% url go-to-something %} we will have {% url 'go-to-something' %} 

Update conf/settings.py of the client site. Edit this:

	from tendenci.core.registry.utils import update_addons

to this

	from tendenci.apps.registry.utils import update_addons

Update haystack config on the conf/settings.py from this:

	HAYSTACK_SEARCH_ENGINE = env('HAYSTACK_SEARCH_ENGINE', 'solr')
	HAYSTACK_URL = env('WEBSOLR_URL', 'http://localhost')

	if HAYSTACK_SEARCH_ENGINE == "solr":
	    HAYSTACK_SOLR_URL = HAYSTACK_URL

	if HAYSTACK_SEARCH_ENGINE == 'whoosh':
	    HAYSTACK_WHOOSH_PATH = os.path.join(PROJECT_ROOT, 'index.whoosh')

to this:

	__engine = env('HAYSTACK_SEARCH_ENGINE', 'solr')
	if __engine == "solr":
	    HAYSTACK_CONNECTIONS = {
	        'default': {
	            'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
	            'URL': env('WEBSOLR_URL', 'http://localhost'),
	        }
	    }
	elif __engine == "whoosh":
	    HAYSTACK_CONNECTIONS = {
	        'default': {
	            'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
	            'PATH': os.path.join(PROJECT_ROOT, 'index.whoosh'),
	        }
	    }

Might encounter migration error with djcelery. To solve the issue, run 

	python manage.py migrate djcelery 0001 --fake and re-run deploy.py

Truncate Words deprecated - truncate_words removed in Django 1.6

	try:
	    from django.utils.text import truncate_words
	except ImportError:
	    from django.template.defaultfilters import truncatewords as truncate_words

Expect major issues on migrations. Use "--fake" as needed until this can be scripted


## Credits

Props [https://github.com/tendenci/tendenci/blob/master/docs/credits.md](https://github.com/tendenci/tendenci/blob/master/docs/credits.md)



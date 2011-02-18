## General 

#### Django Filters
Filters allow you to modify the output of a field. Filters can be added with a pipe at the end of a field and then the filter name with an optional colon and arguments.

    articles.release_dt|date:"M d, Y"

Filters can be linked like `|escape|truncatewords:30`. See [Django Filters Docs](http://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs#built-in-filter-reference) for the full list.

-  [date](http://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs#date) - specify the date output.
-  [safe](http://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs#safe) - Print out actual HTML instead of the elements.
-  [truncatewords](http://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs#truncatewords) - Only print a certain number or words
-  [urlize](http://docs.djangoproject.com/en/dev/ref/templates/builtins/?from=olddocs#urlize) - Converts a link to an anchor link

#### Common Arguments

Arguments allow you to modify the list of items that comes back. They are optional but are used often for most content lists. For instance, you may only want to show 4, or you might want them ordered a certain way. Arguments are added at the end of the first line of the template tag like such:

    {% list articles as articles limit=5 tags="featured" q="tendenci" order="release_dt" %}
    
The arguments below are used on all template tags:

- `user=` searches based on permissions of the logged in user. The default is a logged out (anonymous) user.
- `limit=` limits the number of items in the list. The default is 3.
- `tags=` seaches based on the tags on the items. Note, some apps do not use tags.
- `q=` searches as a search term for a full text search of the items

These arguments are currently used on select apps only:

- `order=` lets you select the order of the items
- `random` pulls a random group of items. You do not need to pass an addition value (like `random=something`) as `random` works on it's own.

Arguments work together, so if you have `tags="featured"` and `limit=100`, you may not get 100 items if there are not that many tagged with "featured". Random will pull from the possible total and cutoff at the limit. If there were 20 items tagged "featured", the limit was 5, and random was used, then 5 of the 20 items would be returned in a random order. 


## Articles

#### Template tag:
    {% list_articles as articles_list user=user limit=3 %}
        {% for article in articles_list %}
            {{ article.FIELDNAME }}
        {% endfor %}

#### Fields
Fieldnames used in the template tag as `{{ article.FIELDNAME }}`

- **slug** the slug for the article
- **headline** the title of the article
- **summary** the summary of the article
- **body** the full body of the article
- **source** the source URL for the article
- **website** the link to the website for the article (not the slug)
- **release_dt** the published date of the article

#### HTML code example

    {% list_articles as articles %}
        {% for article in articles %}
            <h2><a href="{{ article.get_absolute_url }}">{{ article.headline }}</a></h2>
            <span class="date">{{ article.release_dt }}</span>
            <div class="article summary">{{ article.summary }}</div>
        {% endfor %}
                
## Jobs

#### Template tag:
    {% list_jobs as jobs_list %}
        {% for job in jobs_list %}
            {{ job.FIELDNAME }}
        {% endfor %}

#### Fields
Fieldnames used in the template tag as `{{ job.FIELDNAME }}`

- **slug** the slug for the job
- **title** the title of the job
- **description** the summary of the job
- **location** the location of the job
- **post_dt** the date of the job post listing

#### HTML code example

    {% list_jobs as jobs_list limit=3 %}
        {% for job in jobs_list %}
            <h2><a href="{{ job.get_absolute_url }}">{{ job.title }}</a></h2>
            <span class="date">{{ job.post_dt }}</span>
            <div class="job summary">{{ job.description|truncatewords_html:"12" }}</div>
        {% endfor %}
            
## Events

#### Template tag:
    {% list_events as events_list %}
        {% for event in events_list %}
            {{ event.FIELDNAME }}
        {% endfor %}

#### Fields
Fieldnames used in the template tag as `{{ event.FIELDNAME }}`

- **guid** the ID for the event (useful for the link)
- **title** the title of the event
- **description** the description of the event
- **start_dt** the start time of the event
- **end_dt** the end time of the event

#### Foreign fields
The foreign fields come from separate tables, so they are used as `{{ event.FOREIGNFIELD.FOREIGNFIELDNAME }}`

- **place.name** the name of the location
- **place.url** the url of the location
- **type.name** the name of the event type
- **type.slug** the slug for a link to the event type
- **registration_configuration.enabled** boolean if the event has registration

#### HTML code example

    {% list_events as events_list limit=3 %}
        {% for event in events_list %}
            <h2><a href="{{ event.get_absolute_url }}">{{ event.title }}</a></h2>
            <div class="event desc">{{ event.description}}</div>
            <span class="event-location">{{ event.place.name }}</span>
            <span class="event-type"><a href="{{ url event.type }}">{{ event.type.name }}</a></span>
        {% endfor %}

## Photos

#### Template tag:
    {% list_photos as photos_list %}
        {% for photo in photos_list %}
            {{ photo.FIELDNAME }}
        {% endfor %}

#### Fields
Fieldnames used in the template tag as `{{ photo.FIELDNAME }}`

-  **guid** the id for the photo (for the slug)
-  **title** the title of the photo
-  **caption** the caption of the photo
-  **tags** the photo's tags
-  **get\_thumbnail\_url** the local url to the photo - 100x75 crop
-  **get\_small\_crop\_url** the local url to the photo - 100x75 crop
-  **get\_display\_url** the local url to the photo - 500x275 no crop
-  **get\_large\_url** the local url to the photo - 500x500 no crop

#### HTML code example

    {% list_photos as photos_list limit=6 %}
        {% for photo in photos_list %}
            <a href="{{ photo.get_absolute_url }}"><img src="{% photo_image_url photo size=80x120 crop=True %}" /></a>
            <span class="photo-title"><a href="{{ photo.get_absolute_url }}">{{ photo.title }}</a></span>
        {% endfor %}

## Stories

#### Template tag:
    {% list_stories as stories_list %}
        {% for story in stories_list %}
            {{ story.FIELDNAME }}
        {% endfor %}

#### Fields
Fieldnames used in the template tag as `{{ story.FIELDNAME }}`

- **full\_story\_link** the slug for the story link
- **title** the title of the story
- **content** the content of the story
- **photo.url** the url to the photo for the story

#### HTML code example

    {% list_stories as stories_list limit=3 %}
        {% for story in stories_list %}
            <img src="{{ story.photo.url }}" alt="{{ story.title }}" />
            <h2><a href="{{ story.full_story_link }}">{{ story.title }}</a></h2>
            <div class="story summary">{{ story.content }}</div>
            <span class="read-more"><a href="{{ story.full_story_link }}">Read More</a></span>
        {% endfor %}

# Newsletter Templates

To begin using Tendenci templates, start by uploading your template you your website at http://example.com/campaign_monitor/templates/add/

The options for including content for Tendenci Newsletter templates are from Articles, Jobs, News, Pages, and Events. You can you use the code below in your templates:

### Articles

Standard formatted article content:

`{{ art_content }}` or `{{ articles_content }}`

Custom formatted article content:

    {% for article in articles_list %}
        <h2><a href="{{ article.get_absolute_url }}">{{ article.headline }}</a></h2>
        <span class="date">{{ article.release_dt }}</span>
        <div class="article summary">{{ article.summary }}</div>
    {% endfor %}

### Jobs

Standard formatted job content:

`{{ jobs_content }}`

Custom formatted job content:

    {% for job in jobs_list %}
        <h2><a href="{{ job.get_absolute_url }}">{{ job.title }}</a></h2>
        <span class="date">{{ job.post_dt }}</span>
        <div class="job summary">{{ job.description|truncatewords_html:"12" }}</div>
    {% endfor %}

### News

Standard formatted news content:

`{{ news_content }}`

Custom formatted news content:

    {% for news in news_list %}
        <h2><a href="{{ news.get_absolute_url }}">{{ news.headline }}</a></h2>
        <span class="date">{{ news.release_dt }}</span>
        <div class="news summary">{{ news.summary }}</div>
    {% endfor %}

### Pages

Standard formatted pages content:

`{{ pages_content }}`

Custom formatted pages content:

    {% for news in news_list %}
        <h2><a href="{{ news.get_absolute_url }}">{{ news.title }}</a></h2>
        <div class="page summary">{{ page.content }}</div>
    {% endfor %}

### Events

Custom formatted events content:

    {% for event in events_list %}
        <h2><a href="{{ event.get_absolute_url }}">{{ event.title }}</a></h2>
        <div class="event desc">{{ event.description}}</div>
        <span class="event-location">{{ event.place.name }}</span>
        <span class="event-type"><a href="{{ url event.type }}">{{ event.type.name }}</a></span>
    {% endfor %}
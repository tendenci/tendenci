Templates are made of .html files. They mostly contain HTML. They also contain Context Variables.

**What is a Context?**

A context is something that is loaded onto the specific page. If you are viewing an Article, then the Article context is filled with information (title, date, author, content, etc.) about that specific article. We can use the context of that Article, say author, to pull in more information from another place. A context can also be a group of Articles, like on a search page.

**What kinds of things can I do in a template?**

You can display information from the Contexts that are passed to the page. One example is the logged in Users name, since the User context is almost always passed. You can also change the way certain fields from a Context are displayed. We can move the Authors name on an article from a byline at the top to down at the bottom of the content. We can also remove certain bits of information that are displayed by default, like the date of creation on a regular page. Along with the standard information that is passed in a Context, we can also use template tags to gain other information or to change what shows from a Context.

**What is a Template Tag?**

Django has some built-in template tags that can be very useful in developing themes. Some examples are `{% if %}` and `{% for %}` loops. Template tags begin and end with a `{%`.

T5 has custom template tags for most modules. For example, we can grab the latest 5 articles and display them in a list in the sidebar. The code required to this is in a couple of parts.

1. We use a T5 template tag to get the 5 articles from the database.

        {% list_articles as articles_list limit=5 %}

    `list_articles` is the actual template tag name, like "if" or "for". The word `articles_list` is our temporary context variable. It could be `baby_elephants`, but we usually choose to name it something more relevant. We could use a descriptive name like `articles_sidebar` if we wanted. The only thing we shouldn't name it is just plain `articles`, because that Context Variable is used on the Articles search page, and it may cause that page to have errors. When in doubt, add some detail to the context variable name. At this point, all we have is a group or articles.
    
2. We loop through the list using the `{% for %}` template tag

        {% for article in articles_list %}
    
    do something for this one article
    
        {% endfor %}
    
    A for loop takes a group of items and then does something for each one. In our example, we have 5 items. The for loop doesn't care how many items there are, as long is there is at least one. In the code, we can set a word (variable) to represent each item. In this case, that word is "article". The loop also has to know which list of things to pull from. We define this as we did in step 1, with "articles_list". This word can be different in step 1, but step 2 must use the same word (context variable). 
    
Inside the loop is where the content get's displayed. There, we can add HTML and change the way the content is laid out for the individual articles. We may want the title in an H4 linked to the article. The variables from the context are displayed with `{{ }}` and use a period to separate the context and the specific field. An example is `{{ article.title }}`. We could want the authors name and the date it was published, too. Now, what if we want a special format for the date, like m.d.y, or if it's an international client, d.m.y?
    
**What is a filter?**

A filter changes the output of a variable. These variables are generally thought of as fields on a form. Title, author, date, etc. For news we may have contact information.

There are some Django filters as well as some custom ones for T5. An example is Title, which capitalizes the first letter of each word automatically. 

An example of how to add a filter is as such 

    {{ article.title|title }}

In this case, the first word title is the field from the article. The second one, after the vertical bar, is the filter.

Date is also a filter. It works using specific letters to represent month names, day numbers, etc. I always look this up from a list.

    {{ article.publish_date|date:"D d M Y" }}

A full list of django template tags and filters is available at (http://docs.djangoproject.com/en/dev/ref/templates/builtins/)

A list of those custom to T5 is in development.

Please explore the list online. You can do some really cool things like:

Tags

- display the first item in a set differently
- add an even/odd class automatically
- set a custom variable value on the page
- only show a month if the name has changed in a list (feb to march)

Filters

- block or allow HTML content to be shown
- set a default value
- separate tags by commas or spaces
- pick a random item from the list
- show the time since something happened
- truncate a section of text
- do a word wrap


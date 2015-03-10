# Theme Guidelines

- Authors: John-Michael Oswalt
- Last update: 2013-10-02

The main sections are:

- [Theme Structure](#theme-structure)
- [Stylesheet Conventions](#stylesheet-conventions)
- [Template Conventions](#template-conventions)
- [HTML and Class Name Conventions](#html-and-class-name-conventions)
- [Full Theme Examples](#full-theme-examples)

## Theme Structure

A theme should be installed in the themes folder of the site root. The themename should be lowercase with hyphens replacing spaces, like `theme-name`. The file tree should be as follows:


- theme-name

  - theme.info
  - screenshot.png
  - settings.json

  - media

      - css
    
          - styles.css

      - fonts

          - Font-name.eot
          - Font-name.svg
          - Font-name.ttf
          - Font-name.woff
    
      - img
    
          - apple-touch-icon.png
          - favicon.ico
          - header-background.jpg (optional)
          - logo.png

      - js
    
          - jquery.cycle.all.min.js
          - jcarousellite.min.js

  - templates

      - homepage.html
      - default.html
      - header.html (optional)
      - footer.html (optional)
      - sidebar.html (optional)
    
### Root

**theme.info** - This file contains a set of attributes associated with a theme. See the example below for some common attributes.

    name = Theme Name
    description = Theme Name custom theme for Tendenci CMS.
    tags = homepage rotator, responsive
    screenshot = screenshot.png
    author = John Doe
    author uri = http://example.com
    version = 1.0
    create_dt = 2013-06-20 15:34:00

**screenshot.png** - This file is a full page screenshot of the theme after it has been loaded with the fixtures using the `load_npo_defaults` management command.

**settings.json** - This file contains settings for the Tendenci site settings. These settings are written in json and are installed whenever the `update_settings`, `set_theme`, or `install_theme` command is run.


### Media

#### css

**media/css/styles.css** - This is the main stylesheet to be used for the site. It will include all css, including menus and media queries.

#### fonts

**media/fonts/Font-name.*** - These are the files for fonts used in the theme. Font files should be copied here, not referenced externally. The 4 formats of `.eot`, `.svg`, `.ttf`, and `.woff` should all be included.

#### img

**media/img/apple-touch-icon.png** - This is the file used by iOS devices when a site is saved to an iOS homescreen.

**media/img/favicon.ico** - This is the favicon for our site.

**media/img/header-background.jpg** (optional) - This is an example of another image used with the site theme.

**media/img/logo.png** - This is the main logo for the site. This can be a `.png` or `.jpg`.


The `media/img` directory should hold all of the images used with the theme.

#### js

**media/js/jquery.cycle.all.min.js** - This is one optional library to use for rotators and sliders.

**media/js/jcarousellite.min.js** - This is the other optional library to use for rotators and sliders.

No other javascript libraries should be used for rotators or sliders. Any other necessary javascript libraries like hint, easing, etc. should be included in `media/js`.


### Templates

**templates/default.html** - This file defines the HTML that is used when a page other than the homepage is loaded.

**templates/footer.html** (optional) - This file should contain the HTML used in the footer. The footer is the last portion of HTML for the theme that would be shared by both the `homepage.html` and `default.html` templates. This file is used to prevent duplicate code in those templates and is **included** within those files. Javascript and CSS should NOT be included in this file.

**templates/header.html** (optional) - This file should contain the HTML used in the header. The header typically includes the logo, login box, search box, and navigation that would be shared by both the `homepage.html` and `default.html` templates. This file is used to prevent duplicate code in those templates and is **included** within those files. Javascript and CSS should NOT be included in this file.

**templates/homepage.html** - This file defines the HTML that is used when the homepage of the site is loaded.

**templates/sidebar.html** (optional) - This file should contain the HTML used in the sidebar. The sidebar has content that would be shared by both the `homepage.html` and `default.html` templates. This file is used to prevent duplicate code in those templates and is **included** within those files. Javascript and CSS should NOT be included in this file.

### Overridden Templates

On occasion, it may be necessary to override a template used in the site. For example, if the default view of an article needed to be edited for this theme, the overridden template would reside in the theme at **templates/articles/view.html**.

## Stylesheet conventions

### Comments

Specify the about comments, similar to WordPress, like so:

    /*   
    Theme Name: The Theme Name
    Theme URI: http://tendenci.com/
    Description: Custom theme design for Tendenci
    Designer: John Doe
    Designer URI: http://example.com/
    Developer: Jane Doe
    Developer URI: http://example.com/jdoe/
    Version: 1.0
    */

CSS comments are very similar, written like so:

    /* ------------------------------
        Reset HTML 
    ------------------------------ */

The header line begins with forward slash, asterisk, and a space, followed by 30 dashes. The footer line is the same, but in reverse. The name row has 4 spaces, then the name of the comments section.

Comments should have empty line after them. The code should begin on the very next line. Comments should have 1 empty line above them.

### Reset

A standard CSS reset should be used like so:

    /* ------------------------------
        Reset HTML 
    ------------------------------ */
    html, body, div, span, object, iframe,
    h1, h2, h3, h4, h5, h6, p, blockquote, pre,
    abbr, address, cite, code, del, dfn, img, ins, kbd, q, samp,
    small, strong, sub, sup, var, b, i, dl, dt, dd, ol, ul, li,
    fieldset, form, label, legend,
    table, caption,
    article, aside, canvas, details, figcaption, figure,
    footer, header, hgroup, menu, section, summary,
    time, mark, audio, video {
      margin: 0;
      padding: 0;
      border: 0;
      font-size: 100%;
      font: inherit;
      vertical-align: baseline;
    }
    
    article, aside, details, figcaption, figure,
    footer, header, hgroup, menu, section {
      display: block;
    }
    
This reset should have the comment above it as demonstrated. After this bit of code, an empty line should be present, followed by the next CSS comment denoting the next section.

### Base HTML Elements

Here is a sample of code that can be used for base HTML elements.

    /* ------------------------------
        Base HTML Elements 
    ------------------------------ */
    body { background-color: #ffffff; font-family: Helvetica, Arial, "sans-serif"; font:13px/1.231 sans-serif; *font-size:small; color: #333333; margin: 0; }
    
    h1, h1 a { font-size: 32px; line-height: 34px; text-decoration: none; font-weight: bold; margin-bottom: 10px; }
    h2, h2 a { font-size: 24px; line-height: 26px; text-decoration: none; font-weight: bold; margin-bottom: 10px; }
    h3, h3 a { font-size: 20px; line-height: 22px; text-decoration: none; font-weight: bold; margin-bottom: 6px; }
    h4, h4 a,
    h5, h5 a,
    h6, h6 a { font-size: 16px; line-height: 18px; text-decoration: none; font-weight: bold; margin-bottom: 6px; }
    
    a { color: #0000ff; }
    a:hover { color: #5555ff; }
    a:visited, a:active { color: #BB55ff; }
    
    p { margin-bottom: 10px; line-height: 18px; }
    
    ul, ol { margin: 0 0 10px 24px; }
    ol { list-style-type: decimal; }
    
    select, input, textarea, button { font:99% sans-serif; }
    pre, code, kbd, samp { font-family: monospace, sans-serif; margin-bottom: 10px; padding: 8px; }
    
    small { font-size: 85%; }
    strong, th { font-weight: bold; }
    
    td, td img { vertical-align: top; } 
    
    sub { vertical-align: sub; font-size: smaller; }
    sup { vertical-align: super; font-size: smaller; }
    
    blockquote { margin: 0 0 10px 20px; }

Note that several variables are used in these base elements. You can also see the layout of a single style. Taking a closer look at the `p` tag, we can see some ways of writing our CSS.

    p { margin-bottom: 10px; line-height: 18px; }

All of the styles are on 1 line. There is a space after the open bracket, and a space before the closing bracket. There is a space between a property and it's value, and there is a space between values. All values (especially the last one) are closed with a semi-colon. Below is an example of the same property without these spaces.

    p {margin-bottom:10px;line-height:18px;}

Yuck. While this code will still work, it is hard to read and becomes more difficult to manage. Same goes for writing out properties on separate lines. The document becomes too long to quickly read and understand.

### Extras

Mostly this is just the clearfix code. This should be the last section of CSS in the document.

    /* ------------------------------
        Extras 
    ------------------------------ */
    .clear { clear: both; }
    .clearfix:before, .clearfix:after { content: "\0020"; display: block; height: 0; visibility: hidden; }
    .clearfix:after { clear: both; }
    .clearfix { zoom: 1; }


### Main Sections

Main sections of the stylesheet should be written like the above example, with a comment heading at the top. Styles should be written in a similar pattern to the HTML. See below for an example order of the CSS sections.

- Reset
- Base HTML Elements
- Header
- Homepage Top (Rotator)
- Homepage Body
- Interior Body
- Interior Sidebar
- Footer
- Tendenci Overrides
- Extras
- Media Queries

## Template conventions

For the `homepage.html` and `default.html` templates, the following conventions apply.

### Extends and Loading libraries

An example `homepage.html` should start like this:

    {% load theme_tags %}
    {% load nav_tags %}
    {% load story_tags %}
    {% load base_tags %}
    
    {% theme_extends 'base.html' %}

Each library loaded at the top will make more template tags available for use. You should only include tag libraries that are used on the page, as loading unused libraries can increase page load times.

The `theme_tags` library is **required** as it allows us to extend the `base.html` template with the `theme_extends` tag. This is a bit different than other Django apps. This is done this way in Tendenci to allow for theme previewing.

The load for `base_tags` is not required, but is almost always used, so it should be included.

The load for `nav_tags` and `story_tags` are optional, but are used frequently.

### Available blocks

The following blocks are available to be used. You are free to make up other blocks, but these blocks are specifically referenced in the `base.html` template. These blocks do not apply to overridden templates or to included templates like `header.html` and `footer.html`.

Blocks are listed below in the order they typically appear in for a template.

`{% block title %}` - Loads into the `<title>` element in the document.

`{% block meta_keywords %}` - Loads into the content attribute of the `<meta name="keywords" />` element in the document.

`{% block meta_description %}` - Loads into the content attribute of the `<meta name="description" />` element in the document.

`{% block extra_head %}` - Contains meta information, CSS, and JS that needs to be included in the `<head>` element of the document. The only JS that should be included here is that for html5shim or tracking code other than Google Analytics.

`{% block body_ids %}` - This pulls in as the id attribute to the `<body>` element. While it is singular, it is recommended to only use one value. A typical value for this is 'home'.

`{% block body_classes %}` - Loads in to the class attribute of the `body` element.

`{% block html_body %}` - **Required**. Loads in the main `<body>` element of the document. This is where all of the HTML code should be included.

`{% block content_classes %}` - **Default.html only**. This block should be placed inside the class of the main content area. This is used on full-width pages like `/events/month/` or `/dashboard/` to ensure the width is overridden.

`{% block content %}` - **Default.html only**. This block will be populated with the content from Tendenci, like a page, article, or job. This block should be included, but empty.

`{% block sidebar %}` - **Default.html only**. This block should be wrapped around any sidebar content that is not intended to be displayed on wide pages like `/events/month/` or `/dashboard/`. Any content within this block will be removed from the page for those wide pages.

`{% block jquery_script %}` - **Rarely used**. This block is available to override Tendenci's default version of jQuery, 1.7.2. If this is used, be sure that the jQuery file is included in the theme and not referenced from a CDN.

`{% block extra_body %}` - Loads on at the end of the document just before `</body>`. JS files for rotators, sliders, or other functionality should be included here. **Note** jQuery 1.7.2 is already included by Tendenci and should not be added here. If you require a different version (most don't), please use the `{% block jquery_script %}` block.

### Referencing Theme media files

Within the templates, when referencing files in the `media` directory, you will need to prepend the path with `{{ THEME_URL }}`. For example, to pull in the default stylesheet, the following link would be included in the `extra_head` block:

     <link rel="stylesheet" href="{{ THEME_URL }}media/css/style.css" type="text/css"/>
     
For other files like javascript files, please follow this same pattern, like the example below:

    <script src="{{ THEME_URL }}media/js/jquery.cycle.all.min.js" type="text/javascript"></script>

### Common Template tags

These template tags are commonly used, and come from either the `base_tags` or the `theme_tags` library.

`theme_include 'header.html'` - This tag is used to include other templates. In this example, it's including a `header.html` file, but this could be replaced with other included templates like `footer.html`, `sidebar.html`, or another template used in the theme.

`{% image_url story.image size=954x386 crop=true quality=90 %}` - This tag is used to create a resized version of an image. The first argument, `story.image`, should be a `File` object. The other arguments include the size, option to crop or constrain, and the quaility.

## HTML and Class Name Conventions

Here are some conventions for designing a Tendenci theme. The code samples shown below are grouped by which template they are typically found in, but some designs may not apply to these rules.

### Homepage.html

#### Libraries

First, we start with our loaded tag libraries:

    {% load theme_tags %}
    {% load nav_tags %}
    {% load story_tags %}
    {% load base_tags %}
    
    <!-- Extends Tendenci Base Structure
    ================================================== -->
    {% theme_extends 'base.html' %}

Notice that we have a comment regarding the extends tag. We will use more of these comments in this style to aid developers that may be also working on our template.

#### SEO Meta    

Next, we define the SEO options for our homepage:

    {% block title %}Our Great Site for Tendenci Themes and Designs{% endblock %}
    {% block meta_description %}Our site specializes in Tendenci Theme Designs, Custom Theme Designs, and helping developers build their own custom Tendenci theme designs.{% endblock %}
    {% block meta_keywords %}Tendenci themes, tendenci designs, tendenci template help, tendenci theme standards, {{ SITE_GLOBAL_SITEPRIMARYKEYWORDS }}{% endblock %}

Notice that we included a setting in our `meta_keywords` block. The `{{ SITE_GLOBAL_SITEPRIMARYKEYWORDS }}` contains the primary keywords from the database setting. This setting, along with many others, is available in our template using the name of the setting from the database.

#### extra_body block

Next, we have `{% block extra_head %}` which includes our main stylesheet, our html5 shim, and some other meta defaults.

    {% block extra_head %}
    <!-- Mobile Specific Metas
    ================================================== -->
      <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
      <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    
    <!-- Favicons
    ================================================== -->
      <link rel="shortcut icon" href="{{ THEME_URL }}media/images/favicon.ico">
      <link rel="apple-touch-icon" href="{{ THEME_URL }}media/images/apple-touch-icon.png">
    
      <!-- CSS
    ================================================== -->
      <link rel="stylesheet" href="{{ THEME_URL }}media/css/styles.css" type="text/css"/>
    
    <!-- IE Specific Compatibility
    ================================================== -->
      <!--[if lt IE 9]>
      <script src="//html5shiv.googlecode.com/svn/trunk/html5.js"></script>
      <![endif]-->
      <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
      <![endif]-->
      <!--[if lt IE 9]>   
      <script src="http://css3-mediaqueries-js.googlecode.com/svn/trunk/css3-mediaqueries.js"></script>
      <![endif]-->
      
    {% endblock extra_head %}

Again, we have comments to indicate certain areas of the code. Note that the only javascript included so far is the html5 shiv and shims used for IE support.

#### Body ids and classes

Tendenci gives two tags to allow you to populate the `id` and `class` of the `<body>` element. This can be useful when needing to get more specific when identifying elements in CSS for things on included templates like the header or footer.

    {% block body_ids %}home{% endblock body_ids %}
    {% block body_classes %}home{% endblock body_classes %}

The convention is to use `home` on `homepage.html` and `sub` on `default.html`.

#### html_body block and includes

Next is `{% block html_body %}`, which includes the bulk of our html for the homepage.

    <!-- Primary Page Layout
    ================================================== -->
    {% block html_body %}
    <div class="wrapper">
    
      <div class="header">
        {% theme_include "header.html" %}
      </div> <!-- /.header -->
      
      ...
      
      <div class="footer">
        {% theme_include "footer.html" %}
      </div> <!-- /.footer -->
      
    </div> <!-- /.wrapper -->
    <!-- End Document
    ================================================== -->
    {% endblock html_body %}
  
The middle will be filled with whatever html is necessary for our homepage. Notice a few particular things.

- All of our elements are nested with two (2) spaces
- When we close elements, we add a comment indicating the class of the element that is being closed, like `<!-- /.header -->`
- We have similar comments around our block tags.
- We have our block name in our `{% endblock %}` tag. This is not required, but strongly recommended when there is lots of content between the start and end of the tag.
- We are using the `theme_include` tag to bring in our header and footer templates. The names of these templates are wrapped with double quotes like `"header.html"`.

#### extra_body tag

In this example, we are using jQuery cycle to rotate our stories. The stories are wrapped in `<div id="stories">`, which is used by our javascript.

    {% block extra_body %}
        <script src="{{ THEME_URL }}media/js/jquery.cycle.all.min.js" type="text/javascript"></script>

        <script type="text/javascript">
        $(document).ready(function() {
            $("#stories").cycle({
                timeout: 8000,
                speed: 2000,
                pager: '#stories-pager',
                pagerEvent: 'mouseover'
            });
        });
        </script>
    {% endblock %}

Notice, we did NOT include jQuery, because Tendenci already includes it for us. We only needed to include the additional library.

When starting our jQuery code, we load jQuery with the `$` to use the function. All of our code is inside `$(document).ready(function() {` to ensure that it does not run before all of our content has loaded.

Notice here, we did not include the name of our block in the `{% endblock %}` tag because we don't have very much content.

### Default.html

This is the interior page template, and it is very similar to the homepage.html template, with a few exceptions in the 'html_body' block.

#### Libraries

See the content for `homepage.html` and adjust for any extra libraries that are needed.

#### SEO Meta

Because this template is used for multiple pages, we do NOT include any of the SEO meta blocks in `default.html`.

#### extra_body block

See the content for `homepage.html` and adjust if any changes are made. This may require removing some stylesheets or elements that are only used on the homepage (like rotator styles).

#### Body ids and classes

See the content for `homepage.html` and change `home` to `sub`.

#### html_body block and includes

This section differs from `homepage.html` enough that all of it's code is below.

    <!-- Primary Page Layout
    ================================================== -->
    {% block html_body %}
    <div class="wrapper">
    
      <div class="header">
        {% theme_include "header.html" %}
      </div> <!-- /.header -->
      
      <div class="main-content {% block content_classes %}{% endblock %}">
        {% block content %}{% endblock %}
      </div> <!-- /.main-content -->
      
      {% block sidebar %}
        <div class="sidebar">
          {% theme_include "sidebar.html" %}
        </div> <!-- /.sidebar -->
      {% endblock sidebar %}
      
      <div class="footer">
        {% theme_include "footer.html" %}
      </div> <!-- /.footer -->
      
    </div> <!-- /.wrapper -->
    <!-- End Document
    ================================================== -->
    {% endblock html_body %}
  
Notice the middle is filled in, where on `homepage.html` it was abbreviated. That has been replaced with a `<div>` for the main content which includes the `content_classes` block.

Below that, we have the sidebar, which is inside the `sidebar` block, and which also includes it's content from the `sidebar.html` template.

The rest of the template, like the parts for the header and footer, remain the same as the `homepage.html` template.

#### extra_body block

Often, this block is not included on `default.html`, because it is typically used for rotator features only found on the homepage.

If it is used because of javascript features on interior pages (like sliders in the sidebar or footer), be sure to remove any javascript that is only for the homepage (like cycle for rotators).


### Header.html

The html shown for this header is only an example for a very simple design. More detailed designs may need additional changes.

The header template does not include any `{% block %}` tags since it is included in other templates.

#### Libraries

Because the `header.html` template is included on other templates, we don't need to extend another template with `theme_extends`.

We DO need to load any libraries we use. The most common ones used in headers are shown below

    {% load nav_tags %}

If stories or boxes are included, please load those tags as well.

#### Content

    <header>
      <div class="logo">
        <img src="{{ THEME_URL }}media/images/logo.png" />
      </div> <!-- /.logo -->
      
      <div class="search">
        <form method="post" action="/search/" class="search-form">
          <input name="q" id="q" type="text" placeholder="Search" />
          <input type="submit" name="Go" value="GO" />
        </form>
      </div> <!-- /.search -->

      <div id="main-nav">
        {% nav 1 %}
      </div><!-- /#main-nav -->
    </header>

We have wrapped everything in a `<header>` tag, and then have different elements for the logo, search form, and the main nav.

The main navigation is included using `{% nav 1 %}`, which pulls in the html needed from the nav editor for Nav with the ID #1. The nav ids can be seen at `/navs/` on your site.


### Footer.html and Sidebar.html

Please see the description above for `header.html`, as all of these templates are included and work in a similar way.

## Full Theme Examples

There is a repository on github at [https://github.com/tendenci/tendenci-themes](https://github.com/tendenci/tendenci-themes) that includes several (15+) fully-built Tendenci themes. These themes can be used as examples to find different ways of loading dynamic content into your Tendenci theme.

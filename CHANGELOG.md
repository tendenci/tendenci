### 11.0.6 [2018-11-06]

* Fixed migration error due to missing a dependency
* Resolved the js error about origin doesn't match for Youtube videos
* Excluded __pycache__ directory from theme editor
* Fixed a couple of issues in form entries exports
* Users can now see profile options menu
* Fixed an error in education edit

### 11.0.5 [2018-10-25]

* Reduced decimal places for Invoice adjustments to 2. The adjustment with four decimal places is unnecessary for currency.
* Added a setting "Discount Amount for Auto Renewal" to memberships so that admin can specify the discount amount for members who opt in auto renewal on memberships join/renew.
* Added the ability to exclude a self-add group from a membership application.
* Updated invoice void process:
  1. Voided invoices show balance of 0
  2. Provided an option to cancel the corresponding event registration if any.
  3. Provided an option to delete the corresponding membership(s) if any.
  4. On invoice view, voided invoices are marked with a VOIDED stamp
  5. Updated invoice view and search accordingly
* Updated the canonical urls to be absolute urls.
* Updated sql_explorer to version 1.1.2, removed the out-dated templates pulled under explorer_extensions, and fixed the issue about schema not showing.
* Added the social media fields to user profile.
* Updated profiles add/edit templates to be responsive.
* Showed primary registrant in registrant search when no guest info entered.
* Fixed for invoice.variance to store accumulated adjustments instead of the last adjustment.
* Fixed event registration stats display
* Fixed TypeError for multi-files upload
* Other small fixes


### 11.0.4 [2018-10-08]

* Default no-reply address for newsletter sender
* Changed PYBB_DEFAULT_TIME_ZONE to match with the default TIME_ZONE setting
* Fixed get_url_patterns for addons
* Fixed an error in recurring payments for authnet
* Fixed some issues in projects
* Applied urlencode filter for tags
* Fixed some issues in global search
* Updated requirements.txt to require django >=1.11.16 because there are vulnerabilities in Django 1.11.x before 1.11.15
* Other fixes


### 11.0.3 [2018-09-21]

* Rotated images if needed when displaying original images.
* Updated invoice pdf to allow invoice owners to download.
* Fixed unicode issues for paypal 

### 11.0.2 [2018-09-07]

* Fixes for memberships multiple online payment methods
* Fixed a url in notification/user_welcome/full.html
* bugfix: '>' not supported between instances of 'NoneType' and 'int'

### 11.0.1 [2018-09-06]

* SECURITY: Patched a secutiry hole in payments that could potentially expose user data.
* Fixed dashboard redirect so that the "Profile Redirect" setting doesn't have to be set to blank for "Group dashboard Redirect" to work.
* Other minor fixes


### 11.0 [2018-08-31]

#### Compatibility
* Support Python 3.6 or newer. Python 2.7 is no longer supported. 
* Requires Django 1.11. Django 1.8 is no longer supported.
* T7 sites can be smoothly migrated from the previous version (7.5.x) if you follow the guide in docs/source/upgrade/upgrade-to-tendenci11.txt.
 

#### Special Thanks
* A quick shout-out to Paul Donohue @PaulSD, who has made tremendous contributions on converting Tendenci to Python 3 and making it compatible with Django 1.11. Thanks Paul!
* And to those who have been working diligently to constantly improve Tendenci, we appreciate you!  


### 7.5.1 [2018-06-26]

* Fixed an error on education search.
* Updated CM top menu.
* Updated EducationForm to populate the data on membership renewal and prevent existing education records from being wipped out on renewal if no education fields are presented,
* Documented discount setup and testing. (Thanks to Karl Goetz @goetzk).


### 7.5.0 [2018-06-18]

* Updated the list_corporate_memberships template tag to have the option to filter by corporate membership type.
* Fixed the issue about new templates not showing in droplist on page add/edit.
* Made embed_form to fail silently to not break entire site.
* Added the active only checkbox to the corporate memberships search.
* Added the setting "Users Can Add Resumes" so that admin can turn off/on users ability to add resumes.
* Updated Members Roster Report for printer.
* Added stripe connect (readonly currently).
* Fixed payment method options not showing all on event registration.
* Excluded admin_only payment method for non-admin.
* Fixed the js error for directories and jobs add/edit caused by RelatedObjectLookups.js.
* Fixed KeyError no id in JobPricingForm.
* Added the option on_delete=models.SET_NULL to avoid data loss for lots of OneToOneField and ForeignKey fields.
* Allow reps to renew their corporate memberships.
* Applied orientation to retain intended position for photos.
* Fixed queryset filter for "disapprove" admin action. 
* Fixed spacing in "From:" header causing spamminess for notifications.
* Checked if email domain is valid before sending email.
* Lots of other minor fixes.

### 7.4.4 [2018-02-28]

* Integrated Google reCaptcha. To turn on Google reCaptcha, visit the help file: [How to Use Google reCaptcha on Tendenci Site](https://www.tendenci.com/help-files/how-use-google-recaptcha-tendenci-site/)
* Added a members search page.
* Added the setting "Member Searching User" to define whether a member can search registered site users.
* Fixed some issues in corp memberships import
* Added new members to the default group specified by the setting "defaultusergroup".
* Corrected some labeling issues in news.
* More fixes

### 7.4.3 [2018-02-09]

* Updated admin index page to have smaller font and numbered list
* Removed campaign monitor from admin backend (it was disabled)
* Made slug field unique for the staff model
* Added the search by group functionality to the profiles search
* Added functionality to email invoices for admin
* Fixed the issue about the total balance of the registrants export caculated on spreadsheet is inaccureate
* More fixes

### 7.4.2 [2018-01-19]

* Added a code of conduct.
* Included company name to the user list display on group view.
* Added the option to order by release date for videos.
* Added theme editor link to the admin section of top menu.
* Fixed the global search to prevent memberships from being searched by unauthorized users.
* Changed tendenci logo for emails.
* Fixed the invoice error due to the blank string feeded to the "permalink" decorator in get_discount_url.
* Fixed the release date initial for article add.
* Avoid rebuilding thumbnails if they exist to improve the photos performance.
* Added the option to specify an API key and URL signing secret for Google maps.
* More bugfixes

### 7.4.1 [2017-12-04]

* Membership auto renew (Works with Stripe and Authorize.net)
* Renamed filename to replace dots, underscores, and spaces with dashes for file uploader
* Replaced the CIM forms addresses with the new “Accept Customer” forms (Authorize.net issued an EOF for the old “Hosted CIM” forms)
* Fixed search term not stick in tinymce file browser
* Fixes for flake8 warnings
* More bug fixes

### 7.4.0 [2017-11-15]

#### Notable changes:

1. New top menu (for both admin and logged in users)
2. Newsletters format update and clone feature
3. Reports format update (including invoices, memberships, ..)
4. Events views - Added sub menu for month view, week view, day view
5. Separated join approval and renewal approval for membership notices
6. Wysiwyg editor - Enabled the image title input field in the image dialog. Added class dropdown to the tinymce link dialog box
7. Updated the directories categories to make it easy manage
8. Added drag-drop functionality to the testimonials
9. Added memberships overview report
10. Added a link on Profile page to view past events.
11. More minor changes


#### Fixes:

1. (Security) Disabled GZipMiddleware to prevent BREACH attacks
2. (Security) Prevent fraudulent simultaneous reuse of PayPal transactions
3. Resolved the issue regarding manage.py hangs when caching is enabled. Re-enabled the cache for site settings.
4. Resolved the subprocess venv issue.
5. Fixed exports for directories, jobs, resumes, pages.
6. Fixed "Most Viewed Files" report.
7. More fixes

Special thanks to @PaulSD for lots of fixes and update!

### 7.3.12 [2017-10-09]

* Added horizontal rule (hr) to tinymce editor
* Added class dropdown to the tinymce link dialog box

### 7.3.11 [2017-10-09]

* Made jobs categories and subcagegories easy to manage
* Set default to now() for date or datetime fields in custom forms
* Fixed encoding error on paypal_thankyou_processing
* Fixed handling of disabled registration forms
* Ensured correct venv is used for subprocesses
* Registered forums to apps_list
* Updated invoices search for custom forms
* Multiple more bugfixes

### 7.3.9 [2017-09-06]

* Replaced allowed_to_view_orginal with has_perm for photos
* Fixed multiple membership types validation error
* Excluded admin_only payment method for non-admin
* Truncated the date list to start with current year for newsletters
* Some updates on corp memberships
* Added tendenci footer to email notifications
* Added category and subcategory drop downs to articles search
* Added reference_number field to /py/
* Made videos sort draggable
* Sending notification only at the time the corp cap is reached
* Made category and video_type editable for the videos list
* More bugfixes

### 7.3.8 [2017-08-16]

**Improvements**

* Added logo field to corporate memberships
* News can be viewed by release year and linked on news search
* Removed stub test files so the real tests stand out
* Updated corporate membership summary report with more graphs


**Fixes**

* Bugfix on event registration with custom form
* Set start_dt and end_dt to current year for newsletter events
* Fixed AttributeError: 'Options' object has no attribute 'module_name'
* Fixed TypeError: Related Field got invalid lookup: icontains
* Bugfixes on form entries export, jobs add/edit, renewed_members and profiles


### 7.3.3 [2017-07-21]

* Fixed NoReverseMatch on email delete
* Bugfix Attribute error on group members export
* Resolved the 'form' name conflicts - the name conflicts occurs when a custom form is embedded in a template header
* Caught DjangoUnicodeDecodeError exception on helpdesk
* Fix UnicodeEncodeError on jobs add/edit


### 7.3.2 [2017-07-13]

**Improvements**

* Video thumbnails will be pulled from youtube API for youtube videos if needed (when embedly is not available), so no need to upload thumbnails for youtube videos.
* Updated version for the dependencies django-simple-captcha (to 0.5.5) and Pillow (to 4.2.1).
* Added categories to the admin backend.

**Fixes**

* Fixed the members graph on dashboard
* Removed the extra space from CAPTCHA image.


### 7.3.1 [2017-07-03]

**Improvements**

* A new site setting is added for embed.ly API key to allow your site to sign up for your own embed.ly API Key.
* Made video categories draggable.
* Handled html emails for Helpdesk tickets - stripped html from email body and added to ticket description.

**Fixes**

* Fixed raw HTML showing up in renewal alert.
* Removed the deprecated sets module.
* Fixed UnicodeDecodeError on jobs add_message.
* Disabled the correct button during event registration
* Updated the way of handling unsubscribe url to prevent it from being broken.


### 7.3.0 [2017-06-07]

* Upgraded tinymce from 4.3.8 to 4.6.3 which fixed the issue about image linking not working.
* Made the number of members on profiles consists with the one on memberships reports.


### 7.2.81 [2017-06-05]

* Bugfix and updated for email edit
* Moved "generated by Tendenci" email footer to a template include.
* Payment/Invoice bugfixes

### 7.2.80 [2017-06-01]

* Bugfix AttributeError
* Allow user to view/edit invoice if bill_to_email matches
* Include guid in Pay Online button on Invoices
* Removed deprecated PayPal redirect_cmd parameter



### 7.0.0 [2015-06-09]

- Support Django 1.8

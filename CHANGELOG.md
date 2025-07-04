### 15.3.5 [2025-7-3]

* Created the admin backend for newsletters to make newsletters searchable.
* Updated donation add page. 1) Changed the format to be consistent with the rest of the forms. 2) Mixed the "donate to entity" and "preset amount" to be a list of radio select. 3) Added the option to charge tax based on user's region. 4) Added a setting to specify required fields. 5) And more.
* Updated /py/.
* Updated the format for corp membership add/edit.
* Added the corp membership type name to corp export.
* Included corp_profile_name to memberships export.
* Granted staff access to report links at top menu. (Thanks to @bernd-wechner)
* Assigned the owner for the cloned newsletters.
* Added the setting usersrequiredfields to specify extra required fields on profiles add/edit.
* Converted span elements with datetime attributes to time elements for event's day view. (Thanks to @tristanjl)
* Added committees settings for root url and labels.
* Added registration_open filter for event_list. (Thanks to @tristanjl)
* Added 20 more UD fields to corp membership application.
* Added the label field to directories pricing.
* Updated newsletter generator to visually toggle group and members only.
* Resolved 2 issues in membership auto renewal: If auto renewal fails, 1) no member number will be assigned to the profile, 2) no multiple membership entries will be created.
* Updated invoice view to show bill_to_company for corp memberships.
* Fixed an issue for file add to not block with blockUI until required fields are filled out.
* Other small fixes.


### 15.3.4 [2025-5-7]

* Updated the frontend add/edit to have wysiwyg editor for the custom forms.
* Updated corp export to include some invoice fields (subtotal, total, tax, balance).
* Added the perm "Can publish form" for custom forms.
* Added 10 more UD fields to corp membership application.
* Fixed some issues in projects documents upload.
* Converted setup.py to pyproject.toml
* Other minor fixes.

### 15.3.3 [2025-3-10]

* Updated assets purchase to handle free purchase.
* Forum subscription update. Notifications for new topics will be sent to all forum subscribers instead of those opted to the "only new topics".
* Added the check that payment mode is online (#1343). When expired membership has submitted renewal, then we trigger online payment only if payment is online payment. (Thanks to @AnttiMJohansson)
* Phone number formatting now uses Phonenumberslite library (#1340). (Thanks to @rob-hills)
* Added a management command "prune_event_log_records" to prune event logs if the setting KEEP_EVENT_LOG_FOR_DAYS is set to a number greater than 0. (Thanks to @rob-hills)
* Set the button label to "Join Webinar" if the Zoom event is a webinar and not a regular meeting. (Thanks to @bje-)
* Added a method to include raw files within the static directory.  (#1342) (Thanks to @rockinrobstar)
* Displayed the renew link for admin to renew a membership that is out of renewal period.
* Updated invoice title for form entries.
* Added an option to show online payment pre page.
* Updated bluevolt API connections.
* Added an option to allow payment credits to be carried over on renewal for both memberships and corporate memberships.
* Included "member type" field to the renewed members report.
* Fixed an issue about "taxes not included in refunds".
* Resolved an issue about registration edit link not showing when event registration passed the cancellation date.
* Other minor fixes.


### 15.3.2 [2025-2-24]

* Allowed event addons to be added without options specified.
* Updated "marks as paid" so that if an admin marks an invoice as paid, the associated object (membership, corporate membership, etc) will be automatically updated if needed.
* Updated the ICS export to include ongoing events.
* Updated corp export to make region field a name instead of ID.
* Updated event registration to handle inactive or anonymous users register user-only events.
* Fixed a format issue for directories on /search/.
* Fixed the issue about tax is calculated before discount being applied for memberships.
* Fixed the issue regarding members not being able to find member-only content in search.
* Changed "Submit" to "Complete Registration" on register_child_events.html (Thanks to b-davies24).
* Other minor fixes.


### 15.3.1 [2025-1-2]

* **SECURITY**: Fixed a potential XSS vulnerability in forums.
* Added the filter "Event Type" to event financial report.
* Added the export option to /admin/auth/user/.
* Added header image field to study groups.
* Added 2 tokens, rep_last_name and rep_salutation, to corp notices
* Added the “unrelease” option to the action dropdown for Registrant Credits.
* Updated event registration to redirect non-members to 403 if the only pricing is for member-only.
* Updated memberships to avoid duplicate memberships submissions on renewal.
* Resolved tinymce menu inoperable in fullscreen.
* Other minor updates and fixes.


### 15.3 [2024-11-21]

* Updated add/edit corp reps to remove the auto-complete with a list of possible email addresses.
* Added a setting "REDIRECT_403_TO_LOGIN" to allow your site to turn off the "403 to login redirection" for anonymous users. If this setting is turned off (default on), whenever a permission is required, anonymous users will see the 403 page immediately instead of being redirected to the login page. 
* Updated directory expiration date after directory edit. (Thanks to @rob-hills)
* Added a check to avoid the "disable_template_cache" from crashing the site. (Thanks to @bernd-wechner)
* Upgraded zoom to the latest SDK (v3.9.0). 
* Added an unsubscribe button to group view if user is allowed to remove themselves from the group.
* Resolved some issues in invoice view.
* Removed the interactive field from profile edit as the regular users should not change their interactive status.
* Made some updates for jobs and directories, including a setting to specify the required fields on add/edit.
* Added an option to set up notices for corp memberships in different regions.
* Added the tax option to directory pricing.
* Users can now assign category/subcategory to their directory listings.
* Added mime types for .xlsx, .docx and .pptx to the allowed list.
* Allowed the corp reps view their invoices.
* Updated forum notifications.
* Fixed invoice logo not showing on invoice PDF.
* Fixed tax being applied before discount for event registration.
* Many other updates and fixes.


### 15.2.1 [2024-8-27]

* Corporate memberships update: 1) Added an option to require admin approval upon joining (Corp members) but allow them to renew upon payment without having to go through admin approval. 2) Added a setting to allow individual who submits a corp membership application to automatically become member under the org upon approval.
* Fixed a TypeError for membership approve method called from recurring memberships.


### 15.2 [2024-8-24]

* New feature: option to use region for tax rate. It can be turned on with the setting "Use Regions for Tax Rate" at /settings/module/invoices/#id_taxrateuseregions. The header and footer of an invoice can be customized for a specific region.
* Added the option to auto apply chapter memberships upon membership approval.
* Added the option to allow event select multiple groups with one primary group. If multiple groups are selected, the primary group is used for financial reports.
* Updated forums view to raise HttpResponseForbidden to avoid a blank page when an authenticated user gets permission denied. (Thanks to @CraigeHales)
* Suppressed captcha for logged users on embeded forms. (Thanks to @CraigeHales)
* Updated digital check-in process so that the user scanning in registrants doesn't have to select a session and click "confirm". (Thanks to @ssimmons42)
* Added 'Powered by Stripe' logo to Stripe payments page. (Thanks to @b-davies24) 
* Updated events credits report - Added a filter by credit name and added export feature to the report.
* Corrected the roster report link on child event view to point to child event roster.
* Updated 403 and 404 pages to include error codes. (Thanks to @b-davies24)
* Added the filter by "Last Login" at users admin backend. 
* Made "Registration email reply to" a required field on events add/edit.
* Added the description field to event Addon.
* Added Event Place admin facility to allow sorting and mergeing event places. (Thanks to @rob-hills)
* Updated jobs and directories add/edit to not show list type dropdown if no premium listing.
* Other minor updates and fixes.


### 15.1 [2024-5-22]

* Upgraded font awesome from v4 to v6.
* Removed UnicodeWriter from exports for invoices, articles, chapters and events to significantly reduce the size of the exported files.
* Added donation allocation to corporate memberships renewal, and have the option to create a separate invoice for donation.
* Projects update: added frontend add/edit pages.
* Resolved some issues in tinymce 6.8.
* Other minor updates and fixes.


### 15.0 [2024-3-30]
 
* **Breaking Changes: Requires Django 4.2 LTS**. Django 3.2 LTS is not supported. For migrating T14 sites to T15, please follow the guide in https://tendenci.readthedocs.io/en/latest/upgrade/upgrade-to-tendenci.html.
* Implemented json-ld as structured data on event view for events to show in Google events search.
* Added bulk checkout feature on events roster report.
* Adjusted the format for event certifications.
* Fixed an error on skillset edit due to openstreetmap search requires user agent specified.
* Fixed an issue regarding photo size too large for photos batch edit.
* Fixed some broken links in tendenci default fixtures.
* Fixed a format issue for profile top menu. 
* Removed "\r" from ical description to prevent it from showing in google calendar.
* Other minor fixes.


### 14.8.2 [2024-2-21]

* Added Region filter option to member_quick_list report. (Thanks to @rob-hills)
* Updated addons on event registration:  1) Removed the checkbox in front of the addons. 2) Added help text in the addons section. 3) Cleared qty after being processed.
* Added an itemized list on payonline for event registration.
* Added the ability to sync credits on event credits edit. 
* Updated event reminder edit to include QR code in reminder test.
* Added an option to block renewal for individual members under corp /settings/module/memberships/#id_orgmembercanrenew.
* linked "Join Zoom Meeting" in registration confirmation email and updated launching zoom meeting to redirect to event view if meeting is not ready or already over.  
* Fixed a format issue on directories search 
* iCal update: 1) Resolved an issue that made "Add to calendar" act as “meeting update” in outlook. 2) Ensured lines of text are less than 75 octets https://icalendar.org/iCalendar-RFC-5545/3-1-content-lines.html
* Fixed pages search not working for tags
* Fixed an issue for event view that the RSVP button doesn't show for non-member users, even though they are in the selected group(s) for a pricing.
* Fixed an issue that the default selected addons can't be deleted.
* Selected addons now show on registration review page. 
* Resolved code scanning alerts
* Other miscellaneous fixes

### 14.8.1 [2023-12-24]

* New feature: Event assets purchase for the past events.
* Updated registration for the nested events to allow users to register for less dates.
* Fixed the issue about creator and owner not being able to search their own news items.
* Fixed a bug in invoices search that didn't take account into blank email address.
* Resolved an issue about forms not being redirected to payment.
* Other small fixes. 
 

### 14.8 [2023-12-10]

**New Features and Improvements**

* ** Event Cancellation and Refund:** 1) Added the ability to charge a cancellation fee when an event registration is cancelled.  2) Added the refund capability to either automatically or manually refund when users cancel their registrations. Currently this feature is only available with Stripe payment. To enable it, you can turn on the setting "Allow refunds" https://www.example.com/settings/module/events/#id_allow_refunds
* **Nested Events:** Nested events functionality allows you to host events with sessions or sub-events. To enable the nested events, turn on the setting "Enable Nested Events" https://www.example.com/settings/module/events/#id_nested_events.
* Added an option to not allow users who already registered to register an event again https://www.example.com/settings/module/events/#id_canregisteragain
* More new features in events: Attendants can earn credits and be granted with certificates. QR code and badges can be used for digital check-in. Zoom integration, etc... 
* Added the "Register A User" functionality for admin to easily search and register a user for an event.
* Updated Stripe Connect onboarding process https://tendenci.readthedocs.io/en/latest/topic-guides/payments.html#how-to-use-stripe-connect.
* Updated custom forms to allow users to specify the quantity of the item(s) purchased. 

**Backward Incompatible**

* Dropped Python 3.6 support. 

**More updates and bugfixes**


### 14.5.1 [2023-07-04]

* Fixed an issue about reps could be removed from dues reps and member reps groups when they're removed from a corp but still associated with other corps.
* Merged HL integration.
 

### 14.5 [2023-06-27]

* **New Feature:** Added Trainings module that allows a Tendenci site to offer certificate programs to users. https://tendenci.readthedocs.io/en/latest/topic-guides/trainings.html
* Besides the standard accounts, express accounts can also be added to stripe connect in Tendenci. For info how to set up stripe connect, please see https://tendenci.readthedocs.io/en/latest/topic-guides/payments.html#how-to-use-stripe-connect. 
* Members list is now viewable to users who have the membership view permission. Previously, it requires change permission. However, the export and email abilities in the members list still require change permission.
* Allowed users with news view and change perms to view un-released news so that they can edit. https://github.com/tendenci/tendenci/issues/1176
* Resolved the issue about guest info is required on event registration form when only first registrant is required.
* Other small fixes.


### 14.4 [2023-05-16]

* Updated Authorize.Net payment gateway integration. 1) Switched SIM to Accept Hosted beause SIM is deprecated https://developer.authorize.net/api/upgrade_guide.html. 2) Removed xml.etree.ElementTree that was used by CIM in recurring payments. The xml.etree.ElementTree module is no longer supported. https://docs.python.org/3/library/xml.etree.elementtree.html
* Integrated stripe connect to payments. https://tendenci.readthedocs.io/en/latest/topic-guides/payments.html#how-to-use-stripe-connect
* Updated forums to not send notifications to those listed in the emailblocks.
* Set the default value for enforce_direct_mail_flag to True on newsletter add. 
* Other small fixes.


### 14.3.6 [2023-03-28]

* Chapter leaders are now not allowed to renew their chapter memberships that are not in renewal period.
* Included membership_type field to chapter memberships export. 
* Updated memberships search to display links for files uploaded via ud fields.
* Fixed a bug that causes files uploaded via ud fields not being saved. 
* More bug fixes.


### 14.3.5 [2023-03-10]

* Added an option for admins to associate a donation to a user, if not already.
* Fixed a NoneType error for event registration (when admin override is checked but override price is not specified).


### 14.3.4 [2023-03-09]

* Committee officers can access their associated groups.
* Admin can register events after an event is full.
* Corporate memberships search can filter by membership types.
* Corp profiles can specify their branches.
* Added an option for members to send broadcast emails to corp reps.
* Included county field on memberships and group members exports.
* Added the command "send_chapter_membership_notices" to the nightly run commands list.
* Added account_id field to corp profiles and user profiles.
* Added an option to allow chapter or committee leaders to adjust invoices for their events by the site setting "Chapter or Committee Leaders Can Adjust Registration Invoices for Their Events".
* Resolved some issues for front-end form edit.
* Fixed the issue about uploading logos for a corp profile resulting in duplicate logos.
* Resolved the issue about missing permission checks on form submissions.
* More bug fixes.


### 14.3.3 [2022-12-21]

* Added an option for corporate members to show their products on their corp profiles.
* Activities logged in eventlogs previously only work for IPv4, it now supports IPv6 as well.
* Made the notifitions go to chapter contacts (specified in the contact email field) when a new member joins a chapter.
* Avoided a redundant admin notification from being sent for auto-approved membership types. 
* Included more basic user info to chapter memberships exports. 
* Bugfixes: Resolved an AttributeError at event delete. Fixed a photo upload issue. Resolved some issues for form entry edit. 


### 14.3.2 [2022-11-19]

* Bumped gevent to 22.10.2 to resolve an installation error for tendenci on Ubuntu 22.04 LTS.
* Bumped pillow from 9.2.0 to 9.3.0.
* Added help_text for tax info (if available) on membership application forms.
* Fixed the tax display on invoices to reduce the number of digits after the decimal point from 4 to 2.
* Made thumbnail not required for youtu.be videos.
* More bugfixes.


### 14.3.1 [2022-11-01]

* Forums update: added an option to subscribe a forum for users. 
* Made Youtube shorts URLs work for videos.
* Granted chapter officers the view and change permissions for their own newsletter group. 
* Renamed the setting "Google Analytics UA Number" to "Google Analytics Tracking (Measurement) ID".
* Refactored file upload process for forms to resolve the possible issue about file not being saved, also sanitized file name.
* Resolved recaptcha v3 timeout issue.
* Fixed an error on logo saving when non-logged in users applying for corporate memberships.
* Some update on Ukrainian translations (Thanks @silpol).
* More bugfixes.


### 14.3 [2022-08-26]

**New Features and Improvements**
* Integrated Django Two-Factor Authentication. To enable the two-factor authentication, please see https://tendenci.readthedocs.io/en/latest/topic-guides/two-factor-auth.html.
* Added form entry editing capabilities (Thanks @bernd-wechner).
* Added chapter state coordinating agencies.
* Listed the chapter memberships (if exists) on user profile.
* Added the option to allow non-interactive user to activate their accounts if self registration is enabled.
* Added the option to NOT override interactive/non-interactive status for existing users on users import.
* Added the confirmation step for newsletters unsubscription. 
* Updated the groups section on user profiles to indicate if newsletter is unsubscribed, and if so, link to re-subscribe.
* Added the setting "Member Can View Corporate Membership Roster" (default to False).
* Changed the default value from True to False for the setting "Minimal Event Add Enabled". 

**Fixes**
* Fixed an issue in Forums about time at front end not matching with the admin back end. 
* More bugfixes.


### 14.2 [2022-07-11]

* **Backward Incompatible**: Due to some issues in the pylibmc, we've switched the memcached client from pylibmc https://pypi.org/project/pylibmc/ to pymemcache https://pypi.org/project/pymemcache/. This change will NOT affect your production sites. However, if you don't have memcached installed in your local environment, please specify the cache backend to `CACHES['default']['BACKEND'] = 'django.core.cache.backends.dummy.DummyCach'` or to something you have set up.

### 14.1.1 [2022-07-07]

* Updated the installation guide
* Chapter leaders can now view/edit their member profiles.
* Added some basic user info to chapter memberships export.
* Added search feature to the admin form entries list.
* Included application/csv to the whitelist mime types.
* Added the template tag list_memberships.
* Resolved the blurry images issue on Photo albums list.
* Added category to photos albums and individual photos
* Added the option to display members on the associated directory.
* Added the option to use state dropdown for the state field on membership and profile forms.
* Appended the non-us choice to the state dropdown.
* Fixed articles category links not working. 
* Fixed the issue about the “paragraph" filed type not showing TextArea field on membership forms
* More bugfixes.


### 14.1 [2022-04-18]

* New feature: Newsletters scheduling https://tendenci.readthedocs.io/en/latest/topic-guides/newsletters.html#newsletters-scheduling.
* Bumped Pillow from 9.0.0 to 9.1.0.
* Added an option to disable gravatar. The setting is at /settings/module/users/#id_disablegravatar.
* Form entry lists have a configurable summary (Thanks @bernd-wechner).
* Allow users with News permissions to see the corresponding edit and delete links (Thanks @bernd-wechner).
* Added the option to have a header image on articles search. The header image can be specified with the setting /settings/module/articles/#id_headerimage.
* Added a template tag "get_categories_for_model".
* Made some performance improvement for newsletters when being sent to members.
* Refactored form entries export to avoid timeout.
* Added an example code for the list_photo_sets template tag.
* Added captcha on password reset form.
* Some bugfixes.


### 14.0.4 [2022-02-04]

* Added the option to use Google reCaptcha v3. This help file includes the info on how to set up reCaptcha v3 for your site https://www.tendenci.com/help-files/how-use-google-recaptcha-tendenci-site/.
* Fixed the issue regarding page edit not recording event logs.
* Avoided the possible error: "check_number" violates not-null constraint.


### 14.0.3 [2022-01-17]

* Upgraded Pytz version to fix dependency conflict resulting from Celery upgrade to version 5.2.3. (Thanks @rob-hills)
* Fixed a format issue for events speakers list.
* Fixed a potential IntegrityError on membership applications where username is not included on the form.
* Avoided a potential DataError for jobs add due to slug is not presented.  


### 14.0.2 [2022-01-13]

* **SECURITY**: Bumped Pillow from 8.3.2 to 9.0.0.
* Bumped celery from 4.4.7 to 5.2.3 .
* Added a new email to members feature on members search.
* Excluded irrelevant tables (event_logs, sessions...) from database dump.
* Changed to company name (instead of site display name) in "Invoice For" for the invoice PDF. 
* Resolved some RemovedInDjango40Warning.


### 14.0.1 [2022-01-02]

* **SECURITY**: Avoided the page /memberships/referer-url/ being redirected to external sites.
* Disallowed /memberships/referer-url/ in robots_public.txt to avoid bots from crawling /memberships/referer-url/.
* Resolved an installation error with python 3.8 due to Embedly package not compatible with python 3.8.
* Added a new feature "email to chapter members" to chapter memberships.
* Added front-end videos add/edit pages.
* Other minor fixes. 


### 14.0 [2021-12-15]
 
* **Requires Django 3.2 LTS**. Django 2.2 LTS is not supported.
* T12 sites can be smoothly migrated to T14. For migration, please follow the guide in docs/source/upgrade/upgrade-to-tendenci14.txt.
* Added memberships search/filter that can search fields based on each app. It also includes the export feature. Linked at /admin/memberships/membershipapp/.
* Added chapter memberships functionality.
* Made time_zone and language fields available to the membership application forms.
* Added the county field to profiles view, edit and search.
* Disabled captcha for authenticated users for custom forms (Thanks @bernd-wechner).
* Used logged in users email as fallback for form submissions (Thanks @bernd-wechner).
* Fixed a format issue for membership application.
* Fiexed an issue where recurring events not being updated on event edit
* Refactored export Active Memberships Report /memberships/reports/active_members/ to resolve timeout issue due to large volume of memberships.
* Other minor fixes.


### 12.5.11 [2021-09-24]

* Added the clone feature for chapters.
* Added two site settings for chapters: "Chapter admin notice recipients" (`/settings/module/chapters/#id_chapterrecipients`) and "Chapter Default Featured Image URL" (`/settings/module/chapters/#id_defaultimage`).
* Added the option (`/settings/module/user_groups/#id_permrequiredingd`) to show groups (in the group dropdown) that user has the change perm (instead of view perm) for news, photos, events and files.
* Added the group field to videos.
* Staff users who has the group edit perm can now see group members and email members.
* Added a section on user profiles to display their chapter, if any.
* Added "Export All Members" to Membership export. (Thanks @bernd-wechner)
* Improved expiry widget layout a little on membership types edit. (Thanks @bernd-wechner)
* Added some simple help to two options, allow_renewal and renewal on membership types. (Thanks @bernd-wechner)
* Added virtual and national fields to events.
* The state field on events add/edit can now opt for a state dropdown instead of an input field (`/settings/module/events/#id_stateusedropdown`). And the state dropdown can be further narrowed to have US states only (`/settings/site/global/#id_usstatesonly`).
* Tightened the permission for user groups.
* Fixed an issue that an unhandled exception in a view returns a status 200. It returns 500 status code now. (Thanks @BenSturmfels)
* Resolved a migration warning.


### 12.5.10 [2021-09-08]

* Bumped Pillow to 8.3.2


### 12.5.9 [2021-09-07]

* Resolved the issue about recap file is significantly larger than the original import file for memberships and profiles import.
* Changed the character limit to match the max_length of username for memberships import.
* Added the county field to the events search.
* Avoided duplicate directory listings being created when a membership application is submitted again.
* Fixed the missing captcha on embed forms
* Removed impersonated_user from code.


### 12.5.8 [2021-08-11]

* Added the option (setting "Hide Free Membership/Corporate Membership Invoices") to not display free membership and corp membership invoices on invoices search.
* Updated username field for the self register form.
* Changed max_length to 150 for the address field in directory to match with the address field in profiles.
* Prevented soft deleted corp profiles from showing on user profile.
* Moved the captcha field to the bottom of the custom forms.
* Included the invoice link (if exists) to form entry.
* Added the `county` field to event place and chapters.
* Validated emails beore being sent.
* Events full details are pulled with tasty API.

### 12.5.7 [2021-07-20]

* Events search respects the group's `show_for_events` checkbox.
* The group dropdown on newsletters add now shows a list of groups that the user has change perm (instead of view perm).
* Chapter officers are granted the view and change perms for their own group so that their group would show up in the group dropdown when they add a newsletter.
* Fixed an AttributeError on chapters add
* Updated tendenci_default_memberships.json to make renew_link clickable.
* Resolved the region display issue on user profile.
* Fixed some issues for api_tasty.


### 12.5.6 [2021-07-01]

* Bumped Pillow from 8.2.0 to 8.3.0.
* Added a grace period column to the Corporate Memberships Overview.
* The text "you have already registered" shows on event registration if user has already registered the event.
* Bug fixes and patch rollups.

### 12.5.5 [2021-06-23]

* Bugfix a FieldError at /donations/. 

### 12.5.4 [2021-06-22]

* Added the export feature to the invoices search.
* Added the ability to use entities for donation allocation for better reporting
* Invoice "mark as paid" can now enter a check number.
* Added a setting "Show Radio Buttons to the Event Pricing List" /settings/module/events/#id_rbonpricinglist to turn on/off Radio Buttons for the Event Pricing List.
* Removed bullets in front of the checkboxes or radio buttons on event registration.
* Fixed the date picker on invoices search.


### 12.5.3 [2021-06-11]

* **SECURITY**: Avoided a potential race condition when assigning permissions for the uploaded files.
* Added expiration date to the officers for chapters and committees.
* Added state and region fields to chapters.
* The entity and group are now automatically created (instead of manually assigned) on chapters add.
* Added radio buttons to the event pricing list.
* Restored back the /reports/ link.
* Videos list page shows thumbnail for youtube videos if no images specified. 
* Fixed a TypeError in the discounts.
* Fixed an error on updating index for recurring_payments.


### 12.5.2 [2021-06-02]

* **SECURITY**: Bumped Django to 2.2.24. https://docs.djangoproject.com/en/3.2/releases/2.2.24/
* Bumped Pillow from 8.1.2 to 8.2.0
* Bumped django-ses from 1.0.3 to 2.0.0
* Updated django-sql-explorer from 1.1.3 to 2.1.2
* Updated the "Request to Associate" for the affiliates.
* Removed the old invoicing link /reports/ from top menu and redirected it to the invoices report overview.
* Fixed "Error App label is required.. Model name is required." when an image in the sponsors field is being uploaded for committees and chapters.
* Updated docs to add the support for ubuntu 20.04 LTS and remove the support for ubuntu 16.04 LTS.
* Fixed "Required field has no asterisk" (issue #1014).
* Made slug field unique for chapters and committees to avoid the MultipleObjectsReturned error.
* Resolved the issue on soft deleting users from the front end.
* Resolved the issue regarding invoice logo not showing on PDF. 
* Fixed an InvalidOperation error for discounts.
* Fixed a TypeError on event registration when admin override is selected but override price is not entered.
* Fixed the issue about not being able to add officers to studygroups.


### 12.5.1 [2021-05-07]

* **SECURITY**: Bumped Django to 2.2.22. https://docs.djangoproject.com/en/3.2/releases/2.2.22/
* **New feature**: Added profile photo upload. Now users don't have to go to gravatar.com to upload their profile photos. If they don't have their profile photos uploaded, their gravatars will still be used if available.
* Added "Revenue & Key Metrics by Tendenci" to the top menu under Reports (Thanks Edna).
* Added an option to specify a reply to email address for event registration confirmation emails
* Updated affiliates to set initial for the listing to connect, and display warning messages if no listings are available to connect.
* Added email field to the officers for committees and chapters.
* Fixed some nav issues for event log summary.
* Updated default memberships fixture to capitalize the first character of company.
* Fixed the green “Pay Invoice” button not showing on invoices view


### 12.4.13 [2021-04-22]

* **SECURITY**: Upgraded jQuery from 3.4.1 to 3.6.0 (There is a XSS vulnerability in the version < 3.5.0 https://blog.jquery.com/2020/04/10/jquery-3-5-0-released/)
* Moved the industry field from memberships to profiles.
* Users can view a list of their own directories.
* Added filters to ListNode (Thanks @theox26)
* Added newsletter recipients on "Ready to Send" confirmation page 
* Fixed a potential IntegrityError on user groups add.
* Fixed a TypeError on tickets search.
* Fixed a NoReverseMatch error in the photos view.


### 12.4.12 [2021-04-07]

* Bumped Django to 2.2.20.
* Added a link to chapters under the community tab. 
* Added an "Add Event" link to the Apps menu. 
* Fixed an AttributeError for forums post deletion.
* Updated invoice reports overview to display default date range and to handle invoices without object type.
* Updated translation for pt_BR (Thanks @farribeiro)


### 12.4.10 [2021-03-31]

* Showed the link to invoice reports overview for superuser only (Hided from non-superuser).

### 12.4.9 [2021-03-31]

* Added an invoice reports overview.
* Fixed photo upload crash with GPS info.
* Resolved the issue regarding free corp memberships that are not required approval should be approved automatically.
* Fixed a issue for event location summary formatting. 


### 12.4.8 [2021-03-23]

* **SECURITY**: Bumped Pillow from 8.1.0 to 8.1.2 https://pillow.readthedocs.io/en/stable/releasenotes/8.1.1.html https://pillow.readthedocs.io/en/stable/releasenotes/8.1.2.html
* **SECURITY**: Tightened security check for the password change page.
* Added a warning message on theme editor to indicate site reload is needed if template caching is on. 
* Ordering fix for helpfiles FAQ (Thanks @bernd-wechner)
* Removed the word "test" from default fixtures
* Extended max_length for user_display field on corp reps add/edit 
* Updated the description for the setting "Create User on Form Submissions" and forms default fixtures.
* Membership view improvements on members search (Thanks @bernd-wechner)
* Resolved an error RelatedObjectDoesNotExist in helpdesk
* Avoided a bad escape in forms


### 12.4.7 [2021-03-10]

* Adjusted the order of fields for event location section on events add/edit
* Updated the help text of some fields for custom forms.
* Added an option (/settings/module/users/#id_showindustry) to show industry on profiles search and view.
* Added the industry field to resumes.
* Fixed an issue about tinymce fullscreen not working properly on event organizer, location and speaker
* Fixed some issues in events edit when changes applied to all recurring events in series.


### 12.4.6 [2021-03-03]

* Fixed a KeyError for resumes add at admin backend 
* Adjusted video description on videos search to resolve a layout issue.
* The associated recurrent payments, if any, now shows on user profiles.
* Avoided users with recurrent payments being deleted 
* Tracked errors with logging for the management command `make_recurring_payment_transactions`.
* Removed wp_importer and wp_exporter 
* Fixed an AttributeError in newsletters. 


### 12.4.5 [2021-03-01]

* Added affiliations functionality in directories.
* Fixed an issue about data is passed via get not post for the paypal thankyou page.

### 12.4.4 [2021-02-24]

* Removed the `urlize` filter from the template events/view.html that is pulled down to the sites.
* Made `name` to be the default category selection (Thanks @lgm527).
* Changed both imageMaxWidth and imageMaxHeight to 2400 (was 1200 as the default) for image upload in wysiwyg editor.
* Added django-admin-rangefilter. 
* Added an option to directories search to display search results without search (Thanks @lgm527).
* Removed `urlize` filter from forms/form_sent.html
* Fixed a js issue about not being able to add officers to chapters and committees.


### 12.4.3 [2021-02-09]

* Updated user profile to show corporation(s) a user is a representative of. 
* Added Apply Date and Renewal Date to options for When to Send on the corporate memberships member notice. 
* Fixed some issues for redirects. 


### 12.4.2 [2021-02-05]

Removed the `urllize` filter from the description of event speakers, organizer and sponsors, because it is not needed for those fields with wysiwyg editor.


### 12.4.1 [2021-02-04]

* Removed "delete" option and added "inactivate" to the Action dropdown for navs to avoid being accidentally deleted.
* Added settings for study groups
* Added the help text for the directory Name field to clearly show this is the public name of the company, not the name of the person filling it out.
* Allowed users who have approve permission to view and edit admin-only fields as the designated approvers need to be able to view and edit these fields.
* Added required attribute for radio field type if needed
* Updated FormControlWidgetMixin to exclude multiplehiddeninput and hiddeninput.
* Updated admin view for the payments
* Django_ses.SESBackend conditional added to newletter relay function (Thanks @robbierobs)
* Updated django to 2.2.18
* Updated Pillow to 8.1.8
* Updated django-storages to 1.11.1
* Updated xhtml2pdf to 0.2.5
* Fixed an IntegrityError on membership type add when a name exists already. Updated the clean method for some forms as well to ensure it is loaded from super call to avoid missing validation from super class.
* Fixed upload not working for photos with metadata
* Fixed some format issues for payment view page
* Fixed an KeyError on events pricing edit


### 12.4 [2021-01-12]

* Added the chapters module
* Removed the "exact match" from profiles search and updated search form format.
* Created the template tag list_jobs_categories. 
* Added title, location and skills fields to jobs search.
* Added sender_display and reply_to to email to pending members. 
* Added canonical url to /news/, /articles/ and /events/. 
* Updated dashboard to show the last three Tendenci blog posts. 
* Added tokens to email sent via groups and newsletters.
* Added the option to have pending and/or active reps groups based on corp membership types.
* Updated Help files: 1) Set to pending for help files added by regular user. 2) Added email notification if added by non-superuser. 3) Fixed top menu for add/edit pages (was showing Articles instead of Help Files).
* Restricted corp profile link on directory view to owner and admins only
* Enabled user to edit directory they are member of (Thanks @yehuda-elementryx)
* Fixed category and subcategory for directories meta title and description 
* Made email fail mode configurable (Thanks @bernd-wechner)
* Removed directory creator from metadata (Thanks @robbierobs and @evanspaeder)
* Allowed superuser or reps or users with view_corpprofile perms to view their corp profile
* Resolved timing out for email to pending members 
* Updated boto3 version to 1.16.43 
* Removed unnecessary duplication in forms menu (Thanks @bernd-wechner)
* Made the officers table headings bold by default for committees. (Thanks @bernd-wechner)
* Added the default fixture for industries
* Fixed search not working for committees and chapters 
* Fixed the issue about default not working in custom forms for boolean field
* Fixed a bug for users with userid 0 (Thanks @bernd-wechner)
* Updated the select boxes on member add for user groups (Thanks @bernd-wechner)
* Updated profiles search to support searching for members NOT in any groups (Thanks @bernd-wechner)
* Fixed header on group detail page (Thanks @bernd-wechner)
* Added Membership Types to the Community menu (Thanks @bernd-wechner)
* Support for timeless dates on membership cards (Thanks @bernd-wechner)
* Added Members to Apps/Organization menu (Thanks @bernd-wechner)
* Added membership type to member cards (Thanks @bernd-wechner)
* Fixed unrestricted deserialization for helpdesk
* Fixed members search showing Users menu instead of Membership menu.
* Updated the description of the Primary Keywords setting 
* Updated email to pending members to allow for segmenting based on membership types.
* Allowed users with directories change permissions to view pending directories.
* Allowed users with profiles change permissions to access users search and similar users list.
* Extended truncated summary and body for directories/marketplace search results (Thanks @robbierobs)
* Fixed some issues in recurring payment for authorizenet.
* Changed h1 tags to h3 tags for news headline on news search page.
* Updated recurring payment details page. 
* Fixed import username limit (Thanks @evanspaeder)
* Fixed some issues for event minimal_add 
* Resolved permission bits not being saved for membership apps
* Fixed a bug in forms module


### 12.3.3 [2020-11-17]

* Updated similar users list to be case-insensitive.
* Resolved the issue about speaker photo overlaps the text.
* Updated django version to 2.2.17.
* Updated the notifications email view to superuser only.
* Fixed value too long for NoticeEmail.
* Fixed missing file perms re-assignment on directories approal.


### 12.3.2 [2020-10-29]

* **SECURITY**: Updated exports to prevent potential CSV injection in the exported CSV files.
* **SECURITY**: Added the missing FileValidator to restrict files to images for case studies edit only at admin backend.

### 12.3.1 [2020-10-28]

* **SECURITY**: Fixed a potential HTML Injection and XSS vulnerability in a few area of admin backend.
* Fixed a ValueError for directory add.
 

### 12.3 [2020-10-26]

* Added the functionality to allow admin to email pending members or pending corp members.  
* Enabled multiple categories and sub-categories for directories.
* Added the sort ability to directory categories with drag-and-drop.
* Added the approve_corpmembership perm so that users can be assigned to approve corporate memberships without granting them the superuser privilege.
* Added a setting to turn on/off private (obscure) url access without login required.
* Added the require_approval field to the corporate membership type with 2 choices "for ALL" and "for Non-Paid Only" (default to "for Non-Paid Only"). Currently, the non-paid corporate memberships are set to pending, while the paid ones are approved automatically. This allows admin to set to require approval for all applicants.
* Updated email to directory owners (If a directory is created from memberships, the owner is the associated member. If a directory is created from corporate memberships, the owners are the representatives.) upon approval.
* Allowed the owners of corp memberships to edit their own pending applications.
* Updated the base class for oauth2_client backend.
* updated gevent version to the latest 20.9.0.
* updated format for corp approve.
* Updated the edit link for memberships admin list - linked "Edit" to the frontend edit page, and "ID" to the backend edit.
* Avoided creating default entity and group in the initial_migrate.
* Added a simple command to show settings (Thanks @bernd-wechner).
* Added a FAQs view to the help_files app (Thanks @bernd-wechner).
* Tidied layout of the template themes/t7-tendenci2020/templates/base.html (Thanks @bernd-wechner).
* Fixed Pay Online button not showing.
* Fixed field lengths in accounts forms (Thanks @evanspaeder)
* Fixed empty app list /base/apps-list/.
* Fixed broken list_tables command.
* Resolved an error in firstdatae4.
* Fixed an error in the command settings_build_init_json (Thanks @bernd-wechner).
* Fixed x_type initial issue for the firstdatae4.
* Removed the extra "\" in email subject when [full name] is used in subject template for custom forms.

### 12.2.8 [2020-09-30]

* Updated format for corporate membership view to avoid long labels being cut off

### 12.2.7 [2020-09-30]

* Fixed corp_membership encoding detection (Thanks @evanspaeder)
* Added an edit button for admin on pending corp membership for easy editing
* Fixed a potential encoding issue on memberships import
* Updated memberships and corporate membership imports to use detected encoding instead of hard-coded utf-8
* Updated the corporate membership add to redirect anonymous user to login instead of add_pre if "public can view" is unchecked
* Formated the pricing end date to also show year  #889
* Resolved corporate membership types not being imported along with their associated corporate memberships 

### 12.2.6 [2020-09-28]

* Fixed default value not working for boolean field on corporate membership application.
* Fixed profile/add form username limits #894 (Thanks @evanspaeder)
* Fixed duplicate slug error on membership app clone #893
* Fixed newsletters are not searchable in Event Logs #892
* Applied strip_control_chars to feed for articles and news to resolve an UnserializableContentError: Control characters are not supported in XML 1.0.


### 12.2.5 [2020-09-25]

* Fixed an error in corporate memberships import (Thanks @evanspaeder)
* Added missing phone2 field to corp profile (The phone2 field exists on app, but was missing in CorpProfile model).

### 12.2.3 [2020-09-23]

* Fixed links on the full settings list not being linked to the specific settings.
* Avoided using the same ud fields for cloned membership applications because same UD fields can't be re-used across applications.
* Resolved a permission issue on deleting unneeded membership applications (and corporate membership applications).

### 12.2.2 [2020-09-17]

* Directory owners can view and edit their directories, but only admin can publish directories that are created with memberships and corporate memberships.
* Updated memberships to have email address take precedence over first name and last name when assigning a username.
* Added the link to directory listing, if any, on user profile and at the bottom of corp member profile.
* Added the link to corp member profile, if any, on directory listing. 
* Updated post-install-checklist.txt for newsletters settings.
* Updated boto3 to 1.12.8 and django-ses to 1.0.3.
* Fixed the issue about pricing 0.00 not working for custom forms.
* Resolved the issue regarding custom forms showing page's nav menu instead of form's when a custom template is selected.

### 12.2.1 [2020-09-08]

* Adjusted (or corrected) the files path for files uploaded in wysiwyg editor. For example, files uploaded in pages will go to files/page/, files uploaded in boxes will go to files/box...
* Files access of custom forms is restricted only to those who have the forms change permission rather than view permission.

### 12.2 [2020-09-05]

**New Features and Improvements**

* An oauth2 client for tendenci that you can use to set up single sign-on (SSO)
* Added an option to add a directory for memberships on join approval
* Directory owner or creator can publish their directories if they are created with their memberships or corporate memberships
* If directory for memberships or corporate memberships is enabled, admin can add a directory and associate it with an existing membership or corp membership.
* Included `directory_url` and `directory_edit_url` tags for membership and corporate membership notices so that they can be added in the approval notifications to link members to their directory view and edit pages
* Added the support for LibreOffice/OpenOffice Document upload (Thanks evanspaeder)

**Fixes**

* Updated django version to 2.2.16 (Django 2.2.16 fixes two security issues and two data loss bugs in 2.2.15)
* Fixed max_length for creator_username and owner_username fields that does not match with username's (Thanks evanspaeder)
* Fixed a DataError in event registration
* Fixed the issue about selected groups being de-selected on event pricing edit

### 12.1.1 [2020-08-21]

* Adjusted MEMCACHE_MAX_KEY_LENGTH 247 to resolve the InvalidCacheKey error
* Added the exclude_expired option to the list_corporate_memberships 

### 12.1 [2020-08-14]

* New feature: Donation option on corporate memberships renewal
* Changed the updated date to event date for events list generated for newsletters
* Fixed an InvalidCacheKey error
* Resolved the issue regarding multiple tags cannot be searched in files search
* Updated the memberships list at admin backend to include the view and profile columns
* Updated group slug pattern to fix a potential NoReverseMatch error when a forward slash (/) is included in the slug. 

### 12.0.14 [2020-08-09]

* Applied FileValidator to file fields for membership and corp membership forms

### 12.0.13 [2020-08-07]

* Updated Django version to 2.2.15
* Added the approved/denied info in the admin area on membership details page
* Included entity_type to the entities list_display
* Made entity a OneToOneField in directory
* Added an option to add a directory for corporate memberships on join
* Added the missing parent_entity field to corp app 1
* Fixed an error in email send due to None Reply-To
* Fixed a AttributeError: 'NoneType' object has no attribute 'email' 
* Made file perms match with the setting "Member Protection"

### 12.0.12 [2020-07-30]

* Updated django-ses to 1.0.2
* Updated Pillow to 7.2.0
* Updated django version to 2.2.14
* added top nav options for photo set
* Updated photo set details view to make photos span the full width of the page
* Made regions sortable
* Added region field to directories
* Added two settings, FILE_UPLOAD_DIRECTORY_PERMISSIONS and FILE_UPLOAD_PERMISSIONS, for file upload permissions
* Included edit link and app id to the memberships fields list
* Removed bad test data (test and testing) from corp membership default fixture
* Avoided corp memberships approval email being sent twice
* Updated tendenci_default_boxes.json
* Resolved the issue on corporate membership add when the company name entered exists but soft deleted
* Fixed top menu unreadable in mobile 
* Fixed tag not working in files search
* Fixed the issue about the enabled zip code field not displaying in the event registrant edit
* Updaed and fixed some issues for iCalendar
* Resolved the issue about event attendees not being linked if "Display Attendees" is turned on
* Added missing trailing slash for events attendees page
* Fixed articles not being created from cloned newsletters
* Fixed OSError: cannot write mode RGBA as JPEG
* Fixed an import error in model_report for python3.8 (Thanks @theox26 and Aaron Oxenrider)


### 12.0.11 [2020-06-24]

* Added tendenci console script for nice install command  (Thanks @iokiwi)
* Restrict non-admins from sending newsletters to certain groups 
* Avoided a potential KeyError on memberships export
* Updated T12 upgrade guide

### 12.0.10 [2020-06-17]

* Resolved the issue about Password requirements text incorrectly populating on account register (Thanks @rob-hills) 
* Tightened password requirements - 1) Ensured a default password regex is used if not set up in site settings. 2) Added password requirements check on profile add and change password forms.
* Fixed KeyError: 'MODULE_PAGES_LABEL_PLURAL'
* Fixed a KeyError on membership change page at admin backend.

### 12.0.9 [2020-06-12]

* Updated Django version to 2.2.13
* Enforced No Email flag on newsletter send. - If selected, newsletter send will not send emails to members that have opted for Don't Send Email in their profile.
* Added an option for non-renewing members to stop receiving notices. - Some sites set up several reminder notices to members as they approach expiration. Sometimes a member will respond upon receipt of the first notice that they are not interested in renewing. This option allows admin to turn off notices for them.
* Fixed a DataError value too long for first_name on account register
* Avoided a AttributeError in memberships export
* Added eventlog on forms confirmation email send

### 12.0.8 [2020-06-01]

* Resolved the issue about redirects not working for forums
* Fixed a ResourceWarning: unclosed file for command precache_photo
* Tweaked the submit button for /photos/set/edit/ 
* Fixed a FieldError for /memberships/reports/expired_members/
* Users with permissions can now access forms link in the top nav
* Reverted back plain text email to html (to make email format consistent for logged in and non-logged users)
* Fixed an issue about user dropdown not working for committee edit at admin backend


### 12.0.7 [2020-05-13]

* Updated nav editor to allow tel: links
* Cleaned up RegConfPricingBaseFormSet
* Fixed a ValueError for PricingForm
* Fixed an AttributeError for stripe payment
* Resolved some issues for forms so that users with permissions can add/edit forms at front end instead of admin backend


### 12.0.6 [2020-05-10]

* Resolved the issue about tinymce menu not showing on fullscreen for events add/edit
* Fixed an error in exports regarding 'Options' object has no attribute 'virtual_fields'
* Fixed the issue about newsletters automatically include events content
* Fixed a ValueError at studygroups edit 
* Fixed a KeyError at membership export


### 12.0.5 [2020-05-01]

* Removed .doc and .xls from the allowed file upload extensions for the security reason. Besides the general threats, determining the mime type for the .doc and .xls files (generated by old MS Word and MS Excel) requires feeding the entire file content due to their format not complying with the standard. 
* Resolved an issue "No module named 'django.forms.extras'" for memberships, corporate memberships and custom forms that could occur when 'django.forms.extras...' is still stored in the field_type but   django.forms.extras has been moved to django.forms.widgets since Django 1.9.

### 12.0.4 [2020-04-29]

* Resolved some issues in memberships edit
* Fixed a TypeError at clone event
* Resolved the issue about creator not being assigned on pages and articles add 

### 12.0.3 [2020-04-21]

* Updated membership backend UX
* Meta title update for articles and news - removed the 100 characters limit and the silly "..."
* Removed the themes dropdown on theme editor 
* Fixed a IllegalMonthError at events month view (ex: /events/2020/0/)
* Fixed a AttributeError at photos zip
* Avoided a DataError at get_email command 
* Fixed a TypeError for forms

### 12.0.2 [2020-04-09]

* Updated django version to 2.2.12
* Some bugfixes for profiles and groups permission edit
* Fixed a TypeError when payment is not fully set up
* Updated format for the groups perms edit 
* Appended ?rel=0 to avoid unrelated youtube videos being displayed when video finishes

### 12.0.1 [2020-04-03]

* Renamed tendenci2018 theme to tendenci2020 
* Replaced http:// with https:// for urls
* Corrected batchsize option for process_unindexed command
* Fixed a DataError for event_logs
* Avoided value exceeding FIELD_MAX_LENGTH for forms
* Resolved some migration warnings

### 12.0 [2020-03-30]
 
* Requires Django 2.2. Django 1.11 is no longer supported.
* T11 sites can be smoothly migrated to T12. For migration, please follow the guide in docs/source/upgrade/upgrade-to-tendenci12.txt.

### 11.4.10 [2020-02-10]

* Included region field to profiles export
* Added a setting "Pre-populate Corporate Profile to Individual Membership's Application" to allow you to turn on or off the behavior of pre-populating corporate profile to individual membership's application
* Removed anonymous user access to payments (Thanks @AdamBark)
* Updated dependencies (including django to 1.11.28) in requirements.txt
* Resolved some RemovedInDjango20Warning
* Fixed an AttributeError for list_corporate_memberships
* Fixed UnserializableContentError for /pages/feed/

### 11.4.9 [2020-01-26]

* Handled the case in event registrations when management forms are tampered maliciously 

### 11.4.8 [2020-01-25]

* Custom forms can now map more fields in profiles
* Allowed the allowfullscreen attribute for embeded Youtube vidoes
* Commented out the non-working historical event logs summary report
* Updated the content for some default fixtures
* Moved tendenci link from footer.html to credits.html
* Updated Pillow to the latest version 7.0.0
* Added verifydata() to avoid DataError for EventLog
* Assorted bugfixes

### 11.4.7 [2020-01-09]

* SECURITY: Prevent unauthorized use of renewal URLs (Thanks @PaulSD)
* Added the "member id", "join" and "last login" fields to the similar users list
* Fixed a bad escape error for forms
* Fixed a IntegrityError for users merge: insert or update on table "profiles_profile" violates foreign key constraint
* Fixed a TypeError for forums: argument cannot be of 'NoneType' type, must be of text type
* Avoided NoReverseMatch errors on tag detail
* Fixed a KeyError error 'start_dt' for events pricing edit

### 11.4.6 [2019-12-30]

* Fixed visibility of announcements in menu (Thanks @AdamBark)
* Resolved the issue about broken profiles images by using Gravatar's own default image for sites (in development) not having domains yet
* Updated form export to make the file names in csv to be consistent with the files downloaded

### 11.4.5 [2019-12-19]

* Removed the contribution.css link to avoid 404s
* Updated doc to avoid installation error about "No module named 'distutils.util'"
* Added an option to show update alert when a superuser logs in and Tendenci version is out date
* Added the ability to map more fields to profile for custom form
* Allowed Pages and Stories to appear in apps menu for non-superuser (Thanks @goetzk)
* Displayed status_detail for admin on file edit
* Added a warning message on redirects add/edit to indicate that site reload (restart) is needed to have changes to take effect.
* Updated the max_length of some fields for ProfileForm to not exceed their corresponding ones specified in Profile model to avoid the "value too long" error.
* Updated the default fixture to change folder names to lowercase for Directory and Staff folders. (And renamed the corresponding folders to their lowercase https://github.com/tendenci/tendenci-project-template/commit/229a508a087fc8b24d5a350c5d223e97ce7e0b96)
* Fixed a FieldError for boxes at admin backend
* Updated the update_tendenci command
* Fixed the issue regarding account registration allowing password and password (confirm) fields with different values
* Resolved some issues and broken links in getting-started fixture
* Resolved ResourceWarning: unclosed <socket.socket in get_latest_version
* Updated django version to 1.11.27 (released on Dec 18, 2019).
* Updated django-sql-explorer to the latest (1.1.3)


### 11.4.4 [2019-11-26]

* Allowed language option in tinymce
* Fixed the null character error in events month view and accounts login
* Removed problematic check on self.user (Thanks Karl Goetz @goetzk)
* Fixed an IntegrityError in donations


### 11.4.3 [2019-11-14]

* Fixed a UnicodeEncodeError in paypal
* Caught the FileNotFoundError in photos
* Fixed NoReverseMatch error for /memberships/referer-url/
* Aavoided value too long error for slug on directory add by non-superuser
* Removed control chars from rss feeds to avoid UnserializableContentError
* Fixed AttributeError for projects feed
* Fixed a TypeError on membership delete (from corporate roster)
* Added release date and stripped away tags like <html>, <head>, <body>... when an article was generated from a newsletter. 


### 11.4.2 [2019-10-08]

* Avoided duplicated base url in og:image tags.
* Refactored RemoveNullByteMiddleware.
* Fixed a typo in profiles/meta.html.
* Stripped control chars from staff feeds to avoid the UnserializableContentError.
* Replaced UnicodeWriter with the builtin csv for group members, users and memberships export to avoid Null chars being included in exported files. 
* Fixed a JavaScript error on dashboard when member info is not available. 

### 11.4.1 [2019-10-07]

* Updated membership delete to ensure member number is cleaned up from profile and user is removed from associated membership group. 
* Fixed invalid date/time error on jobs add/edit at admin backend
* Filtered out expired and not activated jobs from public jobs list.
* Included comments field on event registrants export.


### 11.4 [2019-10-02]

* Upgrade jQuery from 2.1.1 to 3.4.1 (latest)
***Important*: Back up your site first before running tendenci update! Any third party jQuery plugins you use that are not compatible with the latest version of jQuery will potentially break your site.** 
* Resolve the issue about django-admin-bootstrapped not compatible with Django 1.11
* Added none option to image_class_list for tinymce editor
* Added a setting to control whether or not to create user on form submission (default false)
**Note that: **  Even if this setting is set to false, a new user will still be created if payment is involved or "Subscribe to Group" functionality is selected. To make your site GDPR compliant, you can add a new checkbox field to your form to obtain user's consent.
* Other small fixes


### 11.3.1 [2019-08-21]

* Added education field to the staff module
* Added department and position dropdowns to staff search
* Removed Facebook like button
* Removed Google+ url from anywhere
* Blocked files with a comma or two consecutive dots in it
* Specified stripe api version
* Fixed fullpage plugin for newsletter edit

### 11.3 [2019-08-09]

* Set app info for stripe
* Added fullpage plugin to WYSIWYG editor for newsletters 

### 11.2.12 [2019-08-07]

* SECURITY: striped null byte to avoid null byte injection attack
* Fixed "masonry is not a function" js error for photos
* Resolved issue not being able to delete users who posted on forum 
* Prevented tickets from being cascade deleted with user deletion
* Allowed to specify both name and display name separated by a colon in the choices field
* Allowed to set back to the default field type for membership app fields
* Added make payment to financial section of tendenci top menu
* Commented files that are listed underneath content on event view
* Added pagination to videos list for performance reason
* Updated django version to 1.11.23


### 11.2.11 [2019-07-15]

* Added the group option on articles search
* Added the option to pull past events for list_events template tag
* Added the options 'file_cat_id' and 'file_sub_cat_name' to the list_files template tag
* Made some changes for files/search-results.html 
* Removed "t-files-title" unused class in files.css
* Changed the default sort order for entities and user groups in the admin backend to sort by id ascending
* Fixed format issue on profile view when membership is disabled
* Fixed TypeError at /events/reports/financial/
* Ensured absolute url for canonial url
* Fixed an error for invoices reports
* Fixed an issue for helpdesk when creating a ticket from emails sent from no-reply address
* Other small fixes


### 11.2.10 [2019-06-20]

* Fixed the meta title and description in articles/view.html
* Added grid view option for articles
* Moved meta to have it visible in the events
* Removed Google+ from social_media/icons.html


### 11.2.9 [2019-06-17]

* Update django version to 1.11.21 
* Fixed issue not being able to edit /admin/entities/entity/
* Specified the aspect ratio for the video_embed
* Fixed ValidationError on helpdesk query save
* Fixed signal "create_usersettings" not working in helpdesk
* Updated event money output
* Fixed KeyError for memberships app when the payment_method field was unchecked for some reason
* Removed the path arg to avoid unnecessary connections for invoices download
* Added gratuity feature to events


### 11.2.8 [2019-05-17]

* Security: upgraded bootstrap from 3.3.1 to 3.4.1 (There are xss vulnerabilities in version less than 3.4.1)
* Added social media fields to directories
* Included link to notice log if number of recipients > 50 on memberships notice recap to admin
* Added img-responsive class to the directory logo
* Added pagination to 404 reports for the performance reason
* Fixed boolean settings for forms
* Fixed KeyError at /admin/pages/page/
* Fixed error on indexing directories when activation_dt is not set
* Updated credits based on @goetzk feedback 

### 11.2.7 [2019-05-03]

* CRLF for calendar ics file
* Fixed TypeError in jobs search
* Fixed TypeError in directories search
* Made sure fields in videos search get validated to avoid illegal in the query strings

### 11.2.6 [2019-05-01]

* Fixed an error in PayPal IPN

### 11.2.5 [2019-04-30]

* Prevented superuser from being redirected to group dashboard on login
* Removed schipul.com from fixtures
* The auto renew checkbox on membership application is default to checked now
* Replaced the relative to absolute links on registrant email send

### 11.2.4 [2019-04-15]

* Indicated billing address in the profiles
* Fixed an error in news export
* Fixed an error in jobs search
* Fixed an error in fields edit for membership and corporate membership apps

### 11.2.3 [2019-04-05]

* Added "Export selected" actions (for both main and all fields) to memberships admin backend
* Made type required when adding/editing events
* Fixed databases dump not working
* Removed unnecessary ImageSitemap from sitemap.xml for the performance reason
* Fixed memberships details labels
* Fixed KeyError at /search/

### 11.2.2 [2019-03-22]

* Resolved the warning message on migrate to prevent users from being prompted to run 'manage.py makemigrations'

### 11.2.1 [2019-03-21]

* Adjusted event financial report to include discount code quantities
* Auto refresh the calendar view when the date in Events In field changes
* Included admin_notes to list_display
* Updated Pillow to the latest version 5.4.1
* Fixed ValueError in attachments for email_invoice
* Fixed error on logout from admin interface
* Fixed attribute error when loading forums fixtures

### 11.2 [2019-03-15]

* Added option to specify registration caps per pricing
* Added the export option to events financial report
* Replaced MD5 Hash with SHA-512 based hash utilizing Signature Key for authorize.net payment
* Improved the performance for /profiles/similar/ and fixed search not working
* Fixed profile url for officers on study groups detail page
* Fixed event tax not properly calculated
* Fixed IntegrityError on deleting user at /admin/auth/user/
* Fixed locations module
* Other small fixes

### 11.1.2 [2019-02-14]

* Added/Fixed pagination for photo sets list
* Added id and member_number, along with is_superuser and is_active, to UserAdmin
* Fixed missing {% endif %} in base.html
* Fixed save not working on page preview

### 11.1.1 [2019-02-12]

* Updated django version to 1.11.20 to patch a security issue in django 1.11.18
* Added a site setting for Google Tag Manager container ID
* Added sort and filter by category for Files admin backend
* Made staff indexable

### 11.1 [2019-02-07]

* Resumes update
	- Separated contact_name into first_name and last_name
	- Changed file name to be lastname-firstname.xxx if available
	- Updated search and view
	- Populated contact fields for non-superuser on resumes add
* Events update
	- Added the grid view option for event list (can be turned on/off via setting `/settings/module/events/#id_gridview_for_listview`)
	- Updated month view
	- Added notice for events to check for abandoned payments
* Made global search default to not return anything if user didn't enter anything in the search box
* Added event title field to the model report and fixed some js errors
* Updated all social media icons in profiles to dark gray
* Removed contributions, registrants, invoices, photos, profiles and memberships from index as those are not being used and can potentially slow down on search
* Removed multi-select option from groups for event add/edit
* Updated `set_setting` command to automatically update site domain when siteurl is changed
* Fixed boolean settings
* Fixed group not being preserved on news edit
* Fixed the issue about above-cap-ind-price not being sometimes on corp renewal
* Fixed some broken image links and format issues for edit_perms
* Resolved an permission issue for membership view
* Fixed an error in email attachments
* Other minor fixes

**NOTE:**

* The update for the search index requires index to be rebuilt. Please rebuild index with the command `python manage.py rebuild_index`.

### 11.0.8 [2019-01-07]

**Improvements**

* Event template functionality
* Added option to default the event Add-on to yes so the registrant has to purposefully opt-out
* Added option to include uploaded files on resumes export
* Add the sponsors field to committees and studygroups 
* The list_events template tag can now take comma separated multiple types 
* Updated the list_events tag to include 'priority' in order_by
* Made the event priority checkbox available to superusers only
* Updated the command to clean up old exports from db

**Fixes**

* Made the groups list to show the groups only in the selected date range on events monthly view
* Fixed an error on study-group edit due to inline formset
* Fixed group not preserving on Event edit 
* Fixed a javascript error in model-report

### 11.0.7 [2018-12-14]

**Improvements**

* Added date range to resumes export 
* Added sponsor to events 
* Added a new field "show_for_event" to the user groups, and used it to filter groups for the group dropdown on events add/edit 
* Added an option to filter by group on calendar view 
* Updated events export to show date range 
* Included the group field to events export 
* Updated events financial report 1) Added Group Name column 2) Added an option to sort by Group Name 3) Changed Filter button to say Filter by Date
* Added the form entries list view at admin backend 
* Added the date picker to events add/edit
* Updated jQuery File Upload to the latest version 9.28.0
* Updated Fine Uploader to the latest version 5.16.2

**Fixes**

* Fixed some issues, including the performance issue, in events financial
* Fixed several issues in model_report 
* Resolved some issues in /events/types/ 
* Fixed an error on adding a recurring event
* Updated the event admin list view to direct edit link to the proper edit view
* Corrected the profile link on education edit
* Fixed the requirements for making "make_recurring_payment_transactions" command to run
* Fixed an issue in stripe to ensure token is received before creating charge
* Fixed issue about exports (for jobs and resumes) missing main fields
* Avoided sender being entered as a non-email address on email edit
* Fixed an issue about search button not functioning 
* Fixed an error for committee edit in inlineformset 
* Changed regex pattern for youtube videos 
* Used the dateformat setting for forums

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

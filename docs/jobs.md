# Jobs

Jobs is a Tendenci 5 App for hosting Job postings. The postings can be added by administrators, users with permissions, or added by users and put into a pending queue. Admins and those users with permission can activate new job postings. Job postings can be set to require payment, and can be configured to expire after a set amount of time.

## Fields

The following fields are included on the jobs add and edit forms. Items with an * are required.

- title
- slug
- description
- list_type
- code
- location
- skills
- experience
- education
- level
- period
- is_agency
- percent_travel
- contact_method
- contact_company
- contact_name
- contact_address
- contact_address2
- contact_city
- contact_state
- contact\_zip\_code
- contact_country
- contact_phone
- contact_fax
- contact_email
- contact_website
- position\_reports\_to
- salary_from
- salary_to
- computer_skills
- requested_duration
- job_url
- tags

Administrator only
- pricing
- activation_dt
- post_dt
- expiration_dt
- start_dt
- syndicate
- design_notes
- meta


## Add/Edit/Delete

To add a job, go to (http://example.com/jobs/add/) to create a new job listing. Users on your site will be able to add job listings at that URL.

To edit a job listing, you will need to be logged in to your website. There are two places where you can edit your job listing:

1. Click the edit link that is shown below the job listings on the job search page at (http://example.com/jobs/search/).
2. Click the edit link at the bottom of a job listing when viewing that job.

Both links will take you to an edit screen where you can make changes to a job.

## Workflow

## Payments

## Notifications

## Settings

The following settings are available within the Jobs app:

- **Enabled** - specifies whether the Job app is used on the site. Default is True.
- **Job admin notice recipients** - a list of email addresses separated by commas that will receive [notifications](#notifications) listed above.
- **Job Payment Types** - a list of payment types separated by commas that will be available for [paid job listings](#payments).
- **Label** - the text used in menus and on the screen for the jobs app. This will **not** replace the word 'jobs' in the URLs.
- **Requires Payment** - determines whether job postings require a payment.

## Import Export

Import/Export is not currently available for the Jobs app.
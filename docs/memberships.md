Memberships are composed of the following areas:

- [Membership Type](#types)
- [Membership Forms/Applications](#apps)
- [Membership Application Entries](#entries)
- [Member Listing Pages](#listings)

### [Membership Types](types)

The first thing to be created is a Membership Type. This type includes the following fields and options:

- *Type Name
- *Price
- Admin Fee
- Notes
- Expiration Method (Never, Fixed, or Rolling with several options)
- Allow Renewals?
- Renew only?
- *Renewal Period Start
- *Renewal Period End
- *Expiration Grace Period
- Require Approval?
- Admin only?
- Status and Status Detail

An example of a Membership Type could be the following:

- **Name**: Gold Members
- **Price**: $100
- **Admin Fee**: $0
- **Expiration Method**: Fixed, expires on 12/31 of the year they signed up or renewed.
- **Allow Renewals?**: Yes
- **Renewal Period Start**: 45 days, meaning they can renew starting 11/16 of the current year.
- **Renewal Period End**: 31 days, meaning they can renew until 2/1 of the year after they originally signed up.
- **Expiration Grace Period**: 15 days, meaning they still get all of the member benefits until 1/16 if they have not yet renewed.
- **Require Approval?**: Yes, meaning an administrator must approve their application for membership.

To become a Gold Member, a person must fill out a membership application.

### [Membership Applications](apps)

Membership Applications are the gateways into a Membership. A potential member will fill out their information into the Application and depending on the Membership Type settings, the member will be put in a pending queue or automatically accepted as a member. For Administrators, the Membership Application offers a few options as well as a customizable form builder to make custom fields for potential members to fill out.

The Membership Application Administration has the following fields:

- *Name
- *Slug (for the form URL)
- Description (appears at the top of the application page)
- Confirmation Text (appears on the followup page after an application is filled out. Great for tracking code or followup tasks)
- Notes
- *Membership Types (option to select one or many membership types)
- *Payment Methods (supports custom offline methods and any online methods previously activated by a Developer)
- Use Captcha?
- Permissions block (standard on other T5 apps)
- Fields

The fields option is available once you have filled out the initial information and then click "Save and continue editing". The default fields are auto-populated. They are:

- *First Name
- *Last Name
- *Email
- *Membership Type
- *Payment Method

These can be re-labeled and re-ordered, but they cannot be removed from the form. Below the fields is a button to Add another field. When adding another field, you have the following field type options:

- Date
- Date/Time
- Text
- Paragraph text
- File Upload
- Checkbox
- Choose from a list
- Multi-select

Additionally, there are three field types that allow you to better organize your Membership Application. These fields are:

- Section Header
- Description
- Horizontal Rule

All of the different field types come with some of the options below:

- Required?
- Help Text
- Default Value
- CSS Class

Once you have entered in and reordered all of your fields, you can save your Membership Application. You can view your Membership Application at http://example.com/memberships/*slug*  where *slug* is what you entered on the Membership Application entry screen.

### [Membership Application Entires](entries)

Once you have created one or multiple Membership Types and have created at least one Membership Application, your site will be ready to accept Membership Application Entries. A Membership Application Entry is added whenever someone fills out your Membership Application.

As an administrator, you can view a full list of Membership Application Entries at http://example.com/memberships/entries with the option to search based on a specific membership type, membership application, or status (approved, disapproved, or pending). 

When viewing a pending membership application entry, you have the option to approve or disapprove that application entry. This option currently cannot be reversed, and would require an application to re-apply if they need to be approved. 

When approving an entry, the membership that is created must be tied to a user account to allow the member to login and receive the membership benefits. Sometimes a member may already have an account but not be logged in when they apply for a membership. There is also a possibility that a user may be logged in and fill out the form for another person, especially if it is an administrator who is filling out the application. Because of these options, we allow the administrator who is approving application entries to pair the membership to a current user account that matches the information from the application entry. 

For example, let's say a membership application entry is filled out by an administrator with details for their friend, John Smith at jsmith@example.com. The administrator who then wants to approve this application entry may see the following options for users to pair with the membership:

- Administrator who filled out the form
- Matching John Smith user record from the system
- Create a new user

If there is no matching user record, then that option won't appear. Similarly, if the form wasn't filled out by a logged in user, then the first option won't be available. The **Create a new user** option will always be available, and is the default in the case that no match is found within the system. 

Once a membership application entry is approved, the profile for the paired user will have a new tab for memberships which will include their membership details. 

### [Membership Listing Pages](listings)

**Membership listing pages, or membership directories are currently still in development.**

Membership directories will display all of the approved members for the site. They can be filtered based on the membership type, and will display some of the information from the membership application. Depending on your system settings, the entire directory or pieces of information from the directory may only be available to other members. Site visitors will be prompted to log in or to become members when viewing these areas of the site.

The layout and display of these membership lists can be customized for an extra charge. Because memberships are tied to users, information from their profiles like photos can be displayed.

Their are no immediate plans to add member connection ("friending") functionality or to add in any type of comments on member listings.
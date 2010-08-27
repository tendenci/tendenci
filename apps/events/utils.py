


def next_month(month, year):
    # TODO: cleaner way to get next date
    next_month = (month+1)%13
    next_year = year
    if next_month == 0:
        next_month = 1
        next_year += 1

    return (next_month, next_year)

def prev_month(month, year):
    # TODO: cleaner way to get previous date
    prev_month = (month-1)%13
    prev_year = year
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    return (prev_month, prev_year)

def create_registration_record(*args, **kwargs):
    from events.models import Registration

    event = kwargs.get('event')
    user_account = kwargs.get('user')
    payment_method = kwargs.get('payment_method')
    price = kwargs.get('price')

    # user profile shortcut
    user_profile = user_account.get_profile()

    try: # update registration
        reg8n = Registration.objects.get(
            event=event, creator=user_account, owner=user_account, 
            payment_method=payment_method, amount_paid=price)

    except: # add registration
        reg8n = Registration.objects.create(
            event = event, 
            creator = user_account, 
            owner = user_account,
            payment_method_id = payment_method,
            amount_paid = price
        )

    # get or create registrant
    registrant = reg8n.registrant_set.get_or_create(user=user_account)[0]

    # update registrant information                
    registrant.name = ' '.join((user_account.first_name, user_account.last_name))
    registrant.name = registrant.name.strip()
    registrant.mail_name = user_profile.display_name
    registrant.address = user_profile.address
    registrant.city = user_profile.city
    registrant.state = user_profile.state
    registrant.zip = user_profile.zipcode
    registrant.country = user_profile.country
    registrant.phone = user_profile.phone
    registrant.email = user_profile.email
    registrant.company_name = user_profile.company
    registrant.save()

    reg8n.save() # save registration record
    reg8n.save_invoice() # adds/updates invoice

    # TODO: Debating on whether I should pass
    # the invoice object as well

    return reg8n






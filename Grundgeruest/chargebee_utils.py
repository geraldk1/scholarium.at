import chargebee
from django.conf import settings

chargebee.configure(settings.CHARGEBEE_APIKEY, settings.CHARGEBEE_SITENAME)

def create_customer(data):
    if 'id' in data:
        del data['id']
        # Let chargebee handle creation of customer id

    result = chargebee.Customer.create(data)
    return result.customer

def create_checkout(customer, plan_id):
    plan_data = {
            'plan_id': plan_id
        }
    checkout_data = ({
        'subscription': plan_data,
        'customer': {
            'id': customer.id
        }
    })

    try:
        checkout = chargebee.HostedPage.checkout_new(checkout_data)
        if checkout.hosted_page.state == 'created':
            return checkout.hosted_page
    except InvalidRequestError:
        return None

def new_subscription(customer, plan_id):
    result = chargebee.Subscription.create({
    'plan_id': plan_id,
    'customer': customer,
    })

# def db_to_cb():
#     for

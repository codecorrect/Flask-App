from flask import Flask, render_template, request
import requests
from requests_oauthlib import OAuth1
import logging

app = Flask(__name__)

def request_etsy_token():
    api_key = ""   #make this env var
    api_secret = ""    #make this env var

    #Request token URL
    request_token_url = 'https://openapi.etsy.com/v2/oauth/request_token'   #move to v3
  
    #Init OAuth
    oauth = OAuth1(api_key, client_secret=api_secret)

    #Get request token
    response = requests.post(request_token_url, auth=oauth)
    request_token = dict(response.text.split('&'))

    #Extract request token & secret
    oauth_token = request_token['oauth_token']
    oauth_token_secret = request_token['oauth_token_secret']

    print("Request Token: ", oauth_token)
    print("Request Token Secret: ", oauth_token_secret)

def authorize_etsy_app():
    authorize_url = 'https://www.etsy.com/oauth/signin'
    print(f"Please go to {authorize_url}?oauth_token={oauth_token} and authorize access.")
    verifier = input('Enter the verifier code: ')

def get_etsy_access_token():
    access_token_url = 'https://openapi.etsy.com/v2/oauth/access_token'

    #init OAuth with request token & verifier
    oauth = OAuth1(api_key, client_secret=api_secret, resource_owner_key=oauth_token, resource_owner_secret=oauth_token_secret, verifier=verifier)

    #get access token
    response = requests.post(access_token_url, auth=oauth)
    access_token = dict(response.text.split('&'))

    #extract access token & secret
    oauth_token = access_token['oauth_token']
    oauth_token_secret = access_token['oauth_token_secret']

    print("Request Token: ", oauth_token)
    print("Request Token Secret: ", oauth_token_secret)


def get_etsy_orders():
    oauth = OAuth1(api_key, client_secret=api_secret, resource_owner_key=oauth_token, resource_owner_secret=oauth_token_secret)

    url = 'https://openapi.etsy.com/v2/shops//receipts'

    response = request.get(url, auth=oauth)
    orders = response.json()

    print(orders)


def get_tindie_orders():
    all_tindie_orders = []
    api_key = ''    #FIX - from env var
    url = 'https://www.tindie.com/api/v1/order/?format=json&username=&api_key=' + api_key

    try:
        response = requests.get(url)
        response.raise_for_status()

        if response.status_code == 200:
            orders = response.json()

            #spacer = "    - "

            for order in orders['orders']:
                #create dictionary for this tindie order
                tindie_order = {
                    "order_number": order['number'],
                    "source": "Tindie",
                    "date": order['date'],
                    "date_shipped": order['date_shipped'],  # Placeholder for when it's shipped
                    "email": order['email'],
                    "name": order['shipping_name'],
                    "street": order['shipping_street'],
                    "city": order['shipping_city'],
                    "state": order['shipping_state'],
                    "zip": order['shipping_postcode']
                }
                
                items = []

                for item in order['items']:                
                    this_item = {
                        "product": item['product'],
                        "quantity": item['quantity'],
                        "price_per_unit": item['price_unit'],
                        "price_total": item['price_total']
                    }

                    if 'Assembly Required' in item['options']:
                        this_item['pre_assembled'] = False
                    else:
                        this_item['pre_assembled'] = True

                    if 'Add Power Cable?: Yes' in item['options']:
                        this_item['add_cable'] = True
                    else:
                        this_item['add_cable'] = False

                    items.append(this_item)


                tindie_order['items'] = items

                all_tindie_orders.append(tindie_order)
                
            return all_tindie_orders
    except Timeout as e:
        logging.error(f"Timeout error: {e}")
        return None
    except RequestException as e:
        logging.error(f"Request exception: {e}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return None


#### MAIN ####
all_orders = []


@app.route('/')
def index():
    nav = request.args.get('nav', 'home')

    if nav == 'home':
        data = {'title': 'Home'}
    elif nav == 'orders':
        data = {'title': 'Orders', 'orders': get_tindie_orders()}
    elif nav == 'stock':
        data = {'title': 'Stock'}
    elif nav == 'tasks':
        data = {'title': 'Tasks'}
    elif nav == 'profit':
        data = {'title': 'Profit'}
    else:
        data = {'title': 'Home'}
    return render_template('index.html', nav=nav, data=data)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)

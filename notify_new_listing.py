
import requests
from bs4 import BeautifulSoup
from os.path import exists
import json
from datetime import date
import nepali_datetime


def get_pantry_json(api_key = "aa3e70ae-0fde-40d1-abb7-cf29b6271491", bucket = "nepse_stock_list"):
    uri = f"https://getpantry.cloud/apiv1/pantry/{api_key}/basket/{bucket}"

    r = requests.get(uri, headers = {"Content-Type": "application/json"})

    if r.status_code == 200:
        return json.loads(r.text)
    else:
        {"status": r.status_code, "source": "pantry"}


def update_pantry_json(data, api_key = "aa3e70ae-0fde-40d1-abb7-cf29b6271491", bucket = "nepse_stock_list"):
    uri = f"https://getpantry.cloud/apiv1/pantry/{api_key}/basket/{bucket}"

    r = requests.post(uri, headers = {"Content-Type": "application/json"}, data = json.dumps(data))

    if r.status_code == 200:
        return 0
    else:
        return 1

def find_new_listing(prev_listing, get_from_func, source, listing, new_listing):
    prev_symbols = prev_listing.get(source, {})
    current_list = get_from_func()
    new_list = set(current_list) - set(prev_symbols)

    listing[source] = list(current_list)
    new_listing[source] = list(new_list)

    return listing, new_listing


# nepsealpha
def get_from_nepsealpha():
    r = requests.get('https://nepsealpha.com/trading/1/search')
    if r.status_code == 200:
        s = r.json()
        symbols = set([i.get('symbol', "") for i in s])
        return symbols
    return {}


#nepalstock
def get_from_nepalstock():
    r = requests.get('http://www.nepalstock.com/')
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, "html.parser")
        option = soup.find("select",{"name":"StockSymbol_Select"}).findAll("option")
        symbols = set([item.text for item in option if "Choose Symbol" not in item.text])
        return symbols

    return {}


# merolagani
def get_from_merolagani():
    r = requests.get('https://merolagani.com/handlers/AutoSuggestHandler.ashx?type=Company')
    if r.status_code == 200:
        s = list(eval(r.text))
        symbols = set([i.get('d', "") for i in s])
        return symbols

    return {}


def send_msg_on_telegram(message, telegram_auth_token, telegram_group_id):
    telegram_api_url = f"https://api.telegram.org/bot{telegram_auth_token}/sendMessage?chat_id=@{telegram_group_id}&text={message}"
    tel_resp = requests.get(telegram_api_url)
    if tel_resp.status_code == 200 :
        print ("INFO : Notification has been sent on Telegram")
    else :
        print("ERROR : Could not send Message")


def schedule_job():
    telegram_auth_token = "5338104596:AAFOa77XzlZT4cFOyLVQ6wVe8Drz7UirlCE"
    telegram_group_id = "nepse_info_group"

    previous_listing_file = "prev_list.json"
    listing = {"date": str(nepali_datetime.datetime.now())}  # to save to json file
    new_listing = {"date": str(nepali_datetime.datetime.now())}  # to send to notification

    #read the json file
    try:
        prev_listing = get_pantry_json()
    except:
        prev_listing = {}

    try:
        find_new_listing(prev_listing, get_from_nepsealpha, 'nepsealpha', listing, new_listing)
        find_new_listing(prev_listing, get_from_nepalstock, 'nepalstock', listing, new_listing)
        find_new_listing(prev_listing, get_from_merolagani, 'merolagani', listing, new_listing)
        print("Sucess")
    except:
        print("Some Souurces doesnt work")

    ## Finally save this to file
    try:
        r = update_pantry_json(listing)
    except:
        r = 1
    if r == 1:
        print("Couldn't save the bucket")


    # Now send the new listings to notification
    msg = "Update: New Stock Listing \n" + json.dumps(new_listing)
    # send_msg_on_telegram(msg, telegram_auth_token, telegram_group_id)

    num_new_stocks = 0
    for k,v in new_listing.items():
        if k == "date":
            continue
        num_new_stocks += len(v)

    if num_new_stocks == 0:
        print(".")
        send_msg_on_telegram(".", telegram_auth_token, telegram_group_id)
    else:
        print(msg)
        send_msg_on_telegram(msg, telegram_auth_token, telegram_group_id)

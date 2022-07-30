
import requests
from bs4 import BeautifulSoup
from os.path import exists
import json
from datetime import date
import nepali_datetime


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

    prev_file_exists = exists(previous_listing_file)
    if not prev_file_exists:
        # create new file
        f = open(previous_listing_file, "a")
        data = {
            "date": ""
        }
        json_object = json.dumps(data, indent=4)
        f.write(json_object)
        f.close()

    try:
        f = open(previous_listing_file, "r")
        prev_listing = json.load(f)
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
    f.close()
    f = open(previous_listing_file, "w")
    json_object = json.dumps(listing, indent=4)
    f.write(json_object)
    f.close()

    # Now send the new listings to notification
    msg = "Update: New Stock Listing \n" + json.dumps(new_listing)
    send_msg_on_telegram(msg, telegram_auth_token, telegram_group_id)

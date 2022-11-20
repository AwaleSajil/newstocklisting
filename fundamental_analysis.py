import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from datetime import date


def tables_to_dict(tables):
    d = {}

    if tables is None:
        return d
    sub_tables = tables.find_all('tbody')

    if sub_tables is None:
        return d

    for st in sub_tables:
        row = st.find_all('tr')
        if row is None:
            continue
        else:
            row = row[0]
        th = row.find('th')
        td = row.find('td')
        if th is not None and td is not None:
            d[" ".join(th.text.strip().split())] = " ".join(td.text.strip().split())

    return d


# Top 5 symbols qith market price closest to market price

def best_symbols_based_on_book_value(symbol_info, top=5):
    df = pd.DataFrame(columns=['Symbols', 'Change', 'Market price', 'Book Value'])
    for s, info in symbol_info.items():
        market_price = None
        book_value = None

        if info.get('Last Traded On', None) is not None:
            last_trade_date = info.get('Last Traded On', None)
            if last_trade_date == '':
                continue
            last_trade_date = datetime.strptime(last_trade_date, '%Y/%m/%d %H:%M:%S')
            if (date.today() - last_trade_date.date()).days > 7:
                continue
            last_date = str(last_trade_date)
        else:
            continue

        if info.get('Market Price', None) is not None:
            market_price = float(info.get('Market Price', None).replace(",", ""))
        if info.get('Book Value', None) is not None:
            book_value = float(info.get('Book Value', None).replace(",", ""))

        if market_price is not None and book_value is not None:
            if market_price == 0:
                continue
            change = (book_value - market_price) / market_price
            df = df.append(
                {'Symbols': s, 'Change': change,
                 'Market price': market_price,
                 'Book Value': book_value,
                 'Last Trade Date': last_date
                 }, ignore_index=True)
    df = df.sort_values(by=['Change'], ascending=False)
    df.set_index('Symbols', inplace=True)

    temp = df.head(top)[['Market price', 'Book Value']]

    return (temp.to_string())


def best_symbols_based_on_cash(symbol_info, top=10):
    df = pd.DataFrame()
    for s, info in symbol_info.items():
        market_price = None
        cash_per_1000 = None

        if info.get('Last Traded On', None) is not None:
            last_trade_date = info.get('Last Traded On', None)
            if last_trade_date == '':
                continue
            last_trade_date = datetime.strptime(last_trade_date, '%Y/%m/%d %H:%M:%S')
            if (date.today() - last_trade_date.date()).days > 7:
                continue
            last_date = str(last_trade_date)
        else:
            continue

        if info.get('Market Price', None) is not None:
            market_price = float(info.get('Market Price', None).replace(",", ""))
        if info.get('% Dividend', None) is not None:
            dividend_percent = info.get('% Dividend', None).split(" ")[0]
            dividend_percent = dividend_percent.replace(",", "")
            if dividend_percent == '':
                continue
            else:
                cost_price = min([10, 100], key=lambda x: abs(x - market_price))
                dividend_per_share = float(dividend_percent) / 100 * cost_price

        if market_price is not None and dividend_per_share is not None:
            if market_price == 0:
                continue
            cash_per_1000 = (dividend_per_share / market_price) * 1000
            df = df.append(
                {'Symbols': s, 'Cash /1000 invested': round(cash_per_1000,2),
                 'Market price': market_price,
                 'Last Trade Date': last_date
                 }, ignore_index=True)
    df = df.sort_values(by=['Cash /1000 invested'], ascending=False)
    df.set_index('Symbols', inplace=True)

    temp = df.head(top)[['Cash /1000 invested', 'Market price']]

    return (temp.to_string())

def get_symbols_info():
    r = requests.get('https://merolagani.com/handlers/AutoSuggestHandler.ashx?type=Company')
    symbols = None
    if r.status_code == 200:
        s = list(eval(r.text))
        symbols = set([i.get('d', "") for i in s])

    symbol_info_uri = "https://merolagani.com/CompanyDetail.aspx?symbol="
    symbol_info = {}
    for symbol in symbols:
        uri = symbol_info_uri + symbol
        r = requests.get(uri)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text)
            table = soup.find('table', attrs={'id': 'accordion'})
            symbol_info[symbol] = tables_to_dict(table)

    return symbol_info

def message_formater(book_value_analysis, cash_dividend_analysis):
    msg = " --- Weekly Fundamental Analysis ---\n"
    msg += "-----------------------------------\n"
    msg += "Top Stocks based on book and market value\n"
    msg += book_value_analysis
    msg += "\n-----------------------------------\n"
    msg += "Top Stocks based on Cash Dividend Last year\n"
    msg += cash_dividend_analysis
    msg += "\n-----------------------------------"

    return msg


def send_msg_on_telegram(message, telegram_auth_token, telegram_group_id):
    telegram_api_url = f"https://api.telegram.org/bot{telegram_auth_token}/sendMessage?chat_id=@{telegram_group_id}&text={message}"
    tel_resp = requests.get(telegram_api_url)
    if tel_resp.status_code == 200 :
        print ("INFO : Notification has been sent on Telegram")
    else :
        print("ERROR : Could not send Message")

def funda_analysis_job():
    telegram_auth_token = "5338104596:AAFOa77XzlZT4cFOyLVQ6wVe8Drz7UirlCE"
    telegram_group_id = "nepse_info_group"

    symbol_info = get_symbols_info()
    book_value_analysis = best_symbols_based_on_book_value(symbol_info)
    cash_dividend_analysis = best_symbols_based_on_cash(symbol_info,10)
    msg  = message_formater(book_value_analysis, cash_dividend_analysis)
    print(msg)

    send_msg_on_telegram(msg, telegram_auth_token, telegram_group_id)




if __name__ == "__main__":
    funda_analysis_job()

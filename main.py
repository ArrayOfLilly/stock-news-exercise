import datetime as dt
import os

import requests
from twilio.rest import Client

# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

EQUITY_NAME = 'TSLA'
COMPANY_NAME = 'Tesla Inc'

API_KEY_ALPHAVANTAGE = os.environ.get('API_KEY_ALPHAVANTAGE')
ALPHAVANTAGE_API_ENDPOINT = 'https://www.alphavantage.co/query'

API_KEY_NEWSAPI = os.environ.get('API_KEY_NEWSAPI')
NEWSAPI_API_ENDPOINT = 'https://newsapi.org/v2/everything'

TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
FROM = os.environ.get('FROM')
TO = os.environ.get('TO')

parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': EQUITY_NAME,
    'apikey': API_KEY_ALPHAVANTAGE
}

url = ALPHAVANTAGE_API_ENDPOINT
r = requests.get(url, params=parameters)
data = r.json()
date_list = [key for key in data['Time Series (Daily)']]

last_workday_result = float(data['Time Series (Daily)'][date_list[1]]['4. close'])
print(last_workday_result)
last_workday_before_last_workday_result = float(data['Time Series (Daily)'][date_list[2]]['4. close'])
print(last_workday_before_last_workday_result)

difference_between_daily_result = last_workday_before_last_workday_result - last_workday_result
print(difference_between_daily_result)
difference_between_daily_result_percent = (difference_between_daily_result / last_workday_before_last_workday_result
                                           * 100)
print(difference_between_daily_result_percent)

if abs(difference_between_daily_result_percent) > 4:
    # STEP 2: Use https://newsapi.org
    # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.

    print('Get News')

    today = dt.date.today()
    week_ago = today - dt.timedelta(days=7)

    headers = {
        'X-Api-Key': API_KEY_NEWSAPI
    }

    parameters = {
        'q': COMPANY_NAME,
        'from': dt.date.today() - dt.timedelta(days=3),
        'sortBy': 'publishedAt',
    }
    url = NEWSAPI_API_ENDPOINT
    r = requests.get(url, headers=headers, params=parameters)
    data = r.json()
    article_list = data['articles'][:3]

    # STEP 3: Use https://www.twilio.com
    # Send a separate message with the percentage change and each article's title and description to your phone number.

    # Optional: Format the SMS message like this:
"""
    TSLA: 🔺2%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to 
    file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height 
    of the coronavirus market crash.
    or
    "TSLA: 🔻5%
    Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
    Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to 
    file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height 
    of the coronavirus market crash.
    """

account_sid = TWILIO_ACCOUNT_SID
auth_token = TWILIO_AUTH_TOKEN
client = Client(account_sid, auth_token)

symbol = '🔺' if difference_between_daily_result_percent > 0 else '🔻'

for article in article_list:
    message_content = f"""
        TSLA: {symbol} {round(difference_between_daily_result_percent, 2)}%\n
        Headline: {article['title']}\n
        Brief: {article['description']}
        """
    print(message_content)
    message = client.messages \
        .create(
        body=message_content,
        from_=FROM,
        to=TO
    )

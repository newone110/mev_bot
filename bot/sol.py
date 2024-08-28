import requests

def get_solana_price():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {
        "symbol": "SOL",
        "convert": "USD"
    }
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "877fff13-5b22-441c-8ba9-f0cf19ea69a5"
    }
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            solana_info = data["data"]["SOL"]
            solana_price = solana_info["quote"]["USD"]["price"]
            formatted_price = "{:,.2f}".format(solana_price)  # Format the price with commas and no decimals
            return formatted_price
        else:
            return None  # or some default value
    else:
        return None  # or some default value

print(get_solana_price())
import requests

def convert_currency(amount, from_currency, to_currency):
    """
    Converts currency. Returns clean format for frontend.
    """
    # Static fallback rates (Base USD)
    rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 150.0,
        "INR": 83.0,
        "AUD": 1.52,
        "CAD": 1.35
    }

    try:
        url = f"https://api.frankfurter.app/latest?amount={amount}&from={from_currency}&to={to_currency}"
        res = requests.get(url, timeout=3)
        if res.status_code == 200:
            data = res.json()
            converted = data["rates"][to_currency]
            rate = converted / amount
            return {
                "success": True,
                "data": {
                    "converted_amount": converted,
                    "exchange_rate": rate
                }
            }
    except:
        pass

    # Fallback
    if from_currency in rates and to_currency in rates:
        usd = amount / rates[from_currency]
        converted = round(usd * rates[to_currency], 2)
        rate = rates[to_currency] / rates[from_currency]
        return {
            "success": True,
            "data": {
                "converted_amount": converted,
                "exchange_rate": rate
            }
        }

    return {"success": False}

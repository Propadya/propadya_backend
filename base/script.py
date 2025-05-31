from currencies.models import ExchangeRateManager


def get_prices():
    prices = ExchangeRateManager().get_today_price_in_different_currencies(
        119.536921, "BDT"
    )
    print(prices)

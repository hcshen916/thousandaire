"""
Function of trading cost for currency_price_tw.
"""

def calculate_cost(yesterday, today, price):
    """
    Calculate trading cost.

    This function is designed to calculate "today's" trading cost.
    "Today" will move by simulator, so we don't need to handle it
    in this function.

    The trading cost is calculated while selling the target.
    """
    difference = yesterday.quantity - today.quantity
    spread = price.sell - price.buy
    return max(0, difference * spread)

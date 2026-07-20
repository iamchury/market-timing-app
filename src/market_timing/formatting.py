def format_price(value, currency): return f'${value:,.2f}' if currency == 'USD' else f'₩{value:,.0f}'

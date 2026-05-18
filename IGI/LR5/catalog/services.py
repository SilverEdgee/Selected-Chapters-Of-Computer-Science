from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import requests


def fetch_external_api_results(endpoints, timeout=4):
    def fetch_one(item):
        title, url = item
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return {'title': title, 'ok': True, 'data': response.json()}
        except Exception as exc:  # pragma: no cover - network may be unavailable
            return {'title': title, 'ok': False, 'error': str(exc)}

    if not endpoints:
        return []

    max_workers = min(4, len(endpoints))
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(fetch_one, endpoints))


def fetch_currency_rates(timeout=4):
    """Useful API for the project: show BYN exchange rates for common currencies.

    Uses the Belarus National Bank API. Returns a list of dicts with human-friendly data.
    """
    currencies = ['USD', 'EUR', 'RUB']
    rates = []
    for code in currencies:
        url = f'https://www.nbrb.by/api/exrates/rates/{code}?parammode=2'
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        scale = Decimal(str(data.get('Cur_Scale', 1)))
        official = Decimal(str(data.get('Cur_OfficialRate', '0')))
        byn_per_unit = (official / scale).quantize(Decimal('0.0001'))
        rates.append({
            'code': code,
            'name': data.get('Cur_Name', code),
            'scale': int(scale),
            'byn_per_unit': str(byn_per_unit),
            'date': data.get('Date'),
        })
    return rates


def fetch_minsk_weather(timeout=4):
    """Useful API for the project: current weather in Minsk for logistics/planning."""
    url = (
        'https://api.open-meteo.com/v1/forecast'
        '?latitude=53.9000&longitude=27.5667&current_weather=true&timezone=Europe%2FMinsk'
    )
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    current = data.get('current_weather') or {}
    return {
        'temperature': current.get('temperature'),
        'windspeed': current.get('windspeed'),
        'winddirection': current.get('winddirection'),
        'weathercode': current.get('weathercode'),
        'time': current.get('time'),
    }



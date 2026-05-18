from concurrent.futures import ThreadPoolExecutor

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


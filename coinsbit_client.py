import time
import json
import requests
import hmac, hashlib, base64
from typing import Dict, Tuple, List, Optional


class CoinsbitClient():
    REQUEST_TIMEOUT: float = 10

    API_URL = "https://coinsbit.io"

    API_PUBLIC_MARKETS = "/api/v1/public/markets"
    API_PUBLIC_TICKERS = "/api/v1/public/tickers"
    API_PUBLIC_TICKER = "/api/v1/public/ticker"
    API_PUBLIC_BOOK = "/api/v1/public/book"
    API_PUBLIC_HISTORY = "/api/v1/public/history"
    API_PUBLIC_HISTORY_RESULT = "/api/v1/public/history/result"
    API_PUBLIC_PRODUCTS = "/api/v1/public/products"
    API_PUBLIC_SYMBOLS = "/api/v1/public/symbols"
    API_PUBLIC_DEPTH = "/api/v1/public/depth/result"
    API_PUBLIC_KLINE = "/api/v1/public/kline"

    API_LIMIT_ORDER = "/api/v1/order/new"
    API_MARKET_ORDER = "/api/v1/order/new_market"
    API_CANCEL_ORDER = "/api/v1/order/cancel"
    API_ACTIVE_ORDER = "/api/v1/orders"

    API_ACCOUNT_BALANCES = "/api/v1/account/balances"
    API_ACCOUNT_BALANCE = "/api/v1/account/balance"
    API_ACCOUNT_ORDER = "/api/v1/account/order"
    API_ACCOUNT_ORDER_HISTORY = "/api/v1/account/order_history_list"

    SIDE_BUY = 'buy'
    SIDE_SELL = 'sell'

    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        self.API_KEY = api_key
        self.API_SECRET = api_secret
        self.session = self._session()
        self.response = None

    def _session(self):
        headers = {
            'Content-type': 'application/json'
        }
        if self.API_KEY:
            # assert self.API_KEY
            headers['X-TXC-APIKEY'] = self.API_KEY

        session = requests.session()
        session.headers.update(headers)
        return session

    def _order_params(self, path, params: Dict = None):
        list_params = {
            'request': path
        }
        if params:
            list_params.update(params)
        list_params['nonce'] = str(int(time.time() * 1000))
        return list_params

    def _update_headers(self, params: Dict):
        params_query = json.dumps(params).replace(" ", "")
        payload = base64.b64encode(params_query.encode('ascii'))
        payload_str = payload.decode()
        signature = hmac.new(self.API_SECRET.encode('utf-8'), payload, hashlib.sha512).hexdigest()
        headers = {
            'X-TXC-PAYLOAD': payload_str,
            'X-TXC-SIGNATURE': signature
        }
        self.session.headers.update(headers)

        return params_query

    def _request(self, method, path, **kwargs):
        if not kwargs['data']:
            if method == "get":
                self.response = self.session.get(url=self.API_URL + path)
            elif method == "post":
                params = self._order_params(path)
                params_query = self._update_headers(params)
                self.response = self.session.post(url=self.API_URL + path, data=params_query)

        elif kwargs['data']:
            if method == "get":
                params = []
                for key, values in kwargs['data'].items():
                    params.append((key, str(values)))

                params_query = '&'.join(f"{p[0]}={p[1]}" for p in params)
                self.response = self.session.get(url=self.API_URL + path + "?" + params_query)

            elif method == "post":
                params = self._order_params(path, kwargs['data'])
                params_query = self._update_headers(params)
                self.response = self.session.post(url=self.API_URL + path, data=params_query)

        return self.response.json()

    def _get(self, path, **kwargs):
        return self._request('get', path, **kwargs)

    def _post(self, path, **kwargs):
        return self._request('post', path, **kwargs)

    # Public
    def get_ticker(self, **params):
        return self._get(self.API_PUBLIC_TICKER, data=params)

    def get_orderbook(self, **params):
        return self._get(self.API_PUBLIC_BOOK, data=params)

    def get_depth_list(self, **params):
        return self._get(self.API_PUBLIC_DEPTH, data=params)

    # Private
    def get_ticker_pivate(self, **params):
        return self._post(self.API_PUBLIC_TICKER, data=params)

    def get_orderbook_private(self, **params):
        return self._post(self.API_PUBLIC_BOOK, data=params)

    # Market
    def create_limit_order(self, **params):
        return self._post(self.API_LIMIT_ORDER, data=params)

    def create_market_order(self, **params):
        return self._post(self.API_MARKET_ORDER, data=params)

    def cancel_order(self, **params):
        return self._post(self.API_CANCEL_ORDER, data=params)

    def get_active_order(self, **params):
        return self._post(self.API_ACTIVE_ORDER, data=params)

    # Account
    def get_balances(self, **params):
        return self._post(self.API_ACCOUNT_BALANCES, data=params)

    def get_balance(self, **params):
        return self._post(self.API_ACCOUNT_BALANCE, data=params)

    def get_order_info(self, **params):
        return self._post(self.API_ACCOUNT_ORDER, data=parmas)

    def get_order_history(self, **params):
        return self._post(self.API_ACCOUNT_ORDER_HISTORY, data=params)



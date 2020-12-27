"""BitBankのトレード結果をスプレッドシートに書き込む"""

from __future__ import absolute_import, division, print_function, unicode_literals
from hashlib import sha256
from logging import getLogger
import requests, hmac, time, json, os, datetime

try:
    from urllib import urlencode
except:
    from urllib.parse import urlencode

logger = getLogger(__name__)

BB_AKEY = os.environ['BB_AKEY']
BB_SKEY = os.environ['BB_SKEY']


def sign_request(key, query):
    h = hmac.new(bytearray(key, 'utf8'), bytearray(query, 'utf8'), sha256)
    return h.hexdigest()

def make_header(query_data, api_key, api_secret):
    nonce = str(int(time.time() * 1000))
    message = nonce + query_data
    return {
        'Content-Type': 'application/json',
        'ACCESS-KEY': api_key,
        'ACCESS-NONCE': nonce,
        'ACCESS-SIGNATURE': sign_request(api_secret, message)
    }

class bitbankcc_private(object):
    
    def __init__(self, api_key, api_secret):
        self.end_point = 'https://api.bitbank.cc/v1'
        self.api_key = api_key
        self.api_secret = api_secret
    
    def _get_query(self, path, query):
        data = '/v1' + path + urlencode(query)
        logger.debug('GET: ' + data)
        headers = make_header(data, self.api_key, self.api_secret)
        uri = self.end_point + path + urlencode(query)
        response = requests.get(uri, headers=headers)
        return response.json()
    
    def _post_query(self, path, query):
        data = json.dumps(query)
        logger.debug('POST: ' + data)
        headers = make_header(data, self.api_key, self.api_secret)
        uri = self.end_point + path
        response = requests.post(uri, data=data, headers=headers)
        return response.json()
    
    def get_asset(self):
        return self._get_query('/user/assets', {})
    
    def get_order(self, pair, order_id):
        return self._get_query('/user/spot/order?', {
            'pair': pair,
            'order_id': order_id
        })
    
    def get_active_orders(self, pair, options=None):
        if options is None:
            options = {}
        if not 'pair' in options:
            options['pair'] = pair
        return self._get_query('/user/spot/active_orders?', options)

    def order(self, pair, price, amount, side, order_type):
        return self._post_query('/user/spot/order', {
            'pair': pair,
            'price': price,
            'amount': amount,
            'side': side,
            'type': order_type
        })
    
    def cancel_order(self, pair, order_id):
        return self._post_query('/user/spot/cancel_order', {
            'pair': pair,
            'order_id': order_id
        })

    def cancel_orders(self, pair, order_ids):
        return self._post_query('/user/spot/cancel_orders', {
            'pair': pair,
            'order_ids': order_ids
        })

    def get_orders_info(self, pair, order_ids):
        return self._post_query('/user/spot/orders_info', {
            'pair': pair,
            'order_ids': order_ids
        })

    def get_trade_history(self, pair, order_count, since_timestamp, end_timestamp):
        return self._get_query('/user/spot/trade_history?', {
            'pair': pair,
            'count': order_count,
            'since': since_timestamp,
            'end': end_timestamp,
        })

    def get_withdraw_account(self, asset):
        return self._get_query('/user/withdrawal_account?', {
            'asset': asset
        })

    def request_withdraw(self, asset, uuid, amount, token):
        q = {
            'asset': asset,
            'uuid': uuid,
            'amount': amount
        }
        q.update(token)
        return self._post_query('/user/request_withdrawal', q)



# main
prv = bitbankcc_private(BB_AKEY, BB_SKEY)

now = datetime.datetime.now()
since_timestamp = int((now - datetime.timedelta(hours=2)).timestamp() * 1000) 
end_timestamp = int(now.timestamp() * 1000)
value = prv.get_trade_history(
    'btc_jpy', # ペア
    '1000', # 取得する約定数
    since_timestamp,
    end_timestamp,
)

print(value)
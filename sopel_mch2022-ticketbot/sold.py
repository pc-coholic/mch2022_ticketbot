import os
import json
import requests

from sopel.module import commands, rate, priority, NOLIMIT
from sopel.logger import get_logger

logger = get_logger(__name__)
token = os.environ.get('PRETIX_TOKEN')

def setup(bot):
    if token == None:
        raise RuntimeError('PRETIX_TOKEN not defined')

    if 'sold_data' not in bot.memory:
        bot.memory['sold_data'] = {
          "paid_orders": 0,
          "pending_orders": 0,
          "exited_orders": 0,
          "blocking_vouchers": 0,
          "cart_positions": 0,
          "waiting_list": 0,
          "available_number": 0,
          "available": True,
          "total_size": 0
        }

@commands('sold')
@rate(30)
@priority('low')
def sold(bot, trigger):
    data = gettickets(bot)
    sold = data['paid_orders'] + data['pending_orders']
    available = data['available_number']
    bot.say('Tickets sold: %d. Still available: %d' % (sold, available))

def gettickets(bot):
    headers = {}
    headers['Accept'] = 'application/json'
    headers['Authorization'] = 'Token %s' % str(token)
    url = 'https://tickets.ifcat.org/api/v1/organizers/ifcat/events/mch2022/quotas/20/availability/'

    try:
      resp = requests.get(url, headers=headers)
      resp.raise_for_status()
      bot.memory['sold_data'] = resp.json()
    except Exception as err:
      logger.error('%s', str(err))

    return bot.memory['sold_data']


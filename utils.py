# -*- coding: utf-8 -*-

from config import YOUR_API_KEY

separator = '&'

## Skobbler routing
url_routing = 'http://1ba644dc0676eb52d755a123c36c313d.tor.skobbler.net/tor/RSngx/calcroute/json/20_5/en/1ba644dc0676eb52d755a123c36c313d?start=%s&dest=%s&profile=carEfficient&advice=no&points=yes&highways=%s&toll=%s'


# ##Skobbler RealReach
# url = 'http://'+YOUR_API_KEY+'.tor.skobbler.net/tor/RSngx/RealReach/json/20_5/en/'+YOUR_API_KEY+'?'
# start = 'start='
# transport = 'transport=car'
# distance = 'range='
# units = 'units='
# nonReachable = 'nonReachable=0'
# response_type = 'response_type=gps'
# highways = 'highways='
# toll = 'toll='

# url_realreach = separator.join((url,
#                                 'start='
#                                 + '%s',
#                                 'transport=car',
#                                 'range='
#                                 + '%s',
#                                 'units='
#                                 + '%s',
#                                 'highways='
#                                 + '%s',
#                                 'toll='
#                                 + '%s',
#                                 'nonReachable=0',
#                                 'response_type=gps'
#                                 ))
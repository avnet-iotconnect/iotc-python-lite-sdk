import urllib.request
from urllib.request import Request

from datetime import datetime

url='https://awsdiscovery.iotconnect.io/api/v2.1/dsdk/cpId/97FF86E8728645E9B89F7B07977E4B15/env/poc'
print(datetime.now().timestamp())
resp = urllib.request.urlopen(urllib.request.Request(url))
print(resp.read())
print(datetime.now().timestamp())




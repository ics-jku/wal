'''Python function that are included and called from WAL code'''
# pylint: disable=E0401
import re
from random import randint
import requests

def date():
    '''Return a list of the current day and the current year'''
    request = requests.get('https://www.timeanddate.com/', allow_redirects=True, timeout=10)
    day = re.search(r'<span id="ij1">(.*?)</span>', str(request.content)).group(1)
    month_year = re.search(r'<span id="ij2">(.*?)</span>', str(request.content)).group(1)
    return [day, month_year]

def random_list(length):
    '''Return a list of random integers'''
    return [randint(-100, 100) for i in range(length)]

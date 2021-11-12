def date():
    import re
    import requests
    request = requests.get('https://www.timeanddate.com/', allow_redirects=True)
    day = re.search(r'<span id="ij1">(.*?)</span>', str(request.content)).group(1)
    date = re.search(r'<span id="ij2">(.*?)</span>', str(request.content)).group(1)
    return [day, date]

def random_list(x):
    from random import randint
    return [randint(-100, 100) for i in range(x)]

from multiprocessing import Pool
import requests
import re
from datetime import datetime

URLS = ["https://test.encodedcc.org"]
MAX_URLS = 5000
def query_list(base_url):
    arr = []
    with open('access-recent.log', mode='r') as log_file:
        for line in log_file:
#           if any(time_filter in line for time_filter in ['08/Jun/2016:21:3']):
            if True:
                match = re.findall(r'\"(.+?)\"', line)
                if 'HEAD' in match[0] or 'GET' in match[0]:
                    if not any(term in match[0] for term in ['limit=all', 'icon', '.png', '.ico', '@download']):
                        arr.append(base_url + match[0].split()[1])
            if len(arr) > MAX_URLS:
                break
    return arr

def make_get(url):
    try:
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
        s = requests.Session()
        r = s.get(url, headers=headers)
        print(r.headers['X-Stats'].split('&queue_time=')[1].split('&')[0])
    except:
        pass

if __name__ == '__main__':
    for url in URLS:
        arr = query_list(url)
        pool = Pool(processes=100)
        before = datetime.now()
        print('starting with {} requests at url '.format(len(arr)), url)
        result = pool.map(make_get, arr)
        pool.close()
        pool.join()
        after = datetime.now()
        print(after - before)

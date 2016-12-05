from multiprocessing import Pool
import requests
import re
import sys
from datetime import datetime


URLS = [str(sys.argv[1])]


def query_list(base_url):
    arr = []
    with open('access.log', mode='r') as log_file:
        for line in log_file:
            match = re.findall(r'\"(.+?)\"', line)
            if match and 'GET' in match[0]:
                if not any(term in match[0] for term in ['limit=all', 'icon', '.png', '.ico', '@download']):
                    arr.append(base_url + match[0].split()[1])
    return arr

def make_get(url):
    try:
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36"}
        s = requests.Session()
        r = s.get(url, headers=headers)
    except IOError as e:
        print ("ERROR: ")
        print (e)
        pass

if __name__ == '__main__':
    for url in URLS:
        arr = query_list(url)[:2000]
        pool = Pool(processes=100)
        before = datetime.now()
        print('starting with {} requests at url '.format(len(arr)), url)
        result = pool.map(make_get, arr)
        pool.close()
        pool.join()
        after = datetime.now()
        print(after - before)

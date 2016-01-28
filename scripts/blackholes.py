'''
Report on 'blackhole' objects, those which are embedded in over many other objects.

Care should be taken with the reverse links from blackhole objects.
'''

from collections import defaultdict
import json


rows = [json.loads(line) for line in open('embeds.txt')]
uuid_row = {row['uuid']: row for row in rows}

CUTOFF = 1000

by_type = defaultdict(list)
for row in rows:
    if row['embeds'] >= CUTOFF:
        by_type[row['item_type']].append(row)

print(json.dumps({k: len(v) for k, v in by_type.items()}, sort_keys=True, indent=4))

'''
Report on number of transacations that invalidate many objects.

  $ sudo -u encoded psql -tAc "select row_to_json(transactions) from transactions where timestamp::date = '2016-01-20'::date;" > transactions.txt

Beware that reverse link invalidations are entered into the transaction log, so any changes will not be reflected.
'''

transactions = [json.loads(line) for line in open('transactions.txt')]

sum_txn = [(sum(uuid_row[uuid]['embeds'] for uuid in txn['data']['updated']), txn) for txn in transactions]
print('Transactions > {}'.format(CUTOFF), sum(s > CUTOFF for s, row in sum_txn))

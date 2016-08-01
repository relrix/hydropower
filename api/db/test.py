#!/usr/bin/env python

from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex

from CodernityDB.database_thread_safe import ThreadSafeDatabase
from CodernityDB.database import RecordNotFound

import time

cdb = ThreadSafeDatabase('database')
#db = Database('database')
if cdb.exists():
    cdb.open()
    cdb.reindex()
else:
    #from database_indexes import UserIndex, MessageAllIndex, MessageUserIndex, FollowerRel1Index, FollowerRel2Index, UserIDIndex, FollowerIndex
    print("no database pressent")
    quit()

print cdb.count(cdb.all, 'eventid')
insert_dict = {"eventid": "123" , "port": "0", "server": "127.0.0.1" }
cdb.insert(insert_dict)
try:
    print "tesit"
    rv = cdb.get('eventid', '123', with_doc=True, with_storage=True)
    # rv= user['doc']['pw_hash']
except RecordNotFound:
    rv = None
else:
    #time.sleep(20)
    data = rv['doc']
    print data
    print rv
#print cdb.delete({'_id' : data['_id'] ,'_rev': data['_rev']})
print rv

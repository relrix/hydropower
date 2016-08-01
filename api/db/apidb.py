"""api db interface.

Copyright (C) 2016 - Shishir Pokharel
shishir.pokharel@gmail.com

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""


from hashlib import md5
from CodernityDB.hash_index import HashIndex

from CodernityDB.database_thread_safe import ThreadSafeDatabase
from CodernityDB.database import RecordNotFound


class dbinterface ():
    """db interface."""

    _DATABASE = 'db/database'

    def __init__(self):
        """initialize."""
        self.dict = {"eventid": '', "port": 0, "server": '127.0.0.1'}

    def getport(self, eventid):
        """get port or insert data."""
        cdb = ThreadSafeDatabase(self._DATABASE)
        if cdb.exists():
            cdb.open()
            cdb.reindex()
            try:
                print eventid
                record_dict = cdb.get('eventid', eventid, with_doc=True, with_storage=True)
                record = record_dict['doc']
                cdb.close()
                return record['port']

            except RecordNotFound:
                print "Record not Found"
                self.dict['eventid'] = eventid
                cdb.insert(self.dict)
                cdb.close()
                return None

        else:
            cdb.create()
            cdb.add_index(CustomEventidIndex(cdb.path, "eventid"))
            self.dict['eventid'] = eventid
            cdb.insert(self.dict)
            cdb.close()
            return None

    def delete_data(self, eventid):
        """delete data."""
        cdb = ThreadSafeDatabase(self._DATABASE)
        status = False
        if cdb.exists():
            cdb.open()
            cdb.reindex()
        try:
            record_dict = cdb.get('eventid', eventid, with_doc=True, with_storage=True)
            record = record_dict['doc']
            cdb.delete({'_id': record['_id'], '_rev': record['_rev']})
            status = True
        except RecordNotFound:
            print "Record not Found"
            status = False
        except:
            print "Error"
            status = False
        finally:
            cdb.close()
            return status


def access_db(eventid):
    """db access point."""
    db = dbinterface()
    return db.getport(str(eventid))


def del_record(eventid):
    """db access point."""
    db = dbinterface()
    return db.delete_data(str(eventid))


class CustomEventidIndex(HashIndex):
    """custom index."""

    def __init__(self, *args, **kwargs):
        """init."""
        kwargs['key_format'] = '16s'
        kwargs['hash_lim'] = 1
        super(CustomEventidIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        """make key value."""
        return md5(data["eventid"]) .digest(), None

    def make_key(self, key):
        """"make key."""
        return md5(key).digest()

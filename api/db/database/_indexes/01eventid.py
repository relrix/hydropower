# eventid
# CustomEventidIndex

# inserted automatically
import os
import marshal

import struct
import shutil

from hashlib import md5

# custom db code start
# db_custom


# custom index code start
# ind_custom


# source of classes in index.classes_code
# classes_code


# index code start

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

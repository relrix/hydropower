#import client
#import time

#for c in range (1, 3):
#	response = client.socket_get_dict_response(22000, "aAAAHA")
#	print response
	#time.sleep(.1)




#!/usr/bin/env python

#!/usr/bin/env python
from __future__ import print_function
 
def fibonacci(cb):
    values = []
    while(True):
        if len(values) < 2:
            values.append(1)
        else:
            values = [values[-1], values[-1] + values[-2]]
 
        r = cb(values[-1])
        if (r[0]):
            return(r[1])
 
def check_17(v):
    if v % 17 == 0:
        return (True, v)
 
    if v > 10000:
        return (True, None)
 
    return (False,)
 
 
if __name__ == '__main__':
    res = fibonacci(check_17)
    if (res != None):
        print(res)

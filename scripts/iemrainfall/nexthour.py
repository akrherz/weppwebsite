"""Make life easier?"""

from __future__ import print_function

import datetime
import sys

yyyy = int(sys.argv[1])
mm = int(sys.argv[2])
dd = int(sys.argv[3])
hr = int(sys.argv[4])

ts = datetime.datetime(yyyy, mm, dd, hr)
t = ts + datetime.timedelta(hours=+1)

print(t.strftime("%Y%m%d%H"))

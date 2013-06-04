
import mx.DateTime, sys

yyyy = int(sys.argv[1])
mm = int(sys.argv[2])
dd = int(sys.argv[3])
hr = int(sys.argv[4])

ts = mx.DateTime.DateTime(yyyy,mm,dd,hr)
t = ts + mx.DateTime.RelativeDateTime(hours=+1)

print t.strftime("%Y%m%d%H")


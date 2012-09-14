import mx.DateTime
import subprocess

sts = mx.DateTime.DateTime(2008,1,1)
ets = mx.DateTime.DateTime(2009,1,1)
interval = mx.DateTime.RelativeDateTime(days=1)

now = sts
while now < ets:
    url = now.strftime("http://mesonet.agron.iastate.edu/cgi-bin/wepp/idep2shape.py?year=%Y&month=%m&day=%d")
    cmd = "wget -q -O %s '%s'" % (now.strftime("%Y%m%d_idep.zip"), url)
    subprocess.call(cmd, shell=True)
    now += interval
#!/usr/bin/env python

import mx.DateTime
from PIL import Image, ImageDraw, ImageFont

sts = mx.DateTime.DateTime(2007, 8, 1)
ets = mx.DateTime.DateTime(2007, 9, 1)
font = ImageFont.truetype("Vera.ttf", 22)

yheader = 44
out = Image.new("RGB", (7 * 320, 6 * 240 + yheader))
draw = ImageDraw.Draw(out)
# draw.rectangle( [280,220,360,260], fill="#000000" )
# now = mx.DateTime.now()
# str = now.strftime("%I:%M")
draw.text((1120, 1), "March 2007", font=font)
draw.text((160, 20), "SUN", font=font)
draw.text((480, 20), "MON", font=font)
draw.text((800, 20), "TUE", font=font)
draw.text((1120, 20), "WED", font=font)
draw.text((1440, 20), "THU", font=font)
draw.text((1760, 20), "FRI", font=font)
draw.text((2080, 20), "SAT", font=font)


interval = mx.DateTime.RelativeDateTime(days=+1)
now = sts
(isoyear, startweek, isoday) = now.iso_week

dayxref = [0, 1, 2, 3, 4, 5, 6, 0]
weekxref = [0, 0, 0, 0, 0, 0, 0, 1]
startweek += weekxref[isoday]

while now < ets:
    print(now)
    (isoyear, isoweek, isoday) = now.iso_week

    i0 = Image.open("%s_daily_rainfall_in.png" % (now.strftime("%Y/%m/%d"),))
    x = 320 * (dayxref[isoday])
    y = 240 * (isoweek + weekxref[isoday] - startweek) + yheader
    out.paste(i0, (x, y))
    now += interval

out.save("test.jpg")
del out

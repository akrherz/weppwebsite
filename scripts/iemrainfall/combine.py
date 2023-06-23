"""Combine"""
import datetime
import os
import sys

BASEDIR = "/mnt/idep/data/rainfall/product"
TMP = "tmp"


def main(argv):
    """Go Main Go"""
    yyyy = int(argv[1])
    mm = int(argv[2])
    dd = int(argv[3])
    hr = int(argv[4])

    ts = datetime.datetime(yyyy, mm, dd, hr)

    rads = ""
    prods = ""
    for mi in [15, 30, 45, 60]:
        tstamp = ts + datetime.timedelta(minutes=mi)
        fp = "%s/HRAP_RAIN_%s" % (TMP, mi)
        rads += "%s\n" % (fp,)

        ofp = ("%s/%s/%s/IA%s.dat") % (
            BASEDIR,
            tstamp.year,
            tstamp.strftime("%Y%m%d"),
            tstamp.strftime("%Y%m%d_%H%M"),
        )
        if not os.path.isdir(
            "%s/%s/%s" % (BASEDIR, tstamp.year, tstamp.strftime("%Y%m%d"))
        ):
            os.makedirs(
                "%s/%s/%s" % (BASEDIR, tstamp.year, tstamp.strftime("%Y%m%d"))
            )
        prods += "%s\n" % (ofp,)

    hts = ts + datetime.timedelta(hours=+1)

    fp = open("%s/S4_files.dat" % (TMP,), "w")
    fp.write("%s/%s\n" % (TMP, hts.strftime("S4_%Y%m%d%H")))
    fp.close()

    fp = open("%s/combout.dat" % (TMP,), "w")
    fp.write(prods)
    fp.close()

    fp = open("%s/NEX_files.dat" % (TMP,), "w")
    fp.write(rads)
    fp.close()

    os.system("bin/combine")


if __name__ == "__main__":
    main(sys.argv)

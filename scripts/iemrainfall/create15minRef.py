"""Do Things"""

import datetime
import os
import shutil
import sys

TMP = "tmp"


def main(argv):
    """Go Main Go"""
    if len(argv) != 6:
        print("Usage: python create15minRef.py RAD YYYY MM DD HR")
        return

    rad = argv[1]
    yyyy = int(argv[2])
    mm = int(argv[3])
    dd = int(argv[4])
    hr = int(argv[5])

    ts = datetime.datetime(yyyy, mm, dd, hr)

    files = {0: "", 1: "", 2: "", 3: ""}
    fcnt = {0: 0, 1: 0, 2: 0, 3: 0}
    fbin = {0: 15, 1: 30, 2: 45, 3: 60}
    # We look for radar data files, if found, we add them to dicts
    if yyyy >= 2002:
        for mi in range(60):
            mybin = int(mi / 15)
            tstamp = ts + datetime.timedelta(minutes=mi)
            fp = "%s/%s_NCR_%s.ras" % (
                TMP,
                rad,
                tstamp.strftime("%Y%m%d_%H%M"),
            )
            if os.path.isfile(fp):
                files[mybin] += "%s\n" % (fp,)
                fcnt[mybin] += 1

    for k in fbin:
        fn = "%s/%s_%s.files15" % (TMP, rad, fbin[k])
        fp = open(fn, "w")
        fp.write(files[k])
        fp.close()
        os.system(
            "bin/create15minutes %s %i > %s/junk.dat" % (fn, fcnt[k], TMP)
        )
        if not os.path.isfile("SDUS53_RAIN.txt"):
            print("%s %s" % (rad, fbin[k]))
        shutil.copy(
            "SDUS53_RAIN.txt", "%s/%s_RAIN_%s.dat" % (TMP, rad, fbin[k])
        )
        os.remove("SDUS53_RAIN.txt")

        if not os.path.isfile("%s/HRAP_RAIN_%s" % (TMP, fbin[k])):
            shutil.copy("lib/empty.hrap", "%s/HRAP_RAIN_%s" % (TMP, fbin[k]))
        os.system(
            ("bin/createHRAP lib/K%s.txt %s/%s_RAIN_%s.dat %s/HRAP_RAIN_%s")
            % (rad, TMP, rad, fbin[k], TMP, fbin[k])
        )


if __name__ == "__main__":
    main(sys.argv)

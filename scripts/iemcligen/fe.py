import os

import pandas as pd
from tqdm import tqdm

for date in tqdm(pd.date_range("2019/09/03", "2020/10/12")):
    cmd = date.strftime("python grids2shp.py %Y %m %d")
    os.system(cmd)

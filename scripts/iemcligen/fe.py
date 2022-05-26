import os

from tqdm import tqdm
import pandas as pd

for date in tqdm(pd.date_range("2019/09/03", "2020/10/12")):
    cmd = date.strftime("python grids2shp.py %Y %m %d")
    os.system(cmd)

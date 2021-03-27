'''
Script to deelop and test code
S. Filhol

TODO:
- create netcdf file, Finish
- figure if netcdf compression possible: Library to compress netcdf: https://github.com/coecms/nccompress


'''

import pandas as pd
import xarray as xr
from laspy.file import File
import numpy as np
import matplotlib.pyplot as plt

mylas = File('/home/arcticsnow/github/SnowyOwl/data/2021.03.15T11-10-00.bin.las', mode='r')

df = pd.DataFrame({'x':mylas.x, 'y':mylas.y, 'z':mylas.z, 'intensity':mylas.intensity, 'gps_time':mylas.gps_time, 'return_num':mylas.return_num})

xstart = -5
xend = 5
dx = 0.1
ystart = -20
yend = 5
dy = 0.1

nx = int((xend - xstart)/dx)
ny = int((yend - ystart)/dy)

bins_x = np.linspace(xstart, xend, nx + 1)
x_cuts = pd.cut(df.x, bins_x, labels=False)
bins_y = np.linspace(ystart, yend, ny + 1)
y_cuts = pd.cut(df.y, bins_y, labels=False)
bin_xmin, bin_ymin = x_cuts.min(), y_cuts.min()
print('Data cut in a ' + str(bins_x.__len__()) + ' by ' + str(bins_y.__len__()) + ' matrix')

print('dx = ' + str(dx) + ' ; dy = ' + str(dy))
grouped = df.groupby([x_cuts, y_cuts])


def pad_with_nan(val, bins_x, bins_y):
    arr = np.empty([bins_y.shape[0],bins_x.shape[0]])*np.nan
    arr[np.ix_(val.index.astype(int),val.columns.astype(int))] = val
    return arr

test=pad_with_nan( grouped.z.count().unstack().T, bins_x=bins_x, bins_y=bins_y)

ds = xr.Dataset(
    {
        "pts_count":(["x", "y", "time"], pad_with_nan( grouped.z.count().unstack().T, bins_x=bins_x, bins_y=bins_y)),
        "z_min": (["x", "y", "time"], grouped.z.min().unstack().T),
        "z_5": (["x", "y", "time"], grouped.z.quantile(0.05).unstack().T),
        "z_10": (["x", "y", "time"], grouped.z.quantile(0.1).unstack().T),
        "z_25": (["x", "y", "time"], grouped.z.quantile(0.25).unstack().T),
        "z_50": (["x", "y", "time"], grouped.z.quantile(0.50).unstack().T),
        "z_75": (["x", "y", "time"], grouped.z.quantile(0.75).unstack().T),
        "z_max": (["x", "y", "time"], grouped.z.max().unstack().T),
        "z_std": (["x", "y", "time"], grouped.z.std().unstack().T),
        "intensity_min": (["x", "y", "time"], grouped.intensity.min().unstack().T),
        "intensity_max": (["x", "y", "time"], grouped.intensity.max().unstack().T),
        "intensity_mean": (["x", "y", "time"], grouped.intensity.mean().unstack().T),
        "intensity_median": (["x", "y", "time"], grouped.intensity.median().unstack().T),
        "intensity_std": (["x", "y", "time"], grouped.intensity.std().unstack().T),
    },
coords={
        "lon": (["x", "y"], lon),
        "lat": (["x", "y"], lat),
        "time": pd.date_range("2014-09-06", periods=3),
        "reference_time": pd.Timestamp("2014-09-05"),
    },
)
ds.attrs = {'title':'Forcing for SURFEX crocus',
                'source': 'data from AROME MEPS, ready for CROCUS forcing',
                'creator_name':'Simon Filhol',
                'creator_email':'simon.filhol@geo.uio.no',
                'creator_url':'https://www.mn.uio.no/geo/english/people/aca/geohyd/simonfi/index.html',
                'institution': 'Department of Geosciences, University of Oslo, Norway',
                'date_created': dt.datetime.now().strftime('%Y/%m/%d %H:%M:%S')}
ds.to_netcdf("saved_on_disk.nc")




#====== test zone

plt.figure()
plt.imshow(arr, vmin=10, vmax=60)
plt.colorbar()

samp = np.linspace(0, df.shape[0],9999).astype(int)[:-2]
plt.figure()
plt.scatter(df.x.iloc[samp], df.y.iloc[samp], c= df.z.iloc[samp], vmin=-9.5, vmax=-9)

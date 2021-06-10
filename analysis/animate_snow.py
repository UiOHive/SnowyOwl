
'''
Script to compute a movie directly from a list of netcdf from the SnowyOwl lidar.
S. Filhol, June 2021

TODO:
- add wind arrow (get data from DB)
- add timestamp
- add colorbar
- add option for video output resolution
- check that all netcdf have same size
- add hillshade option
- automate retrivel of data from DB based on timestamp from netcdf file

'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import xarray as xr
import numpy as np
import datetime
from wsn_client import query

# %%
start = datetime.datetime(2021,4,7,9)
end = datetime.datetime(2021,4,13,6)

varoi =  ['METNOS_99_99_1_1_1', 'WD_20_35_1_1_1', 'WS_16_33_1_1_1']

df = query.query('clickhouse', serial=3668, table='finseflux_Biomet',limit=10000000,fields=varoi, time__gte=start, time_lte=end)


# %%
path_to_data = '../data/202104/*nc'
ds = xr.open_mfdataset(path_to_data)
# compute snow depth in respect to first scan
sd=(ds['min'] - ds['min'].isel(time=0))
msd = np.array(sd)
# exclude any snowdepth above 1m (assumed to be error/noise)
msd[msd[:,:,:]>1]=np.nan


fps = 5
nSeconds = int(msd.shape[0]/fps)
snapshots = msd

# First set up the figure, the axis, and the plot element we want to animate
fig = plt.figure( figsize=(8,8) )


a = snapshots[0,:,:]
dx, dy = 0.2, 0.2
#vmax = np.nanpercentile(msd,80, axis=(1,2))
im = plt.imshow(a, interpolation='none', aspect='equal', vmin=-0.05, vmax=0.3, cmap=plt.cm.Blues, extent=[sd.x.min(), sd.x.max(), sd.y.min(), sd.y.max()])
plt.grid(linestyle=':')

def animate_func(i):

    # show progress
    if i % fps == 0:
        print( '.', end ='' )

    im.set_array(snapshots[i])
    
    #im.set_clim(vmax=0.3)
    return [im]

anim = animation.FuncAnimation(
                               fig, 
                               animate_func, 
                               frames = nSeconds * fps,
                               interval = 1000 / fps, # in ms
                               )

anim.save('test_anim_bis.mp4', fps=fps, extra_args=['-vcodec', 'libx264'])

print('Done!')

'''
Script to compute a movie directly from a list of netcdf from the SnowyOwl lidar.
S. Filhol, June 2021

TODO:
- add option to select date range, and process by chunks to create the png files
- adjust vmin and vmax to see change over time
- check that all netcdf have same size
- add hillshade option
- automate retrivel of data from DB based on timestamp from netcdf file

- Create a second set of subplots
- create another animation that includes extra plots like the snowdepth plots with a dot moving along
- add meteo panel (temp, precip geonor, flowcapt)
- add the snow surface age


- to be considered: add panel with wind graph
'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import xarray as xr
import numpy as np
import datetime, getpass, glob
from wsn_client import query
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from tqdm import tqdm


# %%
met_from_db = False
met_from_file = True

file_meteo = 'data/scan_meteo.pckl'
dir_netcdf = '/media/' + getpass.getuser() + '/My Book/SO_spring_2021_processing/netcdf/'
netlist = glob.glob(dir_netcdf+'*.nc')
netlist.sort()

netdf = pd.DataFrame()
netdf['fname'] = netlist
netdf['date'] = netdf.fname.apply(lambda x: pd.datetime.strptime(x.split('/')[-1], '%Y%m%d.nc'))

start = netdf.date.iloc[0]
end = netdf.date.iloc[-1]
print('Starting date: ', start.strftime('%Y-%b-%d'))
print('Ending date: ', end.strftime('%Y-%b-%d'))

# import reference ground scan


if met_from_db:
    # Get Met data from Finse DB 
    varoi =  ['METNOS_99_99_1_1_1', 'WD_20_35_1_1_1', 'WS_16_33_1_1_1']
    df = query.query('clickhouse', serial=3668, table='finseflux_Biomet', limit=10000000, fields=varoi, time__gte=start, time_lte=end)
    df_hr = df.resample('60min').mean()
    df_hr = wswd_2_uv(df_hr, ws='ws_mean', wd='wd_mean')
    
elif met_from_file:
    df = pd.read_pickle(file_meteo)
    
# process each netcdf file independently
for netfile in netlist:
    ds = xr.open_dataset(netfile)

    
    
    
# compute snow depth in respect to first scan
sd=(ds['min'] - ds['min'].isel(time=0))
msd = np.array(sd)
# exclude any snowdepth above 1m (assumed to be error/noise)
msd[msd[:,:,:]>1]=np.nan
tst = pd.to_datetime(sd.time.values)


#%%


dx, dy = 0.2, 0.2
#vmax = np.nanpercentile(msd,80, axis=(1,2))
wd =  'wd_mean'

# Video parameters:
dpi = 96
framerate = 24
pix_width = 1920
pix_height = 1080
padding_zeros = 5  # image filename padding with zeros
fname_video = 'test.mp4'
cmap = plt.cm.Blues_r



nb_frame = 500
#nb_frame = msd.shape[0]

for i in tqdm(range(0, nb_frame)):
    fig, ax = plt.subplots(1,1,figsize=(pix_width/dpi, pix_height/dpi), dpi=dpi)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('bottom', size='5%', pad=0.35)

    im = ax.imshow(msd[i,:,:], interpolation='none', aspect='equal', vmin=-0.05, vmax=0.3, cmap=cmap, extent=[sd.x.min(), sd.x.max(), sd.y.min(), sd.y.max()])
    ax.arrow(2.5,0,df.V_mean.iloc[i]/10, -df.U_mean.iloc[i]/10, width=0.1)
    ax.text(0,-3,df.index[i].strftime("%b %-d, %-H:%M"))
    ax.text(0,-3.5,'Avg Wind Speed = ' + np.round(df[wd].iloc[i],2).astype(str) + ' m/s')
    fig.colorbar(im, cax=cax, orientation='horizontal', extend='both', label='Snow depth [m]')
    ax.grid(linestyle=':')

    filename='./anim/'+str(i).zfill(padding_zeros)+'.png'
    fig.savefig(filename, dpi=dpi)
    plt.close(fig)


cmd = "ffmpeg -r {} -f image2 -s {}x{} -i %{}d.png -vcodec libx264 -crf 25  -pix_fmt yuv420p {}".format(framerate,pix_width, pix_height, str(padding_zeros).zfill(2), fname_video)
print('--')
print(cmd)

print('Done!')
#%%

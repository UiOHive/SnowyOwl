
'''
Script to compute a movie directly from a list of netcdf from the SnowyOwl lidar.
S. Filhol, June 2021

TODO:
- check that all netcdf have same size
- add hillshade option
- automate retrivel of data from DB based on timestamp from netcdf file

- Create a second set of subplots
- create another animation that includes extra plots like the snowdepth plots with a dot moving along
- add meteo panel (temp, precip geonor, flowcapt)
- add the snow surface age

'''
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import xarray as xr
import numpy as np
import datetime
from wsn_client import query
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable
from tqdm import tqdm

def wswd_2_uv(df, ws='WS_16_33_1_1_1', wd='WD_20_35_1_1_1'):
    """
    Foinction to convert wind speed and direction to UV component

    :param df: [description], [type]
    :param ws: [description], defaults to 'WS_16_33_1_1_1',  str, optional
    :param wd: [description], defaults to 'WD_20_35_1_1_1',  str, optional
    :return: [description], [type]
    """    
    df[wd].loc[df[wd]<0] = df[wd].loc[df[wd]<0] + 360
    df['U'] = df[ws] * np.cos(270-df[wd]*np.pi/180)
    df['V'] = df[ws] * np.sin(270-df[wd]*np.pi/180)
    return df

# %%
# Get Met data from Finse DB 
start = datetime.datetime(2021,4,7,9)
end = datetime.datetime(2021,4,13,6)

varoi =  ['METNOS_99_99_1_1_1', 'WD_20_35_1_1_1', 'WS_16_33_1_1_1']

df = query.query('clickhouse', serial=3668, table='finseflux_Biomet',limit=10000000,fields=varoi, time__gte=start, time_lte=end)
df_hr = df.resample('60min').mean()
df_hr = wswd_2_uv(df_hr)


# %%

path_to_data = '../data/202104/*nc'
ds = xr.open_mfdataset(path_to_data)
# compute snow depth in respect to first scan
sd=(ds['min'] - ds['min'].isel(time=0))
msd = np.array(sd)
# exclude any snowdepth above 1m (assumed to be error/noise)
msd[msd[:,:,:]>1]=np.nan
tst = pd.to_datetime(sd.time.values)

df_hr = df_hr.loc[tst]


#%%


dx, dy = 0.2, 0.2
#vmax = np.nanpercentile(msd,80, axis=(1,2))
wd =  'WS_16_33_1_1_1'

# Video parameters:
dpi = 96
framerate = 5
pix_width = 1920
pix_height = 1080
padding_zeros = 5  # image filename padding with zeros
fname_video = 'test.mp4'
cmap = plt.cm.Blues_r


for i in tqdm(range(0, msd.shape[0])):
    fig, ax = plt.subplots(1,1,figsize=(pix_width/dpi, pix_height/dpi), dpi=dpi)
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('bottom', size='5%', pad=0.35)

    im = ax.imshow(msd[i,:,:], interpolation='none', aspect='equal', vmin=-0.05, vmax=0.3, cmap=cmap, extent=[sd.x.min(), sd.x.max(), sd.y.min(), sd.y.max()])
    ax.arrow(2.5,0,df_hr.V.iloc[i]/10, -df_hr.U.iloc[i]/10, width=0.1)
    ax.text(0,-3,df_hr.index[i].strftime("%b %-d, %-H:%M"))
    ax.text(0,-3.5,'Avg Wind Speed = ' + np.round(df_hr[wd].iloc[i],2).astype(str) + ' m/s')
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

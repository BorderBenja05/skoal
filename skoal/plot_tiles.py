
import astropy.io.fits as fits
import healpy as hp
import numpy as np
from astropy.coordinates import SkyCoord
from astropy.io import fits
from astropy import units as u
import ligo.skymap.plot
from matplotlib import pyplot as plt
import mocpy
from astropy.table import Table



def make_tile_plots(filename, moc_tess, probs):
    """
    Function to plot the tiles
    """

    plot_name = 'figure3.png'

    with fits.open(filename) as hdulist:
        hdu = hdulist[1].data
    columns = [col.name for col in hdu.columns]

    fig = plt.figure(figsize=(8, 6), dpi=100)

    args = {"projection": 'astro mollweide'}
    ax = plt.axes([0.05, 0.05, 0.9, 0.9], **args)
    ax.imshow_hpx(hdu, field=columns.index("PROBDENSITY"), cmap="cylon")


    alphas = np.array(probs) / np.max(probs)

    for moc in moc_tess:
        moc.fill(
            ax=ax,
            wcs=ax.wcs,
            alpha=alphas[ii],
            fill=True,
            color="black",
            linewidth=1,
        )
        moc.border(ax=ax, wcs=ax.wcs, alpha=1, color="black")


    plt.savefig(plot_name, dpi=200)
    plt.close()

def plotter(moc_tess, filename):
    # URL for the skymap FITS file
    # url = 'https://gracedb.ligo.org/api/superevents/S240716b/files/bayestar.multiorder.fits,0'
    # Center coordinate
    # hp.read_map("/home/borderbenja/skoal/skoal/data/skymaps/cwb.multiorder.fits,1")
    # nside = hp.npix2nside(len(map_data))
    # print(f"NSIDE: {nside}, Number of Pixels: {len(map_data)}")
    # Create the figure and axes
    filename = '/home/borderbenja/skoal/skoal/data/skymaps/MS240324c_3_bayestar.multiorder.fits'
    


    fig = plt.figure(figsize=(8, 8), dpi=100)
    ax = plt.axes([0.05, 0.05, 0.9, 0.9], projection='astro mollweide')
    with fits.open(filename, mode='readonly') as hdulist:
    # print(hdulist[1].data)
    # Extract the probability column from the first table extension
        hdu = hdulist[1]
        print(hdu.header.get('NSIDE', None))


        ax.imshow_hpx(hdu, cmap='cylon')
    # Customize the inset axis

    ax.grid()


    # Display the skymap



    # Plot the MOC on the main and inset axes
    for moc in moc_tess:
        # ax.plot_moc(moc, edgecolor='red', lw=1, alpha=0.2)
        moc.border(ax=ax, wcs=ax.wcs, alpha=0.5, fill=True, color="green")

        

    plt.savefig('figure3.png', dpi=200)

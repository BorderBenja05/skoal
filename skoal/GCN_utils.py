import xml.etree.ElementTree as ET
import os
from urllib.parse import urlparse
import astropy.units as u
from astropy.coordinates import SkyCoord
import astropy_healpix as ah
from astropy.table import QTable
import numpy as np
import requests
from pathlib import Path
from ligo.gracedb.rest import GraceDb
import lxml.etree


def area(total_probability, bayestar_file):
    skymap = QTable.read(bayestar_file)
    skymap.sort('PROBDENSITY', reverse=True)
    level = ah.uniq_to_level_ipix(skymap['UNIQ'])
    pixel_area = ah.nside_to_pixel_area(ah.level_to_nside(level))
    prob = pixel_area * skymap['PROBDENSITY']
    cumprob = np.cumsum(prob)
    i = cumprob.searchsorted(total_probability)
    area_90 = pixel_area[:i].sum()
    area=area_90.to_value(u.deg**2)
    print(area)
    return area

def download_from_url(skymap_url: str, output_dir: Path, skymap_name: str) -> Path:
    """
    Download a skymap from a URL

    :param skymap_url: URL to download from
    :param output_dir: Output directory
    :param skymap_name: Name of skymap
    :return: Path to downloaded skymap
    """
    output_dir = Path(output_dir)
    savepath = output_dir.joinpath(skymap_name)

    if savepath.exists():
        print(f"File {savepath} already exists. Using this.")
    else:
        print(f"Saving to: {savepath}")
        response = requests.get(skymap_url, headers={"User-Agent": "Mozilla/5.0"})

        with open(savepath, "wb") as f:
            f.write(response.content)

    return savepath


def get_skymap_gracedb(
    event_name: str, rev=None, output_dir: Path = 'SKYMAP_DIR'
) -> Path:
    """
    Fetches the skymap from GraceDB

    :param event_name: name of the event
    :param rev: revision number of the event
    :param output_dir: directory to save the skymap and event info
    :return: path to the skymap
    """
    ligo_client = GraceDb()

    voevents = ligo_client.voevents(event_name).json()["voevents"]

    if rev is None:
        rev = len(voevents)

    elif rev > len(voevents):
        raise Exception(f"Revision {0} not found".format(rev))

    latest_voevent = voevents[rev - 1]
    print(f"Found voevent {latest_voevent['filename']}")

    if "Retraction" in latest_voevent["filename"]:
        raise ValueError(
            f"The specified LIGO event, "
            f"{latest_voevent['filename']}, was retracted."
        )

    response = requests.get(
        latest_voevent["links"]["file"],
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )

    root = lxml.etree.fromstring(response.content)
    params = {
        elem.attrib["name"]: elem.attrib["value"] for elem in root.iterfind(".//Param")
    }

    latest_skymap_url = params["skymap_fits"]

    print(f"Latest skymap URL: {latest_skymap_url}")

    skymap_name = "_".join(
        [event_name, str(latest_voevent["N"]), os.path.basename(latest_skymap_url)]
    )

    skymap_path = download_from_url(latest_skymap_url, output_dir, skymap_name)

    return skymap_path

    


def get_skymap(event_name: str, output_dir: Path = 'SKYMAP_DIR', rev: int = None) -> Path:
    """
    Fetches the event info and skymap from GraceDB

    :param event_name: name of the event
    :param output_dir: directory to save the skymap and event info
    :param rev: revision number of the event
    :return: path to the skymap
    """

    # if Path(event_name).exists():
    #     savepath = Path(event_name)
    # elif output_dir.joinpath(event_name).exists():
    #     savepath = output_dir.joinpath(event_name)
    # elif event_name[:8] == "https://":
    #     savepath = download_from_url(
    #         event_name, output_dir, os.path.basename(event_name)
    #     )
    # else:
    savepath = get_skymap_gracedb(event_name, output_dir=output_dir, rev=rev)

    return savepath



def get_ivorn(xml_file_path):
    try:
        try:
            tree = ET.parse(xml_file_path)
        except:
            print('file not found')
            exit()
        root = tree.getroot()
        ivorn = root.attrib['ivorn']
        # Extracting from the 3rd '/' to the '#' character
        return ivorn.split('/')[3].split('#')[0]
    except Exception as e:
        print("Error:", e)
        return None
    


    
def getEvent(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find the skymap_fits parameter within the GW_SKYMAP group
    event = root.find(".//Param[@name='GraceID']").attrib.get('value')
    
    return event

# Description:
#Grabs the GW skymap URL from VOEvent files




def getFERMICoordinates(file_path):
    # Parse the XML file
    tree = ET.parse(file_path)

    # Find the C1, C2, and Error2Radius elements
    c1_element = tree.find(".//C1")
    c2_element = tree.find(".//C2")
    error_radius_element = tree.find(".//Error2Radius")

    if c1_element is not None and c2_element is not None and error_radius_element is not None:
        # Extract RA (C1), Dec (C2), and error radius values
        ra = float(c1_element.text)
        dec = float(c2_element.text)
        error_radius = float(error_radius_element.text)
        return ra, dec, error_radius
    else:
        raise ValueError("<C1>, <C2>, or <Error2Radius> element not found in the XML.")
# Description:
#Grabs FK5 coordinates and error radius from GMB VOEvent.xml files


def decdeg2hms(decimal_degrees):
    mult = -1 if decimal_degrees < 0 else 1
    mnt,sec = divmod(abs(decimal_degrees)*3600, 60)
    deg,mnt = divmod(mnt, 60)
    
    return mult*deg, mult*mnt, mult*sec

# Description:
#Changes decimal degrees to degree, minute, second


def Fermi_fileWrite(output_file_path, radec, fields):
    try:
        with open(output_file_path, 'w') as file:
            i=0
            for row in radec:
                file.write(f"{fields[i]},{row[0]},{row[1]},1\n")
                i+=1
        print(f"Schedule successfully written to {output_file_path}")
    except Exception as e:
        print(f"Error occurred while writing to file: {e}")

# Description:
#makes schedule file for FERMI notices
import xml.etree.ElementTree as ET
import os
from urllib.parse import urlparse
import astropy.units as u
from astropy.coordinates import SkyCoord


def getEvent(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    # Find the skymap_fits parameter within the GW_SKYMAP group
    event = root.find(".//Param[@name='GraceID']").attrib.get('value')
    
    return event

# Description:
#Grabs the GW skymap URL from VOEvent files


def getGALCoordinates(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    CoordsGroup = root.find(".//Group[@name='Obs_Support_Info']")

    gal_Lon_degrees = CoordsGroup.find(".//Param[@name='Galactic_Long']")
    gal_Lat_degrees = CoordsGroup.find(".//Param[@name='Galactic_Lat']")
    
    return gal_Lat_degrees, gal_Lon_degrees

# Description:
#Grabs the galactic coordinates from GMB VOEvent.xml files

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

def galactic_2_icrs(Gal, GalDec):
    galactic_coords = SkyCoord(Gal=Gal*u.degree, GalDec=GalDec*u.degree, frame='galactic')
    equatorial_coords = galactic_coords.transform_to('icrs')
    ra_dec = (equatorial_coords.ra.degree, equatorial_coords.dec.degree)
    
    return ra_dec

# Description:
#changes galactic coordinates to ICRS coordinates




from sklearn.neighbors import BallTree
import xml.etree.ElementTree as ET
from gcn_kafka import Consumer
import numpy as np
from pathlib import Path

wk_dir = Path(__file__).parent.absolute()


# please just use this coordinate changer as others, such as astropy's, do
# not take/return the correct format 
def spherical_to_cartesian(spherical_cartesian_coords):
    theta = np.radians(spherical_cartesian_coords[:, 0])
    phi = np.radians(spherical_cartesian_coords[:, 1] +90)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    cartesian_coords = np.column_stack((x, y, z))
    return cartesian_coords

def Fermi_handle(telescope,outpath, data):
        """! Handles the alert by using the site_controller class
        @param site_controller  The overall point of control for the site
        @param data             The data retrieved by catching the alert
        """

        print(f"Handling an Alert")

        # Parse the XML file
        tree = ET.fromstring(data.value())

        # Find the C1, C2, and Error2Radius elements
        error_buff = (((3.25^2) + (2.07^2))^(1/2))/2

        try:
            ra = float(tree.find(".//C1").text)
            dec = float(tree.find(".//C2").text)
            error = float(tree.find(".//Error2Radius").text) + error_buff
        except:
            raise ValueError("ra, dec, or error element not found in the XML.")
    
        #get everything in radians
        ra = np.radians(ra)
        dec= np.radians(dec+90)
        center = [[np.sin(dec) * np.cos(ra),np.sin(dec) * np.sin(ra),np.cos(dec)]]
        #get cartesian error radius
        r = 2*np.sin(np.radians(error)/2)
        
        # Read the file and extract the second and third columns
        data = np.loadtxt(f'data/tesselations/{telescope}.tess', usecols=(1, 2))
        # Create BallTree
        Tree = BallTree(spherical_to_cartesian(data), leaf_size=40)

        field_ids = list(Tree.query_radius(center, r=r,sort_results=True,return_distance=True)[0][0])
        pointers = [list(data[index]) for index in field_ids]

        # Write targets to file
        with open(wk_dir.parent[2] / outpath, 'w') as file:
            for field, pointer in zip(field_ids, pointers):
                file.write(f"{field},{pointer[0]},{pointer[1]},1\n")

import numpy as np
import math
from sklearn.neighbors import BallTree
from astropy.table import Table
import xml.etree.ElementTree as ET

def round_list(list,decimal_place = 5):
    rounded_list = []
    for i in list:
        rounded_i = np.round(i ,decimal_place)
        rounded_list.append(rounded_i)
    return rounded_list

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

def Generate_fermi_pointers(tessfile, error_rad, ra, dec):

    # Read the file and extract the second and third columns
    data = np.loadtxt(tessfile, usecols=(1, 2))
    #print(data)


    #get everything in radians
    ra = np.radians(ra)
    dec= np.radians(dec+90)
    center = [[np.sin(dec) * np.cos(ra),np.sin(dec) * np.sin(ra),np.cos(dec)]]
    #get cartesian error radius
    r = 2*np.sin(np.radians(error_rad)/2)

    cartesian_coords = spherical_to_cartesian(data)
    #print(cartesian_coords)

    Tree = BallTree(cartesian_coords, leaf_size=40)
    exposures = Tree.query_radius(center, r=r, count_only=True)
    field_ids = Tree.query_radius(center, r=r,sort_results=True,return_distance=True)
    field_ids = [item for sublist in field_ids for item in sublist]
    field_ids = field_ids[0].tolist()
    #print(f'{exposures} exposures')
    #print(field_ids)

    Pointers = [data[index] for index in field_ids]
    Pointers = [list(arr) for arr in Pointers]
    #print(Pointers)

    return Pointers




def write_pointings_to_xml(pointings, output_file):
    # Create table from pointings
    table = Table(rows=pointings, names=('grid_id', 'field_id', 'ra', 'dec', 'ra_width', 'dec_width', 'prob_sum', 'observ_time', 'airmass'), dtype=('int', 'int', 'float', 'float', 'float', 'float', 'float', 'float', 'float'))

    # Create VOEvent XML structure
    voe = ET.Element('voe:VOEvent', attrib={'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                                            'xmlns:voe': 'http://www.ivoa.net/xml/VOEvent/v2.0',
                                            'xsi:schemaLocation': 'http://www.ivoa.net/xml/VOEvent/v2.0 '
                                                                   'http://www.ivoa.net/xml/VOEvent/VOEvent-v2.0.xsd'})
    table_element = ET.SubElement(voe, 'Table', attrib={'name': 'data'})
    description = ET.SubElement(table_element, 'Description')
    description.text = 'The datas of GWAlert'
    
    fields = table.colnames
    for field_name in fields:
        field = ET.SubElement(table_element, 'Field', attrib={'dataType': 'float' if field_name != 'priority' else 'int',
                                                              'ucd': '' if field_name == 'priority' else f'pos.eq.{field_name}',
                                                              'name': field_name,
                                                              'unit': 'deg' if field_name.endswith('_width') else 'None'})
        field_desc_elem = ET.SubElement(field, 'Description')
        field_desc_elem.text = ''
    
    data = ET.SubElement(table_element, 'Data')
    for row in table:
        tr = ET.SubElement(data, 'TR')
        for val in row:
            td = ET.SubElement(tr, 'TD')
            td.text = str(val)
    
    # Write the XML to the output file
    tree = ET.ElementTree(voe)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

def read_telescope_footprint(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ra_width = float(root.find('ra_width').text)
    dec_height = float(root.find('dec_height').text)
    return ra_width, dec_height

# Example usage
center_ra = 15.0  # Center RA in radians
center_dec = 45.0  # Center Dec in radians (near the North celestial pole)
error_radius = 18  # Error radius in degrees
xml_file = "config.xml"
output_file='schedule.xml'

# Read telescope footprint from XML file
#telescope_width, telescope_height = read_telescope_footprint(xml_file)

# Generate telescope pointings and write to XML file
Pointers =Generate_fermi_pointers('RASA11.tess',15,0,-90)
write_pointings_to_xml(Pointers, output_file)
print(f"Telescope pointings written to {output_file}.")

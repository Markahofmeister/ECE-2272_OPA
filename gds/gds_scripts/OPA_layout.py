import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
import cornerstone_pdk as cs_pdk # type: ignore
from gdsfactory.typings import ComponentSpec, CrossSectionSpec
import math

# DESIGN PARAMETERS
wavelength = 1.55                       # um    
numElements = 8                         # Number of radiating elements
separationScalar = 50                   # Should be ~1.2              
elementSeparation = wavelength * separationScalar    # Separation between radiating elements 
die_width = 3000.0                       # um
die_height = 3000.0                      # um
splitter_Xsep = 200                      # X separation between splitter stages, um
xMargin = 500                            # distance from x boundary to place elements, um

# Max. separation between outer radiating elementsa
ysepMax = elementSeparation * (numElements - 1)    

fa_pitch = 127.0                     # um

# Cornerstone rib cross section
xs = cs_pdk.cornerstone_rib()

# Cornerstone Library
gc = cs_pdk.gc_cornerstone_pdk()
fgc = cs_pdk.gc_focusing_cornerstone_pdk()
mmi1x2 = cs_pdk.mmi1x2_cornerstone_pdk()
mmi2x2 = cs_pdk.mmi2x2_cornerstone_pdk()
wgx = cs_pdk.crossing_cornerstone_pdk()












# top cell
top = gf.Component('TOP')

# floor plan
# This is the outline of the available space 
# ^^ It is on layer 99 because of it.
top << gf.components.rectangle(size=(die_width, die_height), centered=True, layer=(99,0))



re = gf.Component('Radiating Elements')

radiatingElements = list()

for i in range(numElements):

    # CHANGE TO GRATING COUPLERS
    radiatingElements.insert(i, re << gc)
    radiatingElements[i].movex( (die_width / 2) - xMargin)
    radiatingElements[i].movey( (ysepMax / 2) - (elementSeparation * i) )

# Add radiating elements to top
top << re


# Splitter
pdiv = gf.Component('Power Division')

# Number of required MMI splitter stages
numStages = round(np.log2(numElements))

# List of lists of MMI splitters
splitters = []

# Generate, place, and route N = log2(numElements) MMI splitters 
for stage in range( numStages ):

    temp_splitters = []

    divisor = 2**(stage + 1)

    # Generate and place MMI splitters for stage M 
    for i in range( round( numElements / divisor ) ):

        temp_splitters.insert(i, pdiv << mmi1x2)
        temp_splitters[i].movex( (die_width / 2) - xMargin - (splitter_Xsep * (stage + 1)) )
        temp_splitters[i].movey( (ysepMax / 2) - ((divisor-1) * (elementSeparation / 2)) - (elementSeparation * i * divisor) )

    # Add stage M of splitters to master MMI splitter list 
    splitters.append(temp_splitters)

    # If we are not on the stage that connects to the bragg gratings, 
    # draw the connections betweem gratings 
    if(stage != 0):
        rg = round( (numElements * 2) / divisor)
        for i in range( rg ):
            if(i % 2 == 0):
                gf.routing.route_single(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
            else:
                gf.routing.route_single(pdiv, port1=splitters[stage][int(i/2)].ports['o3'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
            

top << pdiv

for i in range(numElements):
    if(i % 2 == 0):
        gf.routing.route_single(top, port1=splitters[0][int(i/2)].ports['o2'], port2=radiatingElements[i].ports['o1'], cross_section=xs)
    else:
        gf.routing.route_single(top, port1=splitters[0][int(i/2)].ports['o3'], port2=radiatingElements[i].ports['o1'], cross_section=xs)



top.plot()
top.show()

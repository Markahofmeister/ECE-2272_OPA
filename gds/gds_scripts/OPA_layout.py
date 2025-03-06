import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
import cornerstone_pdk as cs_pdk # type: ignore
from gdsfactory.typings import ComponentSpec, CrossSectionSpec

# DESIGN PARAMETERS
wavelength = 1.55                       # um    
numElements = 8                         # Number of radiating elements
separationScalar = 100                   # Should be ~1.2              
elementSeparation = wavelength * separationScalar    # Separation between radiating elements 
die_width = 3000.0                       # um
die_height = 3000.0                      # um
splitter_Xsep = 0.200                      # X separation between splitter stages, um
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

radiatingElements = list() * numElements

for i in range(numElements):

    # CHANGE TO GRATING COUPLERS
    radiatingElements.insert(i, re << gc)
    radiatingElements[i].movex( (die_width / 2) - xMargin)
    radiatingElements[i].movey( (ysepMax / 2) - (elementSeparation * i) )

# Add radiating elements to top
top << re


# Splitter
c1 = gf.Component('Power Division')


# MMI1 
mmi1 = c1 << mmi1x2
mmi1.movex(200.)
mmi1.movey(100.)

# MMI2
mmi2 = c1 << mmi1x2
mmi2.movex(200.)
mmi2.movey(-100.)

# MMI3 
mmi3 = c1 << mmi1x2
mmi3.movex(200.)
mmi3.movey(300.)

# MMI4 
mmi3 = c1 << mmi1x2
mmi3.movex(200.)
mmi3.movey(-300.)

mmiIn = c1 << mmi1x2
mmiIn.movex(-(mmiIn.xmin+mmiIn.xmax)/2)

# gf.routing.route_single(c1, port1=mmiIn.ports['o2'], port2=mmi1.ports['o1'], cross_section=xs)
# gf.routing.route_single(c1, port1=mmiIn.ports['o3'], port2=mmi2.ports['o1'], cross_section=xs)


top << c1


gf.routing.route_single(top, port1=mmi1.ports['o2'], port2=radiatingElements[0].ports['o1'], cross_section=xs)
gf.routing.route_single(top, port1=mmi1.ports['o3'], port2=radiatingElements[1].ports['o1'], cross_section=xs)
gf.routing.route_single(top, port1=mmi2.ports['o2'], port2=radiatingElements[2].ports['o1'], cross_section=xs)
gf.routing.route_single(top, port1=mmi2.ports['o3'], port2=radiatingElements[3].ports['o1'], cross_section=xs)

top.plot()
top.show()

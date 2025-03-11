import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
import cornerstone_pdk as cs_pdk # type: ignore
from gdsfactory.typings import ComponentSpec, CrossSectionSpec
import math as m

# DESIGN PARAMETERS
wavelength = 1.55                       # um    
numElements = 16                         # Number of radiating elements
separationScalar = 7                   # Should be ~1.2              
elementSeparation = wavelength * separationScalar    # Separation between radiating elements 
die_width = 3000.0                       # um
die_height = 3000.0                      # um
splitter_Xsep = 150                      # X separation between splitter stages, um
xMargin = 500                            # distance from x boundary to place elements, um
yMargin = 200
bendRad_min = 10

# Max. separation between outer radiating elementsa
ysepMax = elementSeparation * (numElements - 1)    

fa_pitch = 127.0                     # um

# Create duplicate designs?
duplicate = True

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

OPA = gf.Component('OPA')

re = gf.Component('Radiating Elements')

radiatingElements = list()

for i in range(numElements):

    # CHANGE TO GRATING COUPLERS
    radiatingElements.insert(i, re << gc)
    radiatingElements[i].movex( (die_width / 2) - xMargin)
    radiatingElements[i].movey( (ysepMax / 2) - (elementSeparation * i) )

# Add radiating elements to top
OPA << re


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
    # if(stage != 0):
    #     rg = round( (numElements * 2) / divisor)
    #     for i in range( rg ):
    #         if(i % 2 == 0):
    #             gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
    #             # gf.routing.route_single(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs, radius=10.0,
    #             #                         steps=[{"dx": 20},
    #             #                                {"dy": 50},
    #             #                                {"dx": 40},
    #             #                                {"dy": -40},
    #             #                                {"dx": 20}
    #             #                                  ])
    #         else:
    #             gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o3'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)



splitterCurr1Port = splitters[1][0].ports['o2']
splitterCurr2Port = splitters[0][0].ports['o1']
splitterCurr1 = splitterCurr1Port.center
splitterCurr2 = splitterCurr2Port.center
print(splitterCurr1)
print(splitterCurr2)
dyDiff = splitterCurr2[1] - splitterCurr1[1]
offset = 30

gf.routing.route_single(pdiv, port1=splitters[1][int(0)].ports['o2'], port2=splitters[0][0].ports['o1'], cross_section=xs, radius=10.0,
                                    steps=[{"dx": 20},
                                           {"dy": dyDiff + offset},
                                           {"dx": 40},
                                           {"dy": -offset}
                                             ])

            

OPA << pdiv

# Route final splitter stage to radiating elements 
for i in range(numElements):
    if(i % 2 == 0):
        gf.routing.route_dubin(OPA, port1=splitters[0][int(i/2)].ports['o2'], port2=radiatingElements[i].ports['o1'], cross_section=xs)
    else:
        gf.routing.route_dubin(OPA, port1=splitters[0][int(i/2)].ports['o3'], port2=radiatingElements[i].ports['o1'], cross_section=xs)

# ports_1 = []
# ports_2 = []
# for i in range(numElements):
#     ports_1.append(radiatingElements[i].ports['o1'])
#     if(i % 2 == 0):
#         ports_2.append(splitters[0][int(i/2)].ports['o2'])
#     else:
#         ports_2.append(splitters[0][int(i/2)].ports['o3'])

# gf.routing.route_bundle_all_angle(top, ports1=ports_1, ports2=ports_2, cross_section=xs, bend=)

# Input Grating Coupler
gIn = gf.Component('gratingIn')

# Position Input Grating Coupler
gratingIn = gIn << fgc
mov = (die_width / 2) - xMargin - (splitter_Xsep * (numStages + 1) - (splitter_Xsep / 2))
gratingIn.rotate(180.0)
gratingIn.movex(mov)

# Add to top and route waveguide
OPA << gIn
gf.routing.route_single(OPA, port1=gratingIn.ports['o1'], port2=splitters[numStages - 1][0].ports['o1'], cross_section=xs)

# floor plan
# This is the outline of the available space 
# ^^ It is on layer 99 because of it.
top << gf.components.rectangle(size=(die_width, die_height), centered=True, layer=(99,0))

# Add OPA to top level cell
# top << OPA

dup = gf.Component('dup')

if(duplicate):

    deviceMargin = 150      # Buffer between device copies, um

    opaDimX = OPA.xsize
    opaDimY = OPA.ysize

    deviceYSizeBuff = opaDimY + deviceMargin
    numCopies = m.floor(((die_height - (yMargin * 2)) / deviceYSizeBuff) )
    # print(numCopies)

    for i in range(numCopies):
        topTemp = gf.Component("topTemp" + str(i))
        topTemp << OPA
        yPos = (die_height / 2) - ((deviceYSizeBuff) * (i + 1))
        topTemp.movey(yPos)
        # dup << topTemp
        top << topTemp
    

else:
    top << OPA

top.plot()
top.show()

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
splitter_Xsep = 130

deltaLSpacing = 10                        # um
xBuff = 20                               # Minimum straight leaving/entering port    

radiatorFeed_Xsep = (( (2 * xBuff) + ((numElements + 1) * deltaLSpacing) ) * 2 ) + 0                 # X separation between splitter stages, um
xMargin = 500                            # distance from x boundary to place elements, um
yMargin = 200
bendRad_min = 10

# Max. separation between outer radiating elementsa
ysepMax = elementSeparation * (numElements - 1)    

fa_pitch = 127.0                     # um

# Create duplicate designs?
duplicate = False

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
        if(stage == 0):
            temp_splitters[i].movex( (die_width / 2) - xMargin - (radiatorFeed_Xsep * (stage + 1)) )
        else:
             temp_splitters[i].movex( (die_width / 2) - xMargin - (splitter_Xsep * (stage)) - radiatorFeed_Xsep)
        temp_splitters[i].movey( (ysepMax / 2) - ((divisor-1) * (elementSeparation / 2)) - (elementSeparation * i * divisor) )

    # Add stage M of splitters to master MMI splitter list 
    splitters.append(temp_splitters)


    # If we are not on the stage that connects to the bragg gratings, 
    # draw the connections betweem gratings 
    if(stage != 0):
        rg = round( (numElements * 2) / divisor)
        for i in range( rg ):
            if(i % 2 == 0):
                gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)           
            else:
                gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o3'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
                

            

OPA << pdiv

# Route final splitter stage to radiating elements 

dxMaxDiff = radiatingElements[0].ports['o1'].center[0] - splitters[0][int(i/2)].ports['o2'].center[0]
yOffset = 30
gcPortInDiffY = radiatingElements[0].ports['o1'].center[1] - radiatingElements[1].ports['o1'].center[1]
mmiPortOutDiffY = splitters[0][0].ports['o2'].center[1] - splitters[0][0].ports['o3'].center[1]
elementYdiffOffset = gcPortInDiffY - mmiPortOutDiffY

deltaLScalar = 0.2

for i in range(numElements):    

    if(i % 2 == 0):

        xDist = dxMaxDiff - (xBuff * (i+1))
        yChange = yOffset + i*deltaLScalar

        splitterCurr = splitters[0][int(i/2)].ports['o2'].center
        radiatorCurr = radiatingElements[i].ports['o1'].center
        dyDiff = radiatorCurr[1] - splitterCurr[1]
        dxDiff = radiatorCurr[0] - splitterCurr[0]

        route = gf.routing.route_single(pdiv, port1=splitters[0][int(i/2)].ports['o2'], port2=radiatingElements[i].ports['o1'], cross_section=xs, radius=10.0,
                                        steps=[{"dx": (xBuff/2) * (i+1)},
                                            {"dy": dyDiff + yChange},
                                            {"dx":  xDist},
                                            {"dy": -yChange}
                                             ])

        # gf.routing.route_dubin(OPA, port1=splitters[0][int(i/2)].ports['o2'], port2=radiatingElements[i].ports['o1'], cross_section=xs)
    else:

        xDist = dxMaxDiff - (xBuff * (i+1))
        yChange = (yOffset + i*deltaLScalar) + (elementYdiffOffset / 2)

        splitterCurr = splitters[0][int(i/2)].ports['o3'].center
        radiatorCurr = radiatingElements[i].ports['o1'].center
        dyDiff = radiatorCurr[1] - splitterCurr[1]
        dxDiff = radiatorCurr[0] - splitterCurr[0]

        route = gf.routing.route_single(pdiv, port1=splitters[0][int(i/2)].ports['o3'], port2=radiatingElements[i].ports['o1'], cross_section=xs, radius=10.0,
                                        steps=[{"dx": (xBuff/2) * (i+1)},
                                               {"dy": dyDiff + yChange},
                                               {"dx": xDist},
                                               {"dy": -yChange}
                                                 ])
        
        # gf.routing.route_dubin(OPA, port1=splitters[0][int(i/2)].ports['o3'], port2=radiatingElements[i].ports['o1'], cross_section=xs)

    print(f"Total Route length for {i}: {route.length / 1000} um")
        

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
mov =  OPA.xmax  - OPA.xsize - 50
gratingIn.rotate(180.0)
gratingIn.movex(mov)

# Add to top and route waveguide
OPA << gIn
gf.routing.route_single(OPA, port1=gratingIn.ports['o1'], port2=splitters[numStages - 1][0].ports['o1'], cross_section=xs)


# Input Calibration Grating Coupler 
cIn = gf.Component('Calibrator Input')
calIn = cIn << fgc
cIn.rotate(180.0)
calIn.movex(gratingIn.ports['o1'].center[0])
calIn.movey(gratingIn.ports['o1'].center[1] + fa_pitch)

# Output Calibration Grating Coupler 
cOut = gf.Component('Calibrator Output')
calOut = cOut << fgc
cOut.rotate(180.0)
cOut.movex(gratingIn.ports['o1'].center[0])
cOut.movey(gratingIn.ports['o1'].center[1] - fa_pitch)

OPA << cIn
OPA << cOut

gf.routing.route_single(OPA, port1=calIn.ports['o1'], port2=calOut.ports['o1'], cross_section=xs, radius = 20.0,
                                                    steps=[{"dx": 30},
                                                    {"dy": -50},
                                                    {"dx":  -100},
                                                    {"dy":  -((fa_pitch * 2) - 100)},
                                                    {"dx":  100},
                                                    {"dy": -50}
                                                    ])


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

    pos = (radiatingElements[0].center[0], radiatingElements[0].ymax + 75)
    text = gf.components.texts.text(text = "CS GC, dL = 400 nm", size = 36, position = pos, layer=(100,0), justify="right")
    top << text

    top << OPA

top.plot()
top.show()

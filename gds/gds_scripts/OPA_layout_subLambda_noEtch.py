import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
import cornerstone_pdk as cs_pdk # type: ignore
from gdsfactory.typings import ComponentSpec, CrossSectionSpec
import math as m

# DESIGN PARAMETERS
wavelength = 1.56                       # um. Even for grid snapping.
numElements = 16                         # Number of radiating elements
separationScalar = 4                  # Should be ~1.2              
elementSeparation = wavelength * separationScalar    # Separation between radiating elements 
die_width = 3000.0                       # um
die_height = 3000.0                      # um
splitter_Xsep = 120                      # X separation between splitter stages, um
xMargin = 200                            # distance from x boundary to place elements, um
yMargin = 200
bendRad_min = 10

# Max. separation between outer radiating elementsa
ysepMax = elementSeparation * (numElements - 1)    

fa_pitch = 127.0                     # um

# Create duplicate designs?
duplicate = True


# DERIVED FROM Cornerstone grating coupler "SOI220nm_1550nm_TE_RIB_Grating_Coupler"
@gf.cell
def gc_cornerstone_pdk_subLambda_noEtch(width_grating: float = 1.55, period: float = 0.67, nPeriods: float = 60) -> gf.Component:

    l1 = l2 = period / 2
    gc = gf.components.dbr(w1 = 0.45, w2 = width_grating, l1 = l1, l2 = l2, n=nPeriods, cross_section='cornerstone_rib')

    return gc

numGCPeriods = 240

# Cornerstone rib cross section
xs = cs_pdk.cornerstone_rib()

# Cornerstone Library
fgc = cs_pdk.gc_focusing_cornerstone_pdk()
mmi1x2 = cs_pdk.mmi1x2_cornerstone_pdk()
mmi2x2 = cs_pdk.mmi2x2_cornerstone_pdk()
wgx = cs_pdk.crossing_cornerstone_pdk()


if(duplicate):     

     # top cell
    top = gf.Component('TOP')

    numCopies = 3

    gratingWidths = [1.0, 1.5, 2.0]
    gratingPeriods = [0.67] * numCopies

    for copy in range(numCopies):

        gc = gc_cornerstone_pdk_subLambda_noEtch(width_grating=gratingWidths[copy], period = gratingPeriods[copy], nPeriods=numGCPeriods)

        OPATemp = gf.Component("OPA_subL" + str(copy))

        re = gf.Component("Radiating Elements" + str(copy))

        radiatingElements = list()

        for i in range(numElements):

            radiatingElements.insert(i, re << gc)
            radiatingElements[i].movex( (die_width / 2) - xMargin)
            radiatingElements[i].movey( (ysepMax / 2) - (elementSeparation * i) )

        # Add radiating elements to top
        OPATemp << re


        # Splitter
        pdiv = gf.Component('Power Division' + str(copy))

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
                        gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
                    else:
                        gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o3'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
                    

        OPATemp << pdiv

        # Route final splitter stage to radiating elements 
        for j in range(numElements):
            
            if(j % 2 == 0):
                gf.routing.route_dubin(OPATemp, port1=splitters[0][int(j/2)].ports['o2'], port2=radiatingElements[j].ports['o1'], cross_section=xs)
            else:
                gf.routing.route_dubin(OPATemp, port1=splitters[0][int(j/2)].ports['o3'], port2=radiatingElements[j].ports['o1'], cross_section=xs)



        # Input Grating Coupler
        gIn = gf.Component('gratingIn' + str(copy))

        # Position Input Grating Coupler
        # Position Input Grating Coupler
        gratingIn = gIn << fgc
        mov =  OPATemp.xmax  - OPATemp.xsize - 50
        gratingIn.rotate(180.0)
        gratingIn.movex(mov)

        # Add to top and route waveguide
        OPATemp << gIn
        gf.routing.route_single(OPATemp, port1=gratingIn.ports['o1'], port2=splitters[numStages - 1][0].ports['o1'], cross_section=xs)

        # Input Calibration Grating Coupler 
        cIn = gf.Component('Calibrator Input' + str(copy))
        calIn = cIn << fgc
        cIn.rotate(180.0)
        calIn.movex(gratingIn.ports['o1'].center[0])
        calIn.movey(gratingIn.ports['o1'].center[1] + fa_pitch)

        # Output Calibration Grating Coupler 
        cOut = gf.Component('Calibrator Output' + str(copy))
        calOut = cOut << fgc
        cOut.rotate(180.0)
        cOut.movex(gratingIn.ports['o1'].center[0])
        cOut.movey(gratingIn.ports['o1'].center[1] - fa_pitch)

        OPATemp << cIn
        OPATemp << cOut

        gf.routing.route_single(OPATemp, port1=calIn.ports['o1'], port2=calOut.ports['o1'], cross_section=xs, radius = 20.0,
                                                    steps=[{"dx": 30},
                                                    {"dy": -50},
                                                    {"dx":  -100},
                                                    {"dy":  -((fa_pitch * 2) - 100)},
                                                    {"dx":  100},
                                                    {"dy": -50}
                                                    ])

        OPAIntermediate = gf.Component("Intermediate" + str(copy))
        OPAIntermediate << OPATemp

        pos = (radiatingElements[0].center[0], radiatingElements[0].ymax + 25)
        text = gf.components.texts.text(text = "GC2, WIDTH = " + str(gratingWidths[copy]) + " um", size = 28, position = pos, layer=(100,0), justify="right")
        OPAIntermediate << text

        OPAIntermediate.movey(400 * copy)

        # Add OPA to top level cell
        top << OPAIntermediate

        # deviceMargin = 150      # Buffer between device copies, um

        # opaDimX = OPA.xsize
        # opaDimY = OPA.ysize

        # deviceYSizeBuff = opaDimY + deviceMargin
        # numCopies = m.floor(((die_height - (yMargin * 2)) / deviceYSizeBuff) )


    # floor plan
    # This is the outline of the available space 
    # ^^ It is on layer 99 because of it.
    top << gf.components.rectangle(size=(die_width, die_height), centered=True, layer=(99,0))
        
    top.plot()
    top.show()
    

else:

    gc = gc_cornerstone_pdk_subLambda_noEtch(width_grating=1.0, period=0.67, nPeriods=numGCPeriods)

    # top cell
    top = gf.Component('TOP')

    OPA = gf.Component('OPA')

    re = gf.Component('Radiating Elements')

    radiatingElements = list()

    for i in range(numElements):

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
        if(stage != 0):
            rg = round( (numElements * 2) / divisor)
            for i in range( rg ):
                if(i % 2 == 0):
                    gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
                else:
                    gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o3'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
                

    OPA << pdiv

    # Route final splitter stage to radiating elements 
    for i in range(numElements):
        if(i % 2 == 0):
            gf.routing.route_dubin(OPA, port1=splitters[0][int(i/2)].ports['o2'], port2=radiatingElements[i].ports['o1'], cross_section=xs)
        else:
            gf.routing.route_dubin(OPA, port1=splitters[0][int(i/2)].ports['o3'], port2=radiatingElements[i].ports['o1'], cross_section=xs)



    # Input Grating Coupler
    gIn = gf.Component('gratingIn')

    # Position Input Grating Coupler
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
    calIn.movex(gIn.x - (gIn.xsize / 1))
    calIn.movey(gIn.y + fa_pitch)

    # Output Calibration Grating Coupler 
    cOut = gf.Component('Calibrator Output')
    calOut = cOut << fgc
    calOut.movex(gIn.x - (gIn.xsize / 1))
    calOut.movey(gIn.y - fa_pitch)

    OPA << cIn
    OPA << cOut

    gf.routing.route_single(OPA, port1=calIn.ports['o1'], port2=calOut.ports['o1'], cross_section=xs, radius = 20.0)

    # floor plan
    # This is the outline of the available space 
    # ^^ It is on layer 99 because of it.
    top << gf.components.rectangle(size=(die_width, die_height), centered=True, layer=(99,0))

    # Add OPA to top level cell
    top << OPA

    top.plot()
    top.show()

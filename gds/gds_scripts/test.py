import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
import cornerstone_pdk as cs_pdk # type: ignore
from gdsfactory.typings import ComponentSpec, CrossSectionSpec

# Cornerstone rib cross section
xs = cs_pdk.cornerstone_rib()

# Cornerstone Library
# gc = cs_pdk.gc_cornerstone_pdk()
gc = cs_pdk.gc_focusing_cornerstone_pdk()
mmi1x2 = cs_pdk.mmi1x2_cornerstone_pdk()
mmi2x2 = cs_pdk.mmi2x2_cornerstone_pdk()
wgx = cs_pdk.crossing_cornerstone_pdk()

# top cell
top = gf.Component('TOP')

# floor plan
# This is the outline of the available space 
# ^^ It is on layer 99 because of it.
top << gf.components.rectangle(size=(6000., 3000.), centered=True, layer=(99,0))

# Splitter
c1 = gf.Component('Power Division')
mmiIn = c1 << cs_pdk.mmi1x2_cornerstone_pdk()
mmiIn.movex(-(mmiIn.xmin+mmiIn.xmax)/2)

# MMI1 
mmi1 = c1 << mmi1x2
mmiIn.movex(200.)


top << c1
top.plot()
top.show()

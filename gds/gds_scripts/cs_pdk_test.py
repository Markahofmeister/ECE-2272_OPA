import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
import cornerstone_pdk as cs_pdk

c = gf.Component('TOP') 

mmi1x2 = c << cs_pdk.mmi1x2_cornerstone_pdk()
mmi1x2.movey(-5)

mmi2x2 = c << cs_pdk.mmi2x2_cornerstone_pdk()
mmi2x2.movey(5)

x = c << cs_pdk.crossing_cornerstone_pdk()
x.movey(15)

c.plot()

gc1 = c << cs_pdk.gc_focusing_cornerstone_pdk()
gc1.movey(-25)
c.plot()

gc2 = c << cs_pdk.gc_cornerstone_pdk()
gc2.movey(-45)
c.plot()

c.show()
import numpy as np
import gdsfactory as gf
import gdsfactory.components as pd

c = gf.Component()

# create two grating couplers
gc_rect = c << pdk.grating_coupler_rectangular()
gc_te = c << pdk.grating_coupler_elliptical()
gc_te.dmovey(50)

c.plot()

# add ports to view
c.add_ports(gc_rect.ports, prefix='gc_rect_')
c.add_ports(gc_te.ports, prefix='gc_te_')

c.pprint_ports()
c.draw_ports()
c.plot()

# define input/output ports
port1 = gc_rect.ports['o1']
port2 = gc_te.ports['o1']

# connect ports together using "route_single" function
route = gf.routing.route_single(c, port1=port1, port2=port2, cross_section="strip")

c.plot()

# route from predefined steps instead
c = gf.Component()

gc_rect = c << pdk.grating_coupler_rectangular()
gc_te = c << pdk.grating_coupler_elliptical()
gc_te.dmovey(50)

route_steps = gf.routing.route_single(c, port1=gc_rect.ports['o1'], port2=gc_te.ports['o1'],
                                      cross_section='strip',
                                      steps=[
                                         {"dx": -20}, 
                                         {"dy": -20},
                                         {"dx": -50},
                                         {"dy": 100},
                                         {"dx": 50},
                                         {"dy": -30}
                                             ])

c.plot()

# Define a 2x2 splitter
mmi = pdk.mmi2x2_with_sbend()

mmi.plot()

# Define grating coupler component
gc = gf.partial(pdk.grating_coupler_elliptical_uniform, taper_angle=20, period=0.5)

# Add fiber array to mmi using grating coupler defined above
c2 = gf.routing.add_fiber_array(component=mmi, radius=10.0, grating_coupler=gc, fiber_spacing=150)
c2.plot()

# Add same fiber array but without loopback
c2 = gf.routing.add_fiber_array(component=mmi, radius=10.0, grating_coupler=gc, fiber_spacing=150, with_loopback=False)
c2.plot()
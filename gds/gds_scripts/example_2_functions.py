import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk

@gf.cell
def grating_test_struc(period: float = 0.5, ff: float = 0.5, wg_width: float = 0.8, fiber_spacing: float = 127.0):
    c = gf.Component('Grating Test Structure')
    wgx = gf.cross_section.cross_section(width=wg_width, radius=25.0, layer=(1,0))
    taper_angle = 30

    gc = pdk.grating_coupler_elliptical_uniform(period=period, 
                                                fill_factor=ff, 
                                                taper_angle=taper_angle,
                                                cross_section=wgx)
    
    gc1 = c << gc
    gc2 = c << gc

    gc1.drotate(-90)
    gc2.drotate(-90)
    gc2.dmovex(fiber_spacing)

    route = gf.routing.route_single(c, 
                                    port1=gc1.ports['o1'], 
                                    port2=gc2.ports['o1'],
                                    cross_section=wgx)

    return c

## Test function is working
c = gf.Component()

gc_test = c << grating_test_struc()
c.plot()


## create grating coupler array which sweeps period and fill factor
period_list = np.linspace(0.35, 0.65, 10)
ff_list = np.linspace(0.4, 0.8, 10)

# empty list to add components to
components_list = []

# fill list with grating coupler test structures
for period in period_list:
    for ff in ff_list:
        D = grating_test_struc(period=period, ff=ff)
        components_list.append(D)

# place list of components into uniformly spaced grid
c = gf.grid(
    tuple(components_list),
    spacing=(25, 25),
    shape=(10, 10)
)

c.plot()


# create a new grid with text labels
c = gf.grid_with_text(
    tuple(components_list),
    text=gf.partial(pdk.text, size=10, justify="center"),
    spacing=(25, 25),
    shape=(10, 10)
)

c.show()









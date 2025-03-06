import numpy as np
import gdsfactory as gf
import gdsfactory.components as pdk
from gdsfactory.cross_section import CrossSection, cross_section, xsection
from gdsfactory.typings import LayerSpec

# Define cross section from design rules
@xsection
def cornerstone_rib(
    width: float = 0.45,
    layer: LayerSpec = (3, 0),
    radius: float = 25.0,
    radius_min: float = 10.0,
    **kwargs,
) -> CrossSection:
    """Return Cornerstone rib cross_section."""
    return cross_section(
        width=width,
        layer=layer,
        radius=radius,
        radius_min=radius_min,
        **kwargs,
    )

# Cornerstone grating coupler "SOI220nm_1550nm_TE_RIB_Grating_Coupler"
@gf.cell
def gc_cornerstone_pdk() -> gf.Component:
    gc = pdk.grating_coupler_rectangular(n_periods=60, period=0.67, fill_factor=0.5, 
                                         length_taper=350, width_grating=10.0, layer_slab=None, 
                                         cross_section=cornerstone_rib)
    return gc

# Focusing grating coupler
@gf.cell
def gc_focusing_cornerstone_pdk() -> gf.Component:
    gc = pdk.grating_coupler_elliptical_uniform(n_periods=30, period=0.67, fill_factor=0.5, taper_angle=45,
                                                layer_slab=None, 
                                                cross_section=cornerstone_rib)
    return gc

# Cornerstone 1x2 mmi splitter "SOI220nm_1550nm_TE_RIB_2x1_MMI"
@gf.cell
def mmi1x2_cornerstone_pdk() -> gf.Component:
    mmi = pdk.mmi1x2(width_taper=1.5, length_taper=20.0, length_mmi=32.7, width_mmi=6.0, 
                     gap_mmi=1.64, cross_section=cornerstone_rib)
    return mmi

# Cornerstone 2x2 mmi splitter "SOI220nm_1550nm_TE_RIB_2x2_MMI"
@gf.cell
def mmi2x2_cornerstone_pdk() -> gf.Component:
    mmi = pdk.mmi2x2(width_taper=1.5, length_taper=20.0, length_mmi=44.8, width_mmi=6.0, 
                     gap_mmi=0.53, cross_section=cornerstone_rib)
    return mmi

# Cornerstone rib crossing "SOI220nm_1550nm_TE_RIB_Waveguide_Crossing"
@gf.cell
def crossing_cornerstone_pdk() -> gf.Component:
    x = gf.Component()
    x.add_polygon( [(-0.225, -4.62 ), (-0.4  , -4.235), (-0.452, -3.85 ), (-0.7  , -3.465), 
                    (-0.672, -3.08 ), (-0.658, -2.695), (-0.654, -2.31 ), (-0.7  , -1.925), 
                    (-0.725, -1.54 ), (-0.825, -1.155), (-0.845, -0.845), (-1.155, -0.825), 
                    (-1.54 , -0.725), (-1.925, -0.7  ), (-2.31 , -0.654), (-2.695, -0.658), 
                    (-3.08 , -0.672), (-3.465, -0.7  ), (-3.85 , -0.452), (-4.235, -0.4  ), 
                    (-4.62 , -0.225), (-4.62 ,  0.225), (-4.235,  0.4  ), (-3.85 ,  0.452), 
                    (-3.465,  0.7  ), (-3.08 ,  0.672), (-2.695,  0.658), (-2.31 ,  0.654), 
                    (-1.925,  0.7  ), (-1.54 ,  0.725), (-1.155,  0.825), (-0.846,  0.845), 
                    (-0.825,  1.155), (-0.725,  1.54 ), (-0.7  ,  1.925), (-0.654,  2.31 ), 
                    (-0.658,  2.695), (-0.672,  3.08 ), (-0.7  ,  3.465), (-0.452,  3.85 ), 
                    (-0.4  ,  4.235), (-0.225,  4.62 ), (0.225,  4.62 ), (0.4  ,  4.235), 
                    (0.452,  3.85 ), (0.7  ,  3.465), (0.672,  3.08 ), (0.658,  2.695), 
                    (0.654,  2.31 ), (0.7  ,  1.925), (0.725,  1.54 ), (0.825,  1.155), 
                    (0.845,  0.845), (1.155,  0.825), (1.54 ,  0.725), (1.925,  0.7  ), 
                    (2.31 ,  0.654), (2.695,  0.658), (3.08 ,  0.672), (3.465,  0.7  ), 
                    (3.85 ,  0.452), (4.235,  0.4  ), (4.62 ,  0.225), (4.62 , -0.225), 
                    (4.235, -0.4  ), (3.85 , -0.452), (3.465, -0.7  ), (3.08 , -0.672), 
                    (2.695, -0.658), (2.31 , -0.654), (1.925, -0.7  ), (1.54 , -0.725), 
                    (1.155, -0.825), (0.845, -0.845), (0.825, -1.155), (0.725, -1.54 ), 
                    (0.7  , -1.925), (0.654, -2.31 ), (0.658, -2.695), (0.672, -3.08 ), 
                    (0.7  , -3.465), (0.452, -3.85 ), (0.4  , -4.235), (0.225, -4.62 )],
                    layer=(3,0) )
    x.add_port(name='o1', center=(x.xmin, 0), width=0.45, orientation=180, layer=(3,0))
    x.add_port(name='o2', center=(0, x.ymax), width=0.45, orientation=90, layer=(3,0))
    x.add_port(name='o3', center=(x.xmax, 0), width=0.45, orientation=0, layer=(3,0))
    x.add_port(name='o4', center=(0, x.ymin), width=0.45, orientation=270, layer=(3,0))
    return x

# For testing components
def main():

    c = gf.Component('TOP') 

    gc = c << gc_cornerstone_pdk()
    gc.movey(-15)

    gc = c << gc_focusing_cornerstone_pdk()
    gc.movey(-30)

    mmi1x2 = c << mmi1x2_cornerstone_pdk()
    mmi1x2.movey(-5)

    mmi2x2 = c << mmi2x2_cornerstone_pdk()
    mmi2x2.movey(5)

    x = c << crossing_cornerstone_pdk()
    x.movey(15)
    print('plotting...')
    c.plot()
    c.show()


if __name__ == "__main__":
    main()


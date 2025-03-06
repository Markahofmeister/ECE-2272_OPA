import numpy as np
import matplotlib.pyplot as plt
import gdsfactory as gf
import gdsfactory.components as pdk
import os
os.environ["GIT_PYTHON_REFRESH"] = "quiet"

def main(): 

    # create a Component object to add components to
    c = gf.Component()

    # waveguide with 25 um length and 750 nm width:
    wg1 = c << pdk.straight(length=25, width=0.75)

    # display components added to c
    c.show()

    # add circular bend to c
    b1 = c << pdk.bend_circular(radius=15, width=0.75)

    # move by 10 um in the y-direction
    b1.dmovey(10)

    c.show()

    # add another bend
    b2 = c << pdk.bend_euler(radius=20, width=0.75)

    # mirror bend wrt x-axis
    b2.dmirror_y()

    # move by -10 um in x-direction
    b2.dmovex(-10)

    c.show()

    # create a multi-mode interferometer component and move -5 um in the y-direction
    mmi = c << pdk.mmi1x2(width=0.75)
    mmi.dmovey(5)

    c.show()

    # display port names:
    mmi.ports.print()
    wg1.ports.print()
    b1.ports.print()

    # Connect various components together using ports
    wg1.connect('o2', mmi.ports['o1'])
    b1.connect('o1', mmi.ports['o2'])
    b2.connect('o1', mmi.ports['o3'])

    c.show()

    # create various path elements
    p1 = gf.path.straight(length=10)
    p2 = gf.path.arc(radius=20, angle=90)
    p3 = gf.path.euler(radius=10, angle=180)

    # combine into single path "p"
    p = p1 + p1 + p2 + p1 + p3 + p1

    p.plot()

    # move and rotate p
    p.rotate(45)
    p.move([10, -20])

    p.plot()

    # calculate path information
    print(p.length())

    s, K = p.curvature()
    plt.plot(s, K, ".-")
    plt.xlabel("Position along curve (arc length)")
    plt.ylabel("Curvature")

    # note that plt is using the matplotlib library
    plt.plot()

    # create three cross section definitions (waveguide and two metal layers):
    wgx = gf.Section(width=1, offset=0, layer=(1,0), port_names=("in", "out"))
    m1x = gf.Section(width=3, offset=3, layer=(45, 0))
    m2x = gf.Section(width=3, offset=-3, layer=(49, 0))

    # combine into single cross section
    xs = gf.CrossSection(sections=[wgx, m1x, m2x])

    # extrude cross section "xs" along the path "p" we created:
    c = gf.path.extrude(p, cross_section=xs)

    c.plot()

    # create a new Component object "c" since we overwrote it
    c = gf.Component('TOP')

    # add extruded path as two references to "c"
    ref1 = c << gf.path.extrude(p, cross_section=xs)
    ref2 = c << gf.path.extrude(p, cross_section=xs)
    ref2.dmirror_x()

    c.show()

    ## connect ports
    ref2.connect("in", ref1.ports['in'])

    c.show()

if __name__ == "__main__":
    main()

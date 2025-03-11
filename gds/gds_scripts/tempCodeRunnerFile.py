on the stage that connects to the bragg gratings, 
            # draw the connections between gratings 
            if(stage != 0):
                rg = round( (numElements * 2) / divisor)
                for i in range( rg ):
                    if(i % 2 == 0):
                        gf.routing.route_dubin(pdiv, port1=splitters[stage][int(i/2)].ports['o2'], port2=splitters[stage-1][i].ports['o1'], cross_section=xs)
                    else:
                        gf.rou
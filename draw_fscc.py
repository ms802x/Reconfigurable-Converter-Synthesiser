import schemdraw
import schemdraw.elements as elm

def draw_fib(caps,SW_connection,top_sw,SW_init):
    sw_count  = 1
    # fibunatchi circuit 
    d = schemdraw.Drawing()
    switch_label = ["Sa","Sb","Sa"]
    sw_count2 = SW_init
    #print(SW_connection)
    #SW_connection.insert(0, dict.fromkeys(top_sw[0]))
    print(SW_connection)
    #exit(1)
    for i,SW in zip(range(caps+1),SW_connection):


        if (i == 0):
            d.push()
            d += elm.Line().length(2.5).down()

            # this line list(dict.fromkeys(top_sw)) tp remove duplicates
            if (len(list(dict.fromkeys(top_sw[0])))==1):
              d += elm.Switch().down().label("S"+str(sw_count),loc="bottom")
              sw_count+=1
            sw_count,d = SW_helper(sw_count,d,list(dict.fromkeys(top_sw[0])))
            d.pop()

        else:
            d += elm.Line().length(2.5)

            d += elm.Switch().label(switch_label[i%2+1])
            d += elm.Dot() 
            d.push()
            #check for empty list
            if (len(top_sw[i])>0):
              sw_count2,d = SW_helper_up(sw_count2,d,list(dict.fromkeys(top_sw[i])))
            d.pop()
            d.push()
            d += elm.Capacitor().down().label("C"+str(i))
            d += elm.Dot()
            d.push()  # Save this drawing position/direction for later
            d += elm.Switch().left().label(switch_label[i%2])
            d += elm.Line().up()

            d.pop()
            d += elm.Switch().down().label(switch_label[i%2+1])

            ## Here starts the Vin,Vout, GND labeling 

            # now based on the number of connection 3,2,1 it will decide if it should connect directly 
            # or it will use two or three switches 
            sw_count,d = SW_helper(sw_count,d,SW)

            # add the last switch 
        if(i == caps):
            
            d += elm.Switch().right().label(switch_label[i%2])
            d += elm.Line().right().length(1)
            d += elm.Line().down().length(.5)

            #last switch
            sw_count,d = SW_helper(sw_count,d,SW_connection[-1])

    #d.save("FSCC circuit.svg")
    return d 

# This is helper function, it helps in drawing the circuit and make the code more effiecnt 
def SW_helper(sw_count,d,SW):

# now based on the number of connection 3,2,1 it will decide if it should connect directly 
  # or it will use two or three switches 
  
    if (len(SW) == 1):
      if(SW[0] == "GND"):
        d+=elm.Ground()
      else:
        d += elm.Line().label(SW[0],loc="left").length(0.5) 

      d.pop()

    elif (len(SW) == 2):
    
      # The first Switch is one the left down 
      d.push()
      d += elm.Line().length(1).left()
      d += elm.Switch().down().label("S"+str(sw_count)).label(SW[0],loc="left")
  # The second switch is  down down
      d.pop()
      d.push()
      d += elm.Line().length(1).right()

      if(SW[1] == "GND"):
        d += elm.Switch().down().label("S"+str(sw_count+1))
        d+=elm.Ground()
      else:
        d += elm.Switch().down().label("S"+str(sw_count+1)).label(SW[1],loc="left")

      d.pop()
      d.pop()
      sw_count+=2
    elif (len(SW) == 3):
          
      # The first Switch is one the left down 
      d.push()
      d += elm.Line().length(1.5).left()
      d += elm.Switch().down().label("S"+str(sw_count)).label(SW[0],loc="left")
      # The second switch is  down down
      d.pop()
      d.push()
      d += elm.Switch().down().label("S"+str(sw_count+1)).label(SW[1],loc="left")
      d.pop()
      # The third switch is to the right down. 
      
      if(SW[2] == "GND"):
        
        d += elm.Line().length(1.5).right()
        d += elm.Switch().down().label("S"+str(sw_count+2))
        d+=elm.Ground()
      else: 

        d += elm.Line().length(1.5).right()
        d += elm.Switch().down().label("S"+str(sw_count+2)).label(SW[2],loc="left")
      d.pop()
      sw_count+=3

    return sw_count,d


# This is helper function, it helps in drawing the circuit and make the code more effiecnt 
def SW_helper_up(sw_count,d,SW):

# now based on the number of connection 3,2,1 it will decide if it should connect directly 
  # or it will use two or three switches 
  
    if (len(SW) == 1):
      if(SW[0] == "GND"):
        d += elm.Line().up().length(1)
        d += elm.Switch().up().label("S"+str(sw_count),loc="bottom")
        d+=elm.Ground().up()
      else:
        d += elm.Line().up().length(1)
        d += elm.Switch().label("S"+str(sw_count),loc="bottom").label(SW[0],loc="right")

      d.pop()
      sw_count+=1

    elif (len(SW) == 2):
    
      # The first Switch is one the left down 
      
      d += elm.Line().length(1.5).up()
      d.push()
      d += elm.Line().length(1).left()
      d += elm.Switch().up().label("S"+str(sw_count),loc="bottom").label(SW[1],loc="right")
  # The second switch is  down down
      d.pop()

      d.push()
      d += elm.Line().length(1).right()

      if(SW[0] == "GND"):
        d += elm.Switch().up().label("S"+str(sw_count+1),loc="bottom")
        d+=elm.Ground().up()
      else:
        d += elm.Switch().up().label("S"+str(sw_count+1),loc="bottom").label(SW[0],loc="right")

      d.pop()
      d.pop()
      sw_count+=2
    elif (len(SW) == 3):
      
      d += elm.Line().length(1.5).up()
      # The first Switch is one the left down 
      d.push()
      d += elm.Line().length(1.5).left()
      d += elm.Switch().up().label("S"+str(sw_count),loc="bottom").label(SW[1],loc="right")
      # The second switch is  down down
      d.pop()
      d.push()
      d += elm.Switch().up().label("S"+str(sw_count+1),loc="bottom").label(SW[2],loc="right")
      d.pop()
      # The third switch is to the right down. 
      
      if(SW[2] == "GND"):
        
        d += elm.Line().length(1.5).right()
        d += elm.Switch().up().label("S"+str(sw_count+2),loc="bottom")
        d+=elm.Ground()
      else: 

        d += elm.Line().length(1.5).right()
        d += elm.Switch().up().label("S"+str(sw_count+2),loc="bottom").label(SW[1],loc="right")
      d.pop()
      sw_count+=3
    return sw_count,d

    
if __name__ == '__main__':

    draw_fib(caps,SW_connection)
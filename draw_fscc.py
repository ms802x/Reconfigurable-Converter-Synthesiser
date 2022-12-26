import schemdraw
import schemdraw.elements as elm

def draw_fib(caps,SW_connection):
    print(SW_connection)
    sw_count  = 1
    # fibunatchi circuit 
    d = schemdraw.Drawing()
    switch_label = ["Sa","Sb","Sa"]

    for i,SW in zip(range(caps+1),SW_connection):

        if (i == 0):
            d.push()
            d += elm.Line().down().length(1)
            sw_count,d = SW_helper(sw_count,d,SW)
            d.pop()

        else:
            d += elm.Line().length(2.5)

            d += elm.Switch().label(switch_label[i%2+1])
            d += elm.Dot()
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
            d.push()
            d+= elm.Capacitor().down().label("Cout")
            d+=elm.Ground()
            d.pop()
            d += elm.Line().right().length(3)
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
      #sw_count+=1

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



    
if __name__ == '__main__':

    draw_fib(caps,SW_connection)
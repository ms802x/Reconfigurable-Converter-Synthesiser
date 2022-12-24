from draw_fscc import *
from FSCC import * 
import schemdraw
import schemdraw.elements as elm
from PIL import ImageTk,Image
import io
import pandas as pd

def main(VCR,res):

        #VCR = input("Enter VCR: ")
        # these are for all binary states of P,Q
        P_set = list()
        Q_set = list()

        # Here the input comes from the user
        ##print("\n To terminate the program enter 1 or -1 only: ")
        # VCR = input("\n Enter VCR (example 1,3/2,5) : ")
        # exit command

        if VCR == '-1' or VCR == '1':
            return 0

        # defualt value
        #res = 0

        # if single VCR no res needed :
        try:
        # length = 0  means no input
            if len(VCR) == 0:
                # print No VCRs were entered
                print("1")
        # it will try to convert to float, if it couldn't it means this is multi values array
            float(VCR)
        except:
            pass
            #res = input("RES: ")

        #VCR = VCR.split(',')
        VCR = resolution(VCR, res)

        # this function claculate number of caps and return P,Q array along with it.
        # if the requested VCR ==1 then just show error message

        (capacitors, P, Q) = new_caps(VCR)
        weights_list = list()
        weights_list = terminal_weights(capacitors)
       # return weights_list
        # draw the circuit
        # draw_FSCC(capacitors)
        #   # itterate through P,Q at the same time and remove overlaping sets.
        for (a, b,c) in zip(P,Q,capacitors):
            #(PP_, QQ_) = check_overlap(a, b, weights_list)
            #print(a,b,c)
            (PP_, QQ_) = check_overlap(a, b,weights_list[str(c)] )        
            P_set += PP_
            Q_set += QQ_
      
        # multiply the output set by 2
        Q_set = np.multiply(Q_set, 2)
        # all transitions postive and negative
        SPTT_All = Q_set + P_set
        # Now we need to sort each SPTT code per its VCR
        SPTT_VCR_CODE = defaultdict(list)
        for col in SPTT_All:
          #number of capacitors 
          cap_col = len(col)-2
          SPTT_VCR_CODE[str(calc_VCR(col, weights_list[str(cap_col)]))].append(col)
        # If only one VCR is inserted this step should be ignored and any state is accepted
        # print(SPTT_VCR_CODE.keys())
        requested_SPTT = defaultdict(list)
        # if the lengh was one it means we dont really need to find the dissimilarity
        # also if the VCR =2, this will cause an error because I add the 1 combinarition based on weights lengh>3 however, vcr of 3 has weights of length 3

        if len(VCR) == 1:
            if VCR[0] == '2':
                requested_SPTT[VCR[0]] = np.array([0, 2, 1])
            elif VCR[0] == '0.5' or VCR[0] == '1/2':
                requested_SPTT[VCR[0]] = np.array([0, 1, 2])
            else:
                try:
                    requested_SPTT[VCR[0]] = SPTT_VCR_CODE[VCR[0]][0]
                except:
                    #print Invalid input
                    return 0
        else:

        # remove vout duplicates
        # and remove any connection Vin at the second terminal 
            all_codes = SPTT_VCR_CODE
            SPTT_VCR_CODE = remove_twophase_dup(SPTT_VCR_CODE)
            # The purpose of this to append all the connections which have overlapping connections although there Rout will be calaculated. 
            for VCR_code in all_codes.keys():
              if (VCR_code in SPTT_VCR_CODE):
                pass
              else :
                SPTT_VCR_CODE[VCR_code]= all_codes[VCR_code]

           # return SPTT_VCR_CODE
            Selected_SPTT = SPTT_VCR_CODE
            #return Selected_SPTT
            #return Selected_SPTT
            #return SPTT_VCR_CODE
   
            
        # last thing is to display these sets to the user
        # I have generated both postive and negative VCRs at once, thereofre, we need to filter
            #return Selected_SPTT
            for i in Selected_SPTT.values():
              for j in i:
                temp_VCR = str(calc_VCR(j, weights_list[str(len(j)-2)]))
                if temp_VCR in VCR:
                    requested_SPTT[temp_VCR].append(j)
            #return requested_SPTT
        # if ivalid input the list will be empty
            #return requested_SPTT
            if len(requested_SPTT.keys()) == 0:
                #print Invalid input
                return 0
        # we have multiple VCRs
        # this will calaculte the dissimilarity between options
        requested_SPTT = lengh_match(requested_SPTT)
        #return requested_SPTT
        #return requested_SPTT
        #return requested_SPTT
        mintrans_SPTT = dissimilarity(requested_SPTT)
        #return  mintrans_SPTT
           # mintrans_SPTT
          #Selected_SPTT is the minmum transition matrix
        #return mintrans_SPTT
        requested_SPTT = min_dissimilarity(mintrans_SPTT) 
        #return requested_SPTT
        # the minmum transition doesn't include the VCR, thereofre, I'm recalculating it here.
        selected_VCR =  defaultdict(list)
        for i in requested_SPTT:
         # print(i)
          three_count = (i == 3).sum()
          temp_VCR = str(calc_VCR(i, weights_list[str(len(i)-three_count-2)],three_count))
          selected_VCR[temp_VCR].append(i)


    

        # we need to reverse the connection, otherwise people may get confused from which part of the circuit the input will be plugged. 
        selected_VCR = flip_connection(selected_VCR)
        # the output is the requested VCR by the user
        # print(requested_SPTT)
        
        #print ('\nNumber of capacitors needed: ' + str(capacitors) + '\n')

        # to order the gain in inc order :
        od = OrderedDict(sorted(selected_VCR.items(),key = lambda x: float(Fraction(x[0]))))
        #return od 
        # Create dictionary for the order, reversed gains

        VCR_CODE = defaultdict(list)

        # I have used flip with v so I can reverse the order, where the input comes first

        for (k, v) in od.items():
            w = [("GND" if str(val) == '0' else val) for val in v[0] ]
            w = [("Vin" if str(val) == '1' else val) for val in w]
            w = [("Vout" if str(val) == '2' else val) for val in w]
            w = [("X" if str(val) == '3' else val) for val in w]

        # print("Gain: "+str(round(float(Fraction(k)),3)),", State: "+str(w))

            VCR_CODE[str(round(float(Fraction(k)), 3))] = w

        sptt_code = VCR_CODE   
        VCR_set = list(sptt_code.keys())
        designer_SPTT,SW_connection,SW_connection_x = desiner_code_generator(sptt_code,VCR_set)
        # remove null connection
        return designer_SPTT,SW_connection,SW_connection_x,capacitors

if __name__ == "__main__":
    designer_SPTT,SW_connection,SW_connection_x,capacitors = main(["2","6"],1)
    caps = max(capacitors)
    print(SW_connection_x)
    # now we create the dataframe (or excel sheet switching table)
    df = pd.DataFrame(designer_SPTT)
    df.to_excel("switching_table.xlsx")
    # draw the circuit
    d = draw_fib(caps,SW_connection,designer_SPTT)
    d.draw()
    d.save('my_circuit.svg')

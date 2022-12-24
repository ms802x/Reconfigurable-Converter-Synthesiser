from fractions import Fraction
from scipy.spatial import distance
import itertools
from collections import defaultdict
from collections import OrderedDict
#from FSCC_draw import draw_FSCC
import numpy as np
import sys

# Step (0): find required resoultion

def resolution (VCR,res):
  # this function takes string input, convert it to float and add the resolution between min and max values 
  # also it simplifies fractions 

   #this to simplify the fractions
  VCR = [str(Fraction(v)) for v in VCR]

  if (res == 0 or res ==""):

    return VCR 
  res = float(res)
  #this to find min/max
  VCR_mod = [float(Fraction(v)) for v in VCR]
  VCR_max = max(VCR_mod)
  VCR_min = min(VCR_mod)
  while (VCR_max > VCR_min):
    VCR_min += res
    # this is due to how python translates numbers it give 2.10000001 > this doesn't converge to fraction like 21/10 
    VCR_min = round(VCR_min,6)
    VCR_res = Fraction(str(VCR_min))
    VCR.append(str(VCR_res))
  #Remove duplicates 
  VCR = set(VCR)
  return VCR

# Step (1): Determine the number of required capacitors
# step 1 is found using makowski general limit 

def num_caps(VCR):
  #numerator
  P = list()
  #denominator
  Q = list()
  QP_list = list()
  caps_list = list()


  for r in VCR:
    # casting the type(input is string) 
    #for max vcr:
    num = int(Fraction(r).numerator)
    if(num<0):
      den = -1 * int(Fraction(r).denominator)
    else:
      den = int(Fraction(r).denominator)

    QP_list.append(num)
    QP_list.append(den)

    P.append(abs(num))
    Q.append(abs(den))

  # find the max of the two lists
  QP_list = np.array(QP_list)
  min_VCR = QP_list.min()
  QP_list_abs = np.abs(QP_list) 
# Get the index of the highest absolute value:
  max_index = np.argmax(QP_list_abs) 
  max_VCR = QP_list[max_index]
  max_VCR_abs = abs(max_VCR)
  #Fk+2, means minmum k is 1 otherwise it will be like a buffer. 
  F1 = [1, 0 ,2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
  # Now we need to check if max_VCR was a Fibonnacci number 
  while not (max_VCR_abs in F1):
    max_VCR_abs+=1
  # now we can find the number of capacitor by subtracting two from the index 
  # however, python starts from zero, therefore, subtracting one will give
  #the number of required caps
  capacitors = F1.index(max_VCR_abs)-1
  # this to account for negative vcr when they are the max in the array
  if(max_VCR<0 or abs(max_VCR) == abs(min_VCR)):
    capacitors +=1

  return capacitors,P,Q


# Step (2): Terminal Weight assignment
# The weight depends on Fibonnacci number 
# the sum of the weight should give zero for each terminal 

def terminal_weights(capacitors):

  weights_cap = defaultdict()

  # find unique set of cap
  unique_cap = set(capacitors)
  F1 = [1, 1 ,2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]


  for c in unique_cap:
    # first weight is the max VCR Fk+2
    # remember python lists starts with zero 
    w1 = F1[c+1]
    # last weight is -1
    wk_2 = -1  

    #sum of boundry condition weights 
    net_weight = w1+wk_2

    # now the sum of all Fibonnacci number should be zero 
    # w2+w3+w4...wk_1 = - (w1+wk_2)
    # Also, the number of remaining weights is is actually the number of caps
    # Here I'm finding the combination of slice of Fibonnacci list
    
    F2 = F1[:c+1]
    for i in itertools.combinations(F2, c):
      
      if (np.sum(i) == net_weight):
        #tuples are immutable, we need list to append
        i = [-1*element for element in i]
        i.append(w1)
        i.insert(0,wk_2)
        weights_cap[str(c)]= i 
  # to be modified later, this to account for negative VCR
      elif (np.sum(i) == - net_weight):
        weights_cap[str(c)]= i 
      else:
        continue 
  return weights_cap


def new_caps(VCR):
  #numerator
  P = list()
  #denominator
  Q = list()
  caps_list = list()
  F1 = [-1, -1 ,2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233]
  for r,i in zip(VCR,range(len(VCR))):
    # casting the type(input is string) 
    #for max vcr:
    num = int(Fraction(r).numerator)
    if(num<0):
      den = -1 * int(Fraction(r).denominator)
    else:
      den = int(Fraction(r).denominator)

    P.append(abs(num))
    Q.append(abs(den))

    if (P[i]>=Q[i]):
      max_VCR_abs = P[i]
    else :
      max_VCR_abs = Q [i]    

    while not (max_VCR_abs in F1):
      max_VCR_abs+=1
    # now we can find the number of capacitor by subtracting two from the index 
    # however, python starts from zero, therefore, subtracting one will give
    #the number of required caps
    capacitors = F1.index(max_VCR_abs)-1

    # this to account for negative vcr when they are the max in the array
    if(float(Fraction(r))<0):
      capacitors +=1
    caps_list.append(capacitors)
  return caps_list,P,Q



#Step (3):SPTT Code assignment, 0=GND, 1=Input, 2=Outpt
# Now to generate set set of possible transition we need to use the Maksowki defintion of VCR 
# VCR = P/Q = Vin/Vout , hence Vin = P, Vout = Q 
#Also, using terminal weights we need to find the values that achieve our P/Q 
def ternary_array(value,weights):
  # this have three values 0 (gnd), 1(Vin), 2(Vout)
  # the size of this array is number of capacitor + 2 
  SPTT = list()
  #Note this method appends three set of values, if the weights length was 3 then it will cause a problem:
  # for example, 0.5 and 2 will not work since the weights list is [-1,-1,2]
  # for 1 repetions 
  count_1 = [[0,0,1],[0,1,0],[1,0,0]]
  count_2 = [[1,1,0],[0,1,1],[1,0,1]]
  count_3 = [1,1,1]
  count_4 = [[0,1],[1,0]]
  count_5 = [1,1]


  for i in range(1,len(weights)):
    for j in itertools.combinations(weights, i):
      #print(j)
      #print(abs(np.sum(j)), np.sum(j),j,value)
     # print(j,np.sum(j),value)
      if (abs(np.sum(j)) == abs(value)):
        #print("in")
        # reset the list with each itteration
        P_Array1 = list()

        # count number of ones 
        arr = np.array(j)
        count = (arr == -1).sum()

        # this to pre set all possible combination if 1 apperaed in the sum array
        if(len(weights)>3):
          for k in range(3):
            if(count == 1):
              P_Array1.append(count_1[k])

            elif(count ==2):
              P_Array1.append(count_2[k])

            elif (count == 3):
              P_Array1.append(count_3)
        
            else: 
              # print("I'm in zero")
              P_Array1.append([0,0,0])
        else: 
          for k in range (2):
            if(count == 1):
              P_Array1.append(count_4[k])

            elif(count ==2):
              P_Array1.append(count_5)
        
            else: 
              # print("I'm in zero")
              P_Array1.append([0,0])


## if we had 1 capacitor we would have different combinations 

        # now for not 1 case :
        # copy the list and intiate it with zeros
        #print(P_Array1)
        term_assi = [0]*len(weights) 
        # set 1 at each list corrspond to input or output
        for w in j :
          #print(w)
          if (abs(w)== 1):
            continue 
         # print("I passed continue")
          # set 1 at that number index
          idx = weights.index(w)
          term_assi[idx]=1
        # add all ones combination to the list then remove duplicates
        if (len(weights)>3):
          for m in range(3):
            term_assi[0:3] = P_Array1[m]
            #without [:] this code will not work, you need to copy the list
            SPTT.append(term_assi[:])
        else:
          # this for the case where we have one capacitor only 
          for m in range(2):
            term_assi[0:2] = P_Array1[m]
            #without [:] this code will not work, you need to copy the list
            SPTT.append(term_assi[:])

  SPTT.sort()

  return  list(SPTT for SPTT,_ in itertools.groupby(SPTT))

# If P has common values with Q then cancel it this is the purpose of this function
# it also calls ternary_array function witin so no need to call it
def check_overlap(Nem,Den,weights):
  P_valid_list = list()
  Q_valid_list = list()
  SPTT1 = np.array(ternary_array(Nem,weights))
  SPTT2 = np.array(ternary_array(Den,weights))
  #just to make sure there is no output/input overlap
  for i in range (len(SPTT1)):
    for k in range (len(SPTT2)):
      #3print(SPTT2[k],SPTT1[i])
      if(np.bitwise_and(SPTT2[k],SPTT1[i]).any() == False):
        P_valid_list.append(SPTT1[i])
        Q_valid_list.append(SPTT2[k])
  return P_valid_list , Q_valid_list





# Step 4 minimize number of transition nominomial dissimilarity

# before finding the dissimilarity we need to know the VCR for each row 
def calc_VCR(col,weights,three_count = 0): # takes two inpus the SPTT states and the weights
  P,Q =0,0
  ## The if statment to account for the case where there is an empty connection 
  
  for i in range (len(weights)):
    if (col[i+three_count] == 1):
      P+=weights[i]
    elif(col[i+three_count] == 2):
      Q+=weights[i]
    else :
      continue
  # It will return the net sum of the column as ratio(VCR) 
  if (P ==0 or Q ==0):
    return 1 
  
  return -Fraction(P,Q)





#The purpose of this function is to prevent the Vout from being connected in both phases.
# it will be used again inside another function 
def dup_indices(lst, item):
  return [i for i, x in enumerate(lst) if x == item]

# remove duplicates 
def remove_twophase_dup(SPTT):
# remove any Vout that appears in two phases Sa and Sb
#will be modified later to account for step down conversion 
  n_SPTT= defaultdict(list)

  for k,i in SPTT.items():
    for j in i:
      t = dup_indices(j,2)
     # print(len(t),t)
      if(any(n % 2 == 1 for n in t) and any(n % 2 == 0 for n in t) ):
        pass
      else:
        #create new list  
        if (str(j[0]) == "2" or str(j[1]) == "2"):
          n_SPTT[k].append(j)
  



  return  n_SPTT


# this function purpose if to match the size of each VCR, if the VCR needed 3 capacitor and we have 5 it will appends two null values.
def lengh_match(VCR_Matrix):
  lengh_match_dict = defaultdict(list)
  # to create a size matched matrix we need to append the differnce in size for each VCR matrix
  VCR_Matrix_list = list(VCR_Matrix.values())
  array_size = [len(VCR_Matrix_list[i][0]) for i in range(len(VCR_Matrix.keys()))]
  m_size = max(array_size)
  for k,v in VCR_Matrix.items():
    for VCR in v:
      temp_VCR = VCR
      while (len(temp_VCR)!=m_size):
        # 3 means null value i.e don't include it in the connection
        temp_VCR = np.insert(temp_VCR,0, 3)
      lengh_match_dict[str(k)].append(temp_VCR)

  return lengh_match_dict
  


# Now lets define the dissmalirity function : 
# these data are nominal data, hence the dissimilarity can be easily calculated using 
# (sum of dissimilar data)/(total data)
# we should look for the minmum distance between arrays:
def dissimilarity(SPTT_VCR_CODE):

  mintrans_SPTT = defaultdict(list)
  # we need three nested loop for this task to be accomplished (I belive this is the simplest we can do)
  # I will try to make it faster later because 4 loops is overkill 
  # The number of itterations assume we have 4 arrays is : len(n_3)*len(n_2)*len(n_1)*len(n_0)+len(n_2)*len(n_1)*len(n_0)+ len(n_1)*len(n_0) which is too much we need to optimize it 
  # we need initial D to compare all of our alternatives 
  # D will never exceed 1 crate a list which contains the states of minmum Ds 
  min_D = 1.1
  #mintrans_SPTT["VCR_Array"].append(temp_array)

  #this list is just to store min dissimilarity states 
  temp_array = list()
  all_VCR = list(SPTT_VCR_CODE.keys())
 # print(SPTT_VCR_CODE)
  for i in range(len(all_VCR)):
    for j in range(len(all_VCR)):
      # to escape the case where it compares with itself 
      if (i ==j):
        continue

      for k in SPTT_VCR_CODE[all_VCR[i]]:
        for w in SPTT_VCR_CODE[all_VCR[j]]:
          D = distance.hamming(k,w)

         # print(k,w,D)

          if (min_D > D):
            min_D = D
            temp_array = w[:]
        #print(k,w,D,temp_array)
      #I must convert key into string otherwise it will not work 
      mintrans_SPTT[str(k)].append(temp_array)
      mintrans_SPTT[str(k)].append(min_D)
      #reset D
      min_D = 1.1
  return mintrans_SPTT





  # Now lets define the dissmalirity function : 
# these data are nominal data, hence the dissimilarity can be easily calculated using 
# (sum of dissimilar data)/(total data)
# we should look for the minmum distance between arrays:
def modified_dissimilarity(SPTT_VCR_CODE):

  mintrans_SPTT = defaultdict(list)
  # we need three nested loop for this task to be accomplished (I belive this is the simplest we can do)
  # I will try to make it faster later because 4 loops is overkill 
  # The number of itterations assume we have 4 arrays is : len(n_3)*len(n_2)*len(n_1)*len(n_0)+len(n_2)*len(n_1)*len(n_0)+ len(n_1)*len(n_0) which is too much we need to optimize it 
  # we need initial D to compare all of our alternatives 
  # D will never exceed 1 crate a list which contains the states of minmum Ds 
  min_D = 1.1
  #mintrans_SPTT["VCR_Array"].append(temp_array)

  #this list is just to store min dissimilarity states 
  temp_array = list()
  all_VCR = list(SPTT_VCR_CODE.keys())
 # print(SPTT_VCR_CODE)
  for i in range(len(all_VCR)):
    for j in range(len(all_VCR)):
      # to escape the case where it compares with itself 
      if (i ==j):
        continue

      for k in SPTT_VCR_CODE[all_VCR[i]]:
        for w in SPTT_VCR_CODE[all_VCR[j]]:
          D = distance.hamming(k,w)

         # print(k,w,D)
          if (min_D > D):
            min_D = D
            temp_array = w[:]
        #print(k,w,D,temp_array)
      #I must convert key into string otherwise it will not work 
      mintrans_SPTT[str(k)].append(temp_array)
      mintrans_SPTT[str(k)].append(min_D)
      #reset D
      min_D = 1.1
  return mintrans_SPTT

def min_dissimilarity(mintrans_SPTT):
  # This is just because number of switches will not exceed this number for sure
  #we can set D_temp to #capacitor+1 also >>:) 
  D_temp = 100000000
  #for i in range (1,len(mintrans_SPTT['[0 0 2 1 1]']),2):
  for k,v in mintrans_SPTT.items():

    D = sum([v[i] for i in range (1,len(v),2)])
    SPTT = [v[i] for i in range (0,len(v),2)]
    #print(SPTT)
    if (D_temp > D):
      D_temp = D
      #print(k,v)
      #print( k[1:-1])
      #remoe spaces and make a list, the key is string we need to keep the data type matached with the other types
      k = [int(t) for t in  k[1:-1].replace(' ','')]
      k = np.array(k)
      SPTT.append(k) 
      Selected_SPTT = SPTT[:] 

  return Selected_SPTT


# the purpose of this function is to reverse the whole matrix connections 
# I have wired it wrong at the beginging and now I'm fixing the problem. 
def flip_connection(connections):
  flip_connection_dic = connections.copy()
  for k,c in flip_connection_dic.items():
    ind = max(dup_indices(c[0],3),default=None)
    l = c[0][:ind:-1]
    if(ind != None):
      flip_connection_dic[k][0][ind+1:]=l
    else:
      flip_connection_dic[k][0][:]=l

  return flip_connection_dic





def desiner_code_generator(SPTT,VCR_set):
  
    #This part we are trying to generate ON/OFF switch state from VOUT,Vin,GND parameter 
    # convert row to coulmn
    # create list out of the dict and
    SPTT1 = [i for i in SPTT.values()]
    SPTT1 = [i  for i in SPTT1 if len(i)>0]
    row_col = [list(i) for i in zip(*SPTT1)]
    """
    #temperoray list 
    temp = list()
    try:
      for k in range(len(SPTT1)):
        # to avoid empty sets
        for i in SPTT1:
          temp.append(i[k])
        row_col.append(temp)
        temp = list()
      return row_col 
    except:
      print(i)
      return 0
      """
    # generate the unique values from the converted list  
    temp = list()
    SW_connection = list()
    for i in row_col:
      for j in set(i):
        temp.append(j)
      SW_connection.append(temp)
      temp = list()
    
    #This part generate the SW_states for the designer 
    designer_SPTT = defaultdict(list)

    designer_SPTT["SW/G"] = VCR_set

    SW_init = 1
    SW_connection_x = SW_connection
    SW_connection = [ list(set(i) - set(['X'])) if 'X' in i else i for i in SW_connection]
    for a,b in zip(row_col,SW_connection):
      if (len(set(a))==1):
        continue

      for port in b :
        s_temp = ["ON" if i==port else "OFF" for i in a ]
        designer_SPTT["S"+str(SW_init)] = s_temp

        SW_init+=1
      
    return designer_SPTT,SW_connection,SW_connection_x
'''
Arguments:
1. Block Size - 64/128 depdends on IVLBC block size    
2. Number for rounds
3. Minimum Number of active S-boxes
4. Maximum Number of active S-boxes in each round
5. fix/no_fix - whether difference of some round is fixed or not
6. No. of trails to find 
7. possilbe/impossible differential characteritics
8. Solver to be used (GUROBI/CPLEX)
(if you are changing the code for anothe cipher then please change no. of ineq. in line 247 and 382)
python IVLBC_1.py 64 11 1 2 no_fix 1 possible GUROBI 
python IVLBC_1.py 64 5 1 2 fix 1 impossible CPLEX
'''

import string
import sys
from math import floor


GUROBI_EXISTS = False
CPLEX_EXISTS = False

try:
  import google.colab
  IN_COLAB = True
except:
  IN_COLAB = False

if (sys.argv[8] == "GUROBI"):
    try: 
    	from gurobipy import *
    	GUROBI_EXISTS = True
    except:
    	GUROBI_EXISTS = False

if (sys.argv[8] == "CPLEX"):
	try: 
		from docplex.mp.model_reader import ModelReader
		CPLEX_EXISTS = True
	except:
		CPLEX_EXISTS = False

if (GUROBI_EXISTS == False) and (CPLEX_EXISTS == False):
	sys.exit()

conv = (
0, 1, -1, 0, -1, 0, 1, -1, 2,
-2, -2, -1, -1, -1, -1, 1, 2, 6,
2, -2, 1, 0, 3, -2, 1, -1, 2,
-2, -1, 5, 1, 3, 3, 2, -2, 0,
1, 0, 3, -2, 1, -1, 2, -2, 2,
3, 3, 2, -2, -2, -1, 5, 1, 0,
1, 1, -2, 0, 1, 1, 1, 2, 0,
5, 1, 3, 3, 2, -2, -2, -1, 0,
1, 1, 1, 2, 1, 1, -2, 0, 0,
1, 2, -2, -2, -1, 1, -1, 1, 4,
1, 2, -2, -2, -1, -1, -1, -1, 6,
-1, 2, 2, -1, 0, 2, 1, 2, 0,
-1, 1, -1, 1, 1, 2, -2, -2, 4,
1, -1, 0, 1, -1, 0, -1, 0, 2,
-1, 1, 1, 2, -2, -2, -1, 1, 4,
-1, -1, 1, 2, -2, -2, -1, -1, 6,
2, -2, -2, -1, 5, 1, 3, 3, 0,
-1, -1, -1, -1, 1, 2, -2, -2, 6,
-1, 0, -1, 0, 1, -1, 0, 1, 2,
-1, 0, 1, -1, 0, 1, -1, 0, 2,
-2, -2, -1, 1, -1, 1, 1, 2, 4,
    )
convpbl = (
-1, -1, -3, 0, 0, 0, 2, 1, 2, 4, 0,
0, 0, 1, 0, 0, 0, 1, 0, 0, -1, 0,
0, 0, -1, 0, 2, -1, 1, 2, 1, 0, 0,
1, 0, 1, 0, 1, 0, 1, 0, -1, -2, 0,
2, -1, 1, 2, 0, 0, -1, 0, 1, 0, 0,
1, 2, 0, 0, -1, 0, 2, -1, 1, 0, 0,
2, 1, -1, -1, -3, 0, 0, 0, 2, 4, 0,
-1, 2, -2, 2, -1, -1, -1, 1, 2, 5, 0,
-2, 2, -1, -1, -1, 1, -1, 2, 2, 5, 0,
0, 0, 2, 1, -1, -1, -3, 0, 2, 4, 0,
-2, 1, -1, 1, 0, 1, -1, -1, 2, 4, 0,
-1, 0, 2, -1, 1, 2, 0, 0, 1, 0, 0,
-3, 0, 0, 0, 2, 1, -1, -1, 2, 4, 0,
1, 0, 0, 0, 1, 0, 0, 0, 0, -1, 0,
-1, -1, -2, 1, -1, 1, 0, 1, 2, 4, 0,
-2, 1, -1, -2, -1, -2, -1, -1, 6, 9, 0,
-1, -1, -2, 1, -1, -2, -1, -2, 6, 9, 0,
-1, -2, -1, -1, -2, 1, -1, -2, 6, 9, 0,
-1, -2, -1, -2, -1, -1, -2, 1, 6, 9, 0,
0, 0, 0, 0, 0, 0, 0, 0, -1, -1, 1,
    )

P64 = (24,25,26,27,36,37,38,39,48,49,50,51,12,13,14,15,
       40,41,42,43,52,53,54,55,0,1,2,3,28,29,30,31,56,
       57,58,59,4,5,6,7,16,17,18,19,44,45,46,47,8,9,10,
       11,20,21,22,23,32,33,34,35,60,61,62,63)

#P64 = (63,62,61,60,35,34,33,32,23,22,21,20,11,10,9,8,47,
    #    46,45,44,19,18,17,16,7,6,5,4,59,58,57,56,31,30,
    #    29,28,3,2,1,0,55,54,53,52,43,42,41,40,15,14,
    #    13,12,51,50,49,48,39,38,37,36,27,26,25,24)

# P64 = (0,1,2,3,28,29,30,31,40,41,42,43,52,53,54,55,16,
#        17,18,19,44,45,46,47,56,57,58,59,4,5,6,7,32,33,
#        34,35,60,61,62,63,8,9,10,11,20,21,22,23,48,49,
#        50,51,12,13,14,15,24,25,26,27,36,37,38,39)

IVLBC = int(sys.argv[1])
s_boxes = int(IVLBC/4)
if (IVLBC==64):
    Perm = P64
else:
    print("Incorrect Parameters!")
    sys.exit()
ROUND = int(sys.argv[2])
min_sbox = int(sys.argv[3])
max_sbox_round = int(sys.argv[4])

if (sys.argv[5] == "fix"):
    fix = True
else:
    fix = False
attack_type = sys.argv[7]
fix_diff = [0x0000000000000001,0x0000000000000001]
fix_pos = [0,ROUND]
#fix_diff = [0x00000000001100000000000000000000,0x0090000000c000000000000000000000]
#fix_diff = [0x00000000001100000000000000000000]
#fix_diff = [0x000000000a0000000500000000000a00]
#fix_diff = [0x00002000001000010000000000000000]
#fix_pos = [1,2]

fix_diff_bin = [bin(diff)[2:].zfill(IVLBC) for diff in fix_diff];
fix_bit = [];
for diff_1 in fix_diff_bin:
    fix_bit.append([len(diff_1)-1-i for i in range(0,len(diff_1)) if diff_1[i]=="1" ])

def Constraints_XOR(x, y, z):
    #Generate the constraints by XOR operation.
    buf = ''
    buf = buf + x + " + " + y + " - " + z + " >= 0 \n"
    buf = buf + x + " - " + y + " + " + z + " >= 0 \n"
    buf = buf + " - " + x + " + " + y + " + " + z + " >= 0 \n"
    buf = buf + x + " + " + y + " + " + z + " <= 2 \n"
    return buf

def PrintOuter(FixList,BanList):
    opOuter = open("Outer" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND) +"_" + str(attack_type) +".lp",'w+')
    opOuter.write("Minimize\n")
    buf = ''
    if (attack_type == "possible"):
        for i in range(0,ROUND):
            for j in range(0,s_boxes):
                buf = buf + "a" + str(i) + "_" + str(j)
                if i != ROUND-1 or j != (s_boxes-1):
                    buf = buf + " + "
    if (attack_type == "impossible"):
        for i in range(0,IVLBC):
            if (i!=IVLBC-1):
                buf = buf + 'x0_' + str(i) + ' + '
            else:
                buf = buf + 'x0_' + str(i)
    opOuter.write(buf)
    opOuter.write('\n')
    opOuter.write("Subject to\n")
    ##################
    if(fix==True):
        for b in range(0,len(fix_bit)):
            buf = ''
            fix_s_box_next = [floor((i)/4) for i in fix_bit[b]]
            for j in range(0,s_boxes):
                    #if (fix_pos!=0):
                    #    if(j in fix_s_box_prev):
                    #        buf = buf + "a" + str(fix_pos[b]-1) + "_" + str(j) + " = 1\n"
                    #    else:
                    #        buf = buf + "a" + str(fix_pos[b]-1) + "_" + str(j) + " = 0\n"
                    if (fix_pos!=ROUND):
                        if(j in fix_s_box_next):
                            buf = buf + "a" + str(fix_pos[b]) + "_" + str(j) + " = 1\n"
                        else:
                            buf = buf + "a" + str(fix_pos[b]) + "_" + str(j) + " = 0\n"
            opOuter.write(buf)
    #################
    ##################
    if (fix==True):
        for b in range(0,len(fix_bit)):
            buf = ''
            for j in range(0,IVLBC):
                if(j in fix_bit[b]):
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 1\n"
                else:
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 0\n"
            opOuter.write(buf)
    #################
            
    buf = ''
    for i in range(0,ROUND):
        buf = ''
        for j in range(0,s_boxes):
            buf = ''
            for k in range(0,4):
                buf = buf +  "x" + str(i) + "_" + str(4*j+k)
                if k != 3:
                    buf = buf + " + "
            buf = buf + " - a" + str(i) + "_" + str(j) + " >= 0\n"
            for k in range(0,4):
                buf = buf + "x" + str(i) + "_" + str(4*j+k) + " - a" + str(i) + "_" + str(j) + " <= 0\n"
            #
            '''
            for k in range(0,4):
                buf = buf + "4 x" + str(i) + "_" + str(4*j+k)
                if k != 3:
                    buf = buf + " + "
            for k in range(0,4):
                buf = buf + " - x" + str(i+1) + "_" + str(P64[4*j+k])
            buf = buf + " >= 0\n"
            for k in range(0,4):
                buf = buf + "4 x" + str(i+1) + "_" + str(P64[4*j+k])
                if k != 3:
                    buf = buf + " + "
            for k in range(0,4):
                buf = buf + " - x" + str(i) + "_" + str(4*j+k)
            buf = buf + " >= 0\n"
            '''
            #
            # for k in range(0,21):
            #     for l in range(0,9):
            #         if conv[9*k+l] > 0:
            #             if l <= 3:
            #                 buf = buf + " + " + str(conv[9*k+l]) + " x" + str(i) + "_" + str(4*j+3-l)
            #             if 4 <= l and l <= 7:
            #                 buf = buf + " + " + str(conv[9*k+l]) + " x" + str(i+1) + "_" + str(Perm[4*j+7-l])
            #             if l == 8:
            #                 buf = buf + " >= -" + str(conv[9*k+l]) + "\n"
            #         if conv[9*k+l] < 0:
            #             if l <= 3:
            #                 buf = buf + " - " + str(-conv[9*k+l]) + " x" + str(i) + "_" + str(4*j+3-l)
            #             if 4 <= l and l <= 7:
            #                 buf = buf + " - " + str(-conv[9*k+l]) + " x" + str(i+1) + "_" + str(Perm[4*j+7-l])
            #             if l == 8:
            #                 buf = buf + " >= " + str(-conv[9*k+l]) + "\n"
            #         if conv[9*k+l] == 0:
            #             if l == 8:
            #                 buf = buf + " >= " + str(conv[9*k+l]) + "\n"

            # opOuter.write(buf)
            for k in range(0,21):
                for l in range(0,9):
                    if conv[9*k+l] > 0:
                        if l <= 3:
                            buf = buf + " + " + str(conv[9*k+l]) + " x" + str(i) + "_" + str(4*j+3-l)
                        if 4 <= l and l <= 7:
                            buf = buf + " + " + str(conv[9*k+l]) + " y" + str(i) + "_" + str(4*j+7-l)
                        if l == 8:
                            buf = buf + " >= -" + str(conv[9*k+l]) + "\n"
                    if conv[9*k+l] < 0:
                        if l <= 3:
                            buf = buf + " - " + str(-conv[9*k+l]) + " x" + str(i) + "_" + str(4*j+3-l)
                        if 4 <= l and l <= 7:
                            buf = buf + " - " + str(-conv[9*k+l]) + " y" + str(i) + "_" + str(4*j+7-l)
                        if l == 8:
                            buf = buf + " >= " + str(-conv[9*k+l]) + "\n"
                    if conv[9*k+l] == 0:
                        if l == 8:
                            buf = buf + " >= " + str(conv[9*k+l]) + "\n"

            opOuter.write(buf)
        
        buf = ''
        if i != ROUND:
            for j in range(0,IVLBC):
                buf = buf + "u" + str(i) + "_" + str(j) + " - y" + str(i) + "_" + str(Perm[j]) + " = 0\n"   
        opOuter.write(buf)

        for j in range(0, 4):
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8), "u" + str(i) + "_" + str(j * 16 + 4), "u" + str(i) + "_" + str(j * 16 + 8) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 1), "u" + str(i) + "_" + str(j * 16 + 5), "u" + str(i) + "_" + str(j * 16 + 9) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 2), "u" + str(i) + "_" + str(j * 16 + 6), "u" + str(i) + "_" + str(j * 16 + 10) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 3), "u" + str(i) + "_" + str(j * 16 + 7), "u" + str(i) + "_" + str(j * 16 + 11) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 4), "u" + str(i) + "_" + str(j * 16), "u" + str(i) + "_" + str(j * 16 + 12) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 5), "u" + str(i) + "_" + str(j * 16 + 1), "u" + str(i) + "_" + str(j * 16 + 13) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 6), "u" + str(i) + "_" + str(j * 16 + 2), "u" + str(i) + "_" + str(j * 16 + 14) ))
            opOuter.write(Constraints_XOR( "d" + str(i) + "_" + str(j * 8 + 7), "u" + str(i) + "_" + str(j * 16 + 3), "u" + str(i) + "_" + str(j * 16 + 15) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16), "d" + str(i) + "_" + str(j * 8), "u" + str(i) + "_" + str(j * 16 + 12) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 1), "d" + str(i) + "_" + str(j * 8 + 1), "u" + str(i) + "_" + str(j * 16 + 13) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 2), "d" + str(i) + "_" + str(j * 8 + 2), "u" + str(i) + "_" + str(j * 16 + 14) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 3), "d" + str(i) + "_" + str(j * 8 + 3), "u" + str(i) + "_" + str(j * 16 + 15) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 4), "d" + str(i) + "_" + str(j * 8 + 4), "u" + str(i) + "_" + str(j * 16 + 8) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 5), "d" + str(i) + "_" + str(j * 8 + 5), "u" + str(i) + "_" + str(j * 16 + 9) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 6), "d" + str(i) + "_" + str(j * 8 + 6), "u" + str(i) + "_" + str(j * 16 + 10) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 7), "d" + str(i) + "_" + str(j * 8 + 7), "u" + str(i) + "_" + str(j * 16 + 11) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 8), "d" + str(i) + "_" + str(j * 8 + 4), "u" + str(i) + "_" + str(j * 16 + 4) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 9), "d" + str(i) + "_" + str(j * 8 + 5), "u" + str(i) + "_" + str(j * 16 + 5) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 10), "d" + str(i) + "_" + str(j * 8 + 6), "u" + str(i) + "_" + str(j * 16 + 6) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 11), "d" + str(i) + "_" + str(j * 8 + 7), "u" + str(i) + "_" + str(j * 16 + 7) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 12), "d" + str(i) + "_" + str(j * 8), "u" + str(i) + "_" + str(j * 16) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 13), "d" + str(i) + "_" + str(j * 8 + 1), "u" + str(i) + "_" + str(j * 16 + 1) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 14), "d" + str(i) + "_" + str(j * 8 + 2), "u" + str(i) + "_" + str(j * 16 + 2) ))
            opOuter.write(Constraints_XOR( "x" + str(i+1) + "_" + str(j * 16 + 15), "d" + str(i) + "_" + str(j * 8 + 3), "u" + str(i) + "_" + str(j * 16 + 3) ))         
         
    buf = ''
    if len(FixList) == 0:
        for i in range(0,IVLBC):
            buf = buf + "x0_" + str(i)
            if i != (IVLBC-1):
                buf = buf + " + "
            if i == (IVLBC-1):
                buf = buf + " >= 1\n"
        for i in BanList:
            for j in range(0,len(i)):
                buf = buf + "a" + str(i[j][0]) + "_" + str(i[j][1])
                if j != len(i)-1:
                    buf = buf + " + "
                else:
                    buf = buf + " <= " + str(len(i)-1) + '\n'
    else:    
        fl = []
        for i in range(0,IVLBC):
            fl.append(i)
            if fl in FixList:
                buf = buf + "x0_" + str(i) + " = 1\n"
            else:
                buf = buf + "x0_" + str(i) + " = 0\n"
            fl.pop()
    opOuter.write(buf)
   
    buf = ''
    for i in range(0,ROUND):
        buf = ''
        for j in range(0,s_boxes):
            buf = buf + "a" + str(i) + "_" + str(j)
            if j != (s_boxes-1):
                buf = buf + " + "
            if j == (s_boxes-1):
                buf = buf + " <= "+str(max_sbox_round)+"\n"
        opOuter.write(buf)
        
    buf = ''
    for i in range(0,ROUND):
        for j in range(0,s_boxes):
            buf = buf + "a" + str(i) + "_" + str(j)
            if i != ROUND-1 or j != (s_boxes-1):
                buf = buf + " + "
            else:
                buf = buf + " >= "
    
    buf = buf + str(min_sbox) + "\n"
    
    opOuter.write(buf)

    opOuter.write("Binary\n")
    buf = ''
    for i in range(0,ROUND):
        buf = ''
        for j in range(0,s_boxes):
            buf = buf + "a" + str(i) + "_" + str(j) + "\n"
        opOuter.write(buf)
        
    for i in range(0,ROUND):
        buf = ''
        for j in range(0,IVLBC):
            buf = buf + "x" + str(i) + "_" + str(j) + "\n"
            buf = buf + "y" + str(i) + "_" + str(j) + "\n"
            buf = buf + "u" + str(i) + "_" + str(j) + "\n"
        
        for j in range(0,int(IVLBC/2)):
            buf = buf + "d" + str(i) + "_" + str(j) + "\n"
        opOuter.write(buf)

    buf = ''
    for j in range(0,IVLBC):
        buf = buf + "x" + str(ROUND) + "_" + str(j) + "\n"
    opOuter.write(buf)
    opOuter.close()


def PrintInner(FixList, SolveList):
    opInner = open("Inner" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND)+"_" + str(attack_type) +".lp","w+")
    opInner.write("Minimize\n")
    buf = ''
    
    for i in range(0,len(SolveList)):
        buf = buf + "2 z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_0 + 3 z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_1"
        if i != len(SolveList)-1:
            buf = buf + " + "
        else:
            buf = buf + "\n"
    opInner.write(buf)
    opInner.write("Subject to\n")
    ##################
    if (fix==True):
        for b in range(0,len(fix_bit)):
            buf = ''
            for j in range(0,IVLBC):
                if(j in fix_bit[b]):
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 1\n"
                else:
                    buf = buf + "x" + str(fix_pos[b]) + "_" + str(j) + " = 0\n"
            opInner.write(buf)
    #################
            
    buf = ''
    for i in range(0,len(SolveList)):
        buf = ''
        for k in range(0,4):
            buf = buf + "4 x" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+k)
            if k != 3:
                buf = buf + " + "
        for k in range(0,4):
            buf = buf + " - y" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+k)
        buf = buf + " >= 0\n"
        for k in range(0,4):
            buf = buf + "4 y" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+k)
            if k != 3:
                buf = buf + " + "
        for k in range(0,4):
            buf = buf + " - x" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+k)
        buf = buf + " >= 0\n"
        opInner.write(buf)
    
        buf = ''
        for k in range(0,20):
            for l in range(0,11):
                if convpbl[11*k+l] > 0:
                    if l <= 3:
                        buf = buf + " + " + str(convpbl[11*k+l]) + " x" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+3-l)
                    if 4 <= l and l <= 7:
                        buf = buf + " + " + str(convpbl[11*k+l]) + " y" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+7-l)
                    if 8 <=l and l <= 9:
                        buf = buf + " + " + str(convpbl[11*k+l]) + " z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_" + str(l-8)
                    if l == 10:    
                        buf = buf + " >= -" + str(convpbl[11*k+l]) + "\n"
                if convpbl[11*k+l] < 0:
                    if l <= 3:
                        buf = buf + " - " + str(-convpbl[11*k+l]) + " x" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+3-l)
                    if 4 <= l and l <= 7:
                        buf = buf + " - " + str(-convpbl[11*k+l]) + " y" + str(SolveList[i][0]) + "_" + str(4*SolveList[i][1]+7-l)
                    if 8 <= l and l <= 9:
                        buf = buf + " - " + str(-convpbl[11*k+l]) + " z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_" + str(l-8)
                    if l == 10:
                        buf = buf + " >= " + str(-convpbl[11*k+l]) + "\n"
                if convpbl[11*k+l] == 0:
                    if l == 10:
                        buf = buf + " >= " + str(convpbl[11*k+l]) + "\n"

        opInner.write(buf)
    
    buf = ''
    # sl = []
    d_list=[]
    
    for i in range(0,ROUND):
        buf = ''
        sl = []
        sl.append(i)
        for j in range(0,s_boxes):
            sl.append(j)

            if sl not in SolveList:
                for k in range(0,4):
                    buf = buf + "x" + str(i) + "_" + str(4*j+k) + " = 0\n"
                    buf = buf + "y" + str(i) + "_" + str(4*j+k) + " = 0\n"
            sl.pop()

        if i != ROUND:
            for j in range(0,IVLBC):
                buf = buf + "u" + str(i) + "_" + str(j) + " - y" + str(i) + "_" + str(Perm[j]) + " = 0\n"
        opInner.write(buf)
  
        A_0_to_3=[]
        A_4_to_7=[]
        A_8_to_11=[]
        A_12_to_15=[]
        for j in range(0,len(SolveList)):
            if SolveList[j][0] == i:
                if SolveList[j][1] == 3 or SolveList[j][1] == 6 or SolveList[j][1] == 9 or SolveList[j][1] == 12:
                    A_0_to_3.append(SolveList[j][1])
                elif SolveList[j][1] == 0 or SolveList[j][1] == 7 or SolveList[j][1] == 10 or SolveList[j][1] == 13:
                    A_4_to_7.append(SolveList[j][1])
                elif SolveList[j][1] == 1 or SolveList[j][1] == 4 or SolveList[j][1] == 11 or SolveList[j][1] == 14:
                    A_8_to_11.append(SolveList[j][1])
                elif SolveList[j][1] == 2 or SolveList[j][1] == 5 or SolveList[j][1] == 8 or SolveList[j][1] == 15:
                    A_12_to_15.append(SolveList[j][1])
        # print("A_0_to_3=",A_0_to_3)
        # print("A_4_to_7=",A_4_to_7)
        # print("A_8_to_11=",A_8_to_11)
        # print("A_12_to_15=",A_12_to_15)
        buf = ''
        mcl=[]
        if len(A_0_to_3)!=0:
            mcl.append(0)
        if len(A_4_to_7)!=0:
            mcl.append(1)
        if len(A_8_to_11)!=0:
            mcl.append(2)
        if len(A_12_to_15)!=0:
            mcl.append(3)
        # print("mcl=",mcl)

        d_list.append(mcl)

        for k in mcl:
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8), "u" + str(i) + "_" + str(k * 16 + 4), "u" + str(i) + "_" + str(k * 16 + 8) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 1), "u" + str(i) + "_" + str(k * 16 + 5), "u" + str(i) + "_" + str(k * 16 + 9) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 2), "u" + str(i) + "_" + str(k * 16 + 6), "u" + str(i) + "_" + str(k * 16 + 10) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 3), "u" + str(i) + "_" + str(k * 16 + 7), "u" + str(i) + "_" + str(k * 16 + 11) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 4), "u" + str(i) + "_" + str(k * 16), "u" + str(i) + "_" + str(k * 16 + 12) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 5), "u" + str(i) + "_" + str(k * 16 + 1), "u" + str(i) + "_" + str(k * 16 + 13) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 6), "u" + str(i) + "_" + str(k * 16 + 2), "u" + str(i) + "_" + str(k * 16 + 14) ))
            opInner.write(Constraints_XOR( "d" + str(i) + "_" + str(k * 8 + 7), "u" + str(i) + "_" + str(k * 16 + 3), "u" + str(i) + "_" + str(k * 16 + 15) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16), "d" + str(i) + "_" + str(k * 8), "u" + str(i) + "_" + str(k * 16 + 12) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 1), "d" + str(i) + "_" + str(k * 8 + 1), "u" + str(i) + "_" + str(k * 16 + 13) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 2), "d" + str(i) + "_" + str(k * 8 + 2), "u" + str(i) + "_" + str(k * 16 + 14) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 3), "d" + str(i) + "_" + str(k * 8 + 3), "u" + str(i) + "_" + str(k * 16 + 15) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 4), "d" + str(i) + "_" + str(k * 8 + 4), "u" + str(i) + "_" + str(k * 16 + 8) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 5), "d" + str(i) + "_" + str(k * 8 + 5), "u" + str(i) + "_" + str(k * 16 + 9) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 6), "d" + str(i) + "_" + str(k * 8 + 6), "u" + str(i) + "_" + str(k * 16 + 10) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 7), "d" + str(i) + "_" + str(k * 8 + 7), "u" + str(i) + "_" + str(k * 16 + 11) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 8), "d" + str(i) + "_" + str(k * 8 + 4), "u" + str(i) + "_" + str(k * 16 + 4) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 9), "d" + str(i) + "_" + str(k * 8 + 5), "u" + str(i) + "_" + str(k * 16 + 5) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 10), "d" + str(i) + "_" + str(k * 8 + 6), "u" + str(i) + "_" + str(k * 16 + 6) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 11), "d" + str(i) + "_" + str(k * 8 + 7), "u" + str(i) + "_" + str(k * 16 + 7) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 12), "d" + str(i) + "_" + str(k * 8), "u" + str(i) + "_" + str(k * 16) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 13), "d" + str(i) + "_" + str(k * 8 + 1), "u" + str(i) + "_" + str(k * 16 + 1) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 14), "d" + str(i) + "_" + str(k * 8 + 2), "u" + str(i) + "_" + str(k * 16 + 2) ))
            opInner.write(Constraints_XOR( "x" + str(i+1) + "_" + str(k * 16 + 15), "d" + str(i) + "_" + str(k * 8 + 3), "u" + str(i) + "_" + str(k * 16 + 3) ))
    # print("d_list=",d_list)

        # buf = ''
        # if i != ROUND-1:        
        #     for j in range(0,4):
        #         if j not in mcl:
        #             for k in range(0,16):
        #                 buf = buf + "x" + str(i+1) + "_" + str(16*j+k) + " = 0\n"
        #                 buf = buf + "y" + str(i+1) + "_" + str(16*j+k) + " = 0\n"
        #     opInner.write(buf)


    if len(FixList) == 0:
        for j in SolveList:
            if j[0] == 0:
                buf = buf + "x0_" + str(4*j[1]) + " + x0_" + str(4*j[1]+1) + " + x0_" + str(4*j[1]+2) + " + x0_" + str(4*j[1]+3)
                buf = buf + " >= 1\n"
        opInner.write(buf)
    else:
        fl = []

        for j in range(0,IVLBC):
            fl.append(i)
            if fl in FixList:
                buf = buf + "x0_" + str(j) + " = 1\n"
            else:
                buf = buf + "x0_" + str(j) + " = 0\n"
            fl.pop()
        opInner.write(buf)
    
    buf = ''        
    for j in range(0,4):
        if j not in mcl:
            for k in range(0,16):
                buf = buf + "x" + str(ROUND) + "_" + str(16*j+k) + " = 0\n"
    opInner.write(buf)

    buf = ''    
    opInner.write("Binary\n")
    buf = ''
    for i in range(0,ROUND):
        for j in range(0,IVLBC):
            buf = buf + "x" + str(i) + "_" + str(j) + "\n"
        for j in range(0,IVLBC):
            buf = buf + "y" + str(i) + "_" + str(j) + "\n"
        for j in range(0,IVLBC):
            buf = buf + "u" + str(i) + "_" + str(j) + "\n"
        for j in d_list[i]:
            for k in range(0,8):
                buf = buf + "d" + str(i) + "_" + str(8*j+k) + " \n"
        opInner.write(buf)         

    buf = ''
    for j in range(0,IVLBC):
        buf = buf + "x" + str(ROUND) + "_" + str(j) + "\n"
    opInner.write(buf)

    buf = ''
    for i in range(0,len(SolveList)):
        buf = buf + "z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_0\n"
        buf = buf + "z" + str(SolveList[i][0]) + "_" + str(SolveList[i][1]) + "_1\n"
        opInner.write(buf)
        buf = ''
    opInner.close()

def strtoint(s):
    reg = 0
    s1 = ''
    s2 = ''
    res = 0
    result = []
    for i in range(0,len(s)):
        if s[i] == '_':
            reg = 1
        if s[i] >= '0' and s[i]<= '9':
            if reg == 0:
                s1 = s1 + s[i]
            if reg == 1:
                s2 = s2 + s[i]

    result.append(int(s1))
    result.append(int(s2))    
    return result

def strtoint2(s):
    reg = 0
    s1 = ''
    s2 = ''
    res = 0
    result = []
    for i in range(0,len(s)):
        if s[i] == '_':
            reg = 1
        if s[i] >= '0' and s[i]<= '9':
            if reg == 0:
                s1 = s1 + s[i]
            if reg == 1:
                s2 = s2 + s[i]
        
    #result.append(string.atoi(s1))
    result.append(string.atoi(s2))
    return result

def print_binary_data(data,prob):
    for i in range(0,len(data),4):
        print(data[i:i+4],end='  ');
    print(":: Hex => ",end='');
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end='  ')
    print(" :: ",end='0x')
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end='')
    print(" :: Probability => 2^{-"+str(prob)+"}")
    print("");
    
def print_binary_data_1(data):
    for i in range(0,len(data),4):
        print(data[i:i+4],end='  ');
    print(":: Hex => ",end='');
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end='  ')
    print(" :: ",end='0x')
    for i in range(0,len(data),16):
        print(hex(int(data[i:i+16],2))[2:].zfill(4),end='')
    print("");

def shift(n,d,N):
    return ((n << d) % (1 << N) | (n >> (N-d) ))


filename = "Result" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND) +"_" + str(attack_type) + ".txt"
opResult = open(filename,'w+')

def possible_differential():
    count = 1
    fsl = []
    fslstring = []
    ftlstring = []
    BanList = []
    bl = []
    FixList = []    
    while (count<=int(sys.argv[6])):
        PrintOuter(FixList,BanList)
        ###########################GUROBI#################################
        if(GUROBI_EXISTS == True):
            o = read("Outer" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND) +"_" + str(attack_type) +".lp")
            o.optimize()
            obj = o.getObjective()
        ##########################CPLEX####################################
        if(CPLEX_EXISTS == True):
            mr = ModelReader()
            o = mr.read("Outer" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND) +"_" + str(attack_type) +".lp")
            o_sol  = o.solve(log_output=True)
            
        ###########################GUROBI#################################
        if(GUROBI_EXISTS == True):
            o_obj = obj.getValue()
        ##################CPELX###############
        if(CPLEX_EXISTS == True):
            o_obj = o_sol.get_objective_value()
        if o_obj < (min_sbox + 64) :
            b1=[]
            fsl = []
            fslstring = []
            ###########################GUROBI#############################
            if(GUROBI_EXISTS == True):
                for v in o.getVars():
                    if v.x == 1 and v.VarName[0] == 'a':
                        fslstring.append(v.VarName)
            ###########CPLEX###########################
            if(CPLEX_EXISTS == True):
                for v in o_sol.iter_variables():
                    if ('a' in str(v)):
                        fslstring.append(str(v))
            for f in fslstring:
                fsl.append(strtoint(f))
            #if count == 1:
            for f in fslstring:
                bl.append(strtoint(f))
            BanList.append(bl)
            print("*\n*\n*\n*\n")
            print(BanList)
            print("*\n*\n*\n*\n")
            
            print(fsl)
            PrintInner(FixList,fsl)
            
            FixList = []
            ###########################GUROBI#################################
            if(GUROBI_EXISTS == True):
                i = read("Inner" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND) + "_" + str(attack_type) +".lp")
                i.optimize()
                i_obj = i.getObjective().getValue()
            ###################CPLEX#############################
            if(CPLEX_EXISTS == True):
                i = mr.read("Inner" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND) + "_" + str(attack_type) +".lp")
                i_sol  = i.solve(log_output=True)
                i_obj = i_sol.get_objective_value()
            print("Number of Active S-boxes: " + str(o_obj))  
            print("FOUND Optimal Probability: " + str(i_obj))
            #if i_obj > IVLBC:
            #    break
            buf = ''
            buf = buf + str(fsl) + " " + str(i_obj) + "\n"
            
            ftlstring = []
            ###########################GUROBI#################################
            if(GUROBI_EXISTS == True):
                for v in i.getVars():
                    if v.x == 1:
                        buf = buf + v.VarName + " "
                    if v.x == 1 and v.VarName[0] == 'x' and v.VarName[1] == str(ROUND-2):
                        ftlstring.append(v.VarName)
            ############CPLEX##################################################
            if(CPLEX_EXISTS == True):
                for v in i_sol.iter_variables():
                    buf = buf + str(v) + " "
                    #if(fix==True):
                    if (('x' in str(v)) and (str(v).split("_")[0][1:] == str(ROUND)) ):
                            ftlstring.append(str(v))
            if(fix==True):
                for f in ftlstring:
                    FixList.append(strtoint2(f))
            
            buf = buf + "\n"
            opResult.write(buf)
            opResult.flush()
            round_bit_arr  = []
            round_bit_arr_y = []
            round_bit_arr_u = []
            prob_arr = []
            ###########################GUROBI#################################
            if(GUROBI_EXISTS == True):
                for v in i.getVars():
                    if v.x == 1:
                        var = v.VarName
                        if (var[0] == 'x'):
                            round_bit_arr += [strtoint(var)]
                        elif (var[0] == 'y'):
                            round_bit_arr_y += [strtoint(var)]
                        elif (var[0] == 'u'):
                            round_bit_arr_u += [strtoint(var)]
                        elif (var[0] == 'z'):
                            new_var = var.split("_");
                            prob_arr += [strtoint("_".join([new_var[0],new_var[2]]))]

            ############CPLEX################
            if(CPLEX_EXISTS == True):
                for v in i_sol.iter_variables():
                        var = str(v)
                        if (var[0] == 'x'):
                            round_bit_arr += [strtoint(var)]
                        elif (var[0] == 'y'):
                            round_bit_arr_y += [strtoint(var)]
                        elif (var[0] == 'z'):
                            new_var = var.split("_");
                            prob_arr += [strtoint("_".join([new_var[0],new_var[2]]))]
    
            no_of_rounds = max([_[0] for _ in round_bit_arr])
            print(round_bit_arr,"no_of_rounds=",no_of_rounds)
            print("Differential Probability for " + str(no_of_rounds) + " rounds of IVLBC_"+str(IVLBC)+" is 2^{-" + str(i_obj) + "}")
            for r in range(0,ROUND+1):
                print("The input difference of the round "+ str(r+1)+" is: ");
                diff_bits = list("0"*IVLBC);
                diff_bits_y = list("0"*IVLBC);
                diff_bits_u = list("0"*IVLBC);
                active_bits = [a[1] for a in round_bit_arr if a[0]==r]
                active_bits_y = [a[1] for a in round_bit_arr_y if a[0]==r]
                active_bits_u = [a[1] for a in round_bit_arr_u if a[0]==r]
                for bit in active_bits:
                    diff_bits[len(diff_bits)-1-bit] = "1";
                for bit in active_bits_y:
                    diff_bits_y[len(diff_bits_y)-1-bit] = "1";
                for bit in active_bits_u:
                    diff_bits_u[len(diff_bits_u)-1-bit] = "1";
                probability = 0;
                if (r>0):
                    round_prob  = [a[1] for a in prob_arr if a[0]==r-1]
                    for prob in round_prob:
                        if (prob==1):
                            probability += 3;
                        elif (prob==0):
                            probability += 2;
                print_binary_data("".join(diff_bits),probability);
                print("\n")
                if r!=ROUND:
                    print_binary_data_1("".join(diff_bits_y));
                    print("\n")
                if r!=ROUND:
                    print_binary_data_1("".join(diff_bits_u));
                    print("\n")
            count = count + 1     
        else:
            continue

def impossible_differential():
    iter_count_0 = IVLBC
    iter_count_1 = 1
    global fix_diff;
    global fix_diff_bin;
    while True:
        PrintOuter([],[])
        iter_count_1 = iter_count_1 + 1
        ###########################GUROBI#################################
        if(GUROBI_EXISTS == True):
            o = read("Outer" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND)  + "_" + str(attack_type) +".lp")
            o.optimize()
            solCount = o.getAttr("SolCount")
        ##########################CPLEX####################################
        if(CPLEX_EXISTS == True):
            mr = ModelReader()
            o = mr.read("Outer" +"_IVLBC_" + str(IVLBC) + "_" + str(ROUND)  + "_" + str(attack_type) +".lp")
            o_sol  = o.solve(log_output=True)
            if (o_sol==None):
                solCount = 0
            else:
                solCount = 1
        ##########################GUROBI#################################
        if(solCount!=0):
            print([hex(e)[2:].zfill(int(IVLBC/4)) for e in fix_diff])
            print ("Iteratino No. - " + str(iter_count_0) + "_"+ str(iter_count_1) + "\n")
            print("No. of Solultions: " + str(solCount)+"\n")  
            #fix_diff[1] = fix_diff[1] << 1 
            fix_diff[1] = shift(fix_diff[1],1,IVLBC) 
            if (iter_count_1==IVLBC):
                iter_count_0 = iter_count_0 - 1
                fix_diff[0] = shift(fix_diff[0],1,IVLBC) 
                fix_diff[1] = 0x0000000000000001
                iter_count_1 = 0
            fix_diff_bin = [bin(diff)[2:].zfill(IVLBC) for diff in fix_diff];
            fix_bit = [];
            for diff_1 in fix_diff_bin:
                fix_bit.append([len(diff_1)-1-i for i in range(0,len(diff_1)) if diff_1[i]=="1" ])
            continue
        else:       
                print([bin(e)[2:].zfill(IVLBC) for e in fix_diff])
                print([hex(e)[2:].zfill(int(IVLBC/4)) for e in fix_diff])
                break;      
  
if (attack_type=="possible"):
    possible_differential()
if (attack_type=="impossible"):
    impossible_differential()
    
opResult.close()

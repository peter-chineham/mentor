"""
   GENERATE SAMPLE NETWORKS TO TEST AND EXHIBIT ALGORITHMS

   Coordinate Model: V&H coords of 92 large cities

   Node Model: random cities(R) / largest cities(L) / specific cities(S)

   Distance Model: Dist[i][j] = eucl(i,j)/sqrt(10)
      where eucl(i,j) is the Euclidean distance between i and j

   Link Cost Model: (single capacity) - cost = dist
              (multicapacity) - Ncap  (CFlag='D')
         c[k][i][j] = FixedCD[k] + VarCD[k] * Dist[i][j]
              (continuous capacity) - (CFLAG='C')
         c[i][j] = Dist[i][j] * ( FixedCD + Cap[0] ^ VarCD[0] )

   Requirements Model:
     r[i][j] = FixedTraf
                 * ( 1 - RandTraf + 2*RandTraf*rand() )
                 * ( 1 - VarTrafD * Dist[i][j]/MaxDist )
                 * ( 1 + VarTrafP * Pop[i]*Pop[j]/(MaxPop^2) )
     where MaxDist and MaxPop are the max of Dist[i][j] anf Pop[i]
"""

from random import random, randrange
from math  import sqrt
import config

NN = 96                 # max number of nodes
NC = 3                  # max number of line capacities

v     = 0
h     = 1
city  = 2
state = 3
pop   = 4
index = 5
ndata = [[5004 ,  1405 , "NYK" , "NY" ,  7263,  0] ,
         [9217 ,  7856 , "LSA" , "CA" ,  3259,  1] ,
         [5986 ,  3426 , "CHI" , "IL" ,  3010,  2] ,
         [8435 ,  4035 , "DAL" , "TX" ,  1004,  3] ,
         [5499 ,  1582 , "BAL" , "MD" ,   753,  4] ,
         [8495 ,  8729 , "SFO" , "CA" ,   749,  5] ,
         [8364 ,   545 , "MIA" , "FL" ,   374,  6] ,
         [7498 ,  5898 , "DEN" , "CO" ,   505,  7] ,
         [7027 ,  4202 , "KCY" , "MO" ,   441,  8] ,
         [6336 ,  8896 , "SEA" , "WA" ,   486,  9] ,
         [7259 ,  2085 , "ATL" , "GA" ,   422, 10] ,
         [6402 ,  1639 , "GRN" , "NC" ,   177, 11] ,
         [6823 ,  4674 , "LIN" , "NE" ,   183, 12] ,
         [8447 ,  2861 , "BTR" , "LA" ,   241, 13] ,
         [5942 ,  2983 , "FWA" , "IN" ,   173, 14] ,
         [9130 ,  6738 , "PHO" , "AZ" ,   894, 15] ,
         [8458 ,  4108 , "FWO" , "TX" ,   430, 16] ,
         [5536 ,  2829 , "DET" , "MI" ,  1086, 17] ,
         [5785 ,  3582 , "MIL" , "WI" ,   605, 18] ,
         [5780 ,  4526 , "MIN" , "MN" ,   357, 19] ,
         [5637 ,  2472 , "AKR" , "OH" ,   222, 20] ,
         [8547 ,  5878 , "ALB" , "NM" ,   351, 21] ,
         [8266 ,  5075 , "AMA" , "TX" ,   166, 22] ,
         [9250 ,  7810 , "ANA" , "CA" ,   241, 23] ,
         [8456 ,  4064 , "ARL" , "TX" ,   250, 24] ,
         [7495 ,  5877 , "AUR" , "CO" ,   218, 25] ,
         [8984 ,  4011 , "AUS" , "TX" ,   467, 26] ,
         [7518 ,  2446 , "BIR" , "AL" ,   278, 27] ,
         [4427 ,  1251 , "BOS" , "MA" ,   574, 28] ,
         [5076 ,  2327 , "BUF" , "NY" ,   325, 29] ,
         [9475 ,  3739 , "CHR" , "TX" ,   264, 30] ,
         [6673 ,  1706 , "CHA" , "NC" ,   342, 31] ,
         [7097 ,  2357 , "CHT" , "TN" ,   162, 32] ,
         [6263 ,  2680 , "CIN" , "OH" ,   370, 33] ,
         [5586 ,  2557 , "CLE" , "OH" ,   547, 34] ,
         [7680 ,  5813 , "COL" , "CO" ,   273, 35] ,
         [5972 ,  2554 , "CLM" , "OH" ,   566, 36] ,
         [6112 ,  2704 , "DAY" , "OH" ,   179, 37] ,
         [6480 ,  4293 , "DES" , "IA" ,   192, 38] ,
         [9231 ,  5655 , "ELP" , "TX" ,   492, 39] ,
         [8280 ,   573 , "FTL" , "FL" ,   162, 40] ,
         [8658 ,  8241 , "FRE" , "CA" ,   285, 41] ,
         [8404 ,  4015 , "GAR" , "TX" ,   177, 42] ,
         [5628 ,  3261 , "GRA" , "MI" ,   187, 43] ,
         [8938 ,  3536 , "HOU" , "TX" ,  1729, 44] ,
         [9280 ,  7820 , "HUN" , "CA" ,   184, 45] ,
         [7267 ,  2534 , "HVL" , "AL" ,   163, 46] ,
         [6272 ,  2992 , "IND" , "IN" ,   720, 47] ,
         [8044 ,  2883 , "JAC" , "MS" ,   208, 48] ,
         [7628 ,  1240 , "JVL" , "FL" ,   610, 49] ,
         [5003 ,  1415 , "JCY" , "NJ" ,   219, 50] ,
         [6801 ,  2251 , "KNO" , "TN" ,   173, 51] ,
         [8669 ,  7431 , "LAS" , "NV" ,   192, 52] ,
         [6460 ,  2562 , "LEX" , "KY" ,   213, 53] ,
         [7728 ,  3470 , "LRK" , "AR" ,   181, 54] ,
         [9251 ,  7859 , "LNB" , "CA" ,   396, 55] ,
         [6498 ,  2762 , "LOU" , "KY" ,   286, 56] ,
         [8598 ,  4962 , "LUB" , "TX" ,   186, 57] ,
         [5885 ,  3785 , "MAD" , "WI" ,   176, 58] ,
         [7467 ,  3110 , "MEM" , "TN" ,   653, 59] ,
         [9125 ,  6685 , "MES" , "AZ" ,   251, 60] ,
         [8175 ,  2384 , "MOB" , "AL" ,   203, 61] ,
         [7686 ,  2240 , "MON" , "AL" ,   194, 62] ,
         [7009 ,  2711 , "NAS" , "TN" ,   474, 63] ,
         [5016 ,  1430 , "NRK" , "NJ" ,   316, 64] ,
         [8460 ,  2628 , "NWO" , "LA" ,   554, 65] ,
         [5917 ,  1223 , "NOR" , "VA" ,   275, 66] ,
         [8486 ,  8696 , "OAK" , "CA" ,   357, 67] ,
         [7946 ,  4372 , "OKL" , "OK" ,   446, 68] ,
         [6708 ,  4577 , "OMA" , "NE" ,   349, 69] ,
         [5241 ,  1466 , "PHI" , "PA" ,  1643, 70] ,
         [5619 ,  2184 , "PIT" , "PA" ,   387, 71] ,
         [6799 ,  8915 , "POR" , "OR" ,   388, 72] ,
         [6344 ,  1434 , "RAL" , "NC" ,   180, 73] ,
         [5906 ,  1462 , "RIC" , "VA" ,   218, 74] ,
         [9202 ,  7718 , "RIV" , "CA" ,   197, 75] ,
         [4913 ,  2195 , "ROC" , "NY" ,   236, 76] ,
         [8303 ,  8581 , "SAC" , "CA" ,   324, 77] ,
         [9225 ,  4063 , "SAN" , "TX" ,   914, 78] ,
         [9466 ,  7644 , "SDG" , "CA" ,  1015, 79] ,
         [8575 ,  8632 , "SNJ" , "CA" ,   712, 80] ,
         [9277 ,  7800 , "STA" , "CA" ,   237, 81] ,
         [8271 ,  3495 , "SHR" , "LA" ,   220, 82] ,
         [6242 ,  8179 , "SPO" , "WA" ,   173, 83] ,
         [6807 ,  3483 , "STL" , "MO" ,   426, 84] ,
         [8435 ,  8531 , "STO" , "CA" ,   183, 85] ,
         [5776 ,  4499 , "STP" , "MN" ,   264, 86] ,
         [8230 ,  1165 , "SPT" , "FL" ,   239, 87] ,
         [8172 ,  1147 , "TAM" , "FL" ,   278, 88] ,
         [5703 ,  2820 , "TOL" , "OH" ,   341, 89] ,
         [9340 ,  6458 , "TUC" , "AZ" ,   359, 90] ,
         [7694 ,  4149 , "TUL" , "OK" ,   374, 91] ,
         [5916 ,  1205 , "VIR" , "VA" ,   333, 92] ,
         [5623 ,  1586 , "WDC" , "DC" ,   626, 93] ,
         [7489 ,  4520 , "WIC" , "KS" ,   289, 94] ,
         [4954 ,  1420 , "YON" , "NY" ,   186, 95]]
Vcoor = []
Hcoor = []
node  = []
pvpop = []

def NetGenRpt(inp):
    nn = inp.nn

    log_file = open('netgen.rpt', 'w')
    log_file.write("\nNetGen Report\n")
    log_file.write("\n---------- NODES ----------\n")

    if config.NG_KERSH:
        log_file.write("__I ___V ___H ___X ___Y POPU CIT\n")
        for i in range(nn):
            log_file.write("%3d %4d %4d %4d %4d %4d %3s\n" % (i , Vcoor[i], Hcoor[i], inp.Xcoor[i], inp.Ycoor[i], ndata[i][pop], inp.Nname[i]))
    else:
        log_file.write("__I  NAME ___X ___Y POPU\n")
        for i in range(nn):
            log_file.write("%3d %5s %4d %4d %4d\n" % (i, inp.Nname[i], inp.Xcoor[i], inp.Ycoor[i], pvpop[i]))

#    if config.NG_KERSH:
#        log_file.write("\n------- DISTS miles -------\n")
#    else:
#        log_file.write("\n------- DISTS km -------\n")
#    for i in range(nn):
#        for j in range(nn):
#            log_file.write("%8.0f" % (inp.dist[i][j]))
#        log_file.write("\n")

    log_file.write("\n------- REQS  -------\n")
    for i in range(nn):
        for j in range(nn):
            log_file.write("%8.0f"% (inp.req[i][j]))
        log_file.write("\n")

    log_file.close()     
    
def VHtoMiles(xi, xj, yi, yj):
    # V&H coords to miles (Integer)
    dx = float(xi - xj)
    dy = float(yi - yj)
    x = dx * dx + dy * dy
    x = sqrt(0.1 * x)
    return int(x)

# Generate Network
def NetGen_AK(inp):
    global Vcoor, Hcoor, node
    
    nn = inp.nn
    NetGen.first = True

    # Allocate memory
    if nn <= 0 or nn > NN:
        print("Invalid number of nodes (1-" + NN + ") " + nn)
        return
    if NetGen.first:
        NetGen.first = False
    else:
        answer = ""
        print("Erase old net? (y,n): ")
        input(answer)
        if answer[0] != 'y':
            return
   
    # Allocate the node Arrays
    Vcoor   = [0    for i in range(nn)]
    Hcoor   = [0    for i in range(nn)]

    # Allocate the link arrays
    config.np = ( nn * (nn-1) ) // 2

    # Allocate local arrays
    node   = [0.0 for i in range(config.np)]
    value  = [0.0 for i in range(config.np)]

    # Select locations
    nmodel = config.NG_NMODEL
    if nmodel == 'S':
        # Load first nn specific city names from file (discard remainder)
        fc = open(config.NG_CFNAME, 'r')
        for i in range(nn):
            inp.Nname[i] = fc.readline().strip() # remove lf and trailing spaces
        fc.close()
        # find the chosen cities in the node list
        for i in range(nn):
            node[i] = -1
            for j in range(NN):  # could be anywhere in list of nodes
                if inp.Nname[i] == ndata[j][city]:
                    node[i]= j
                    break
            if node[i] < 0:
                print ("Unrecognized city name %s" % ( inp.Nname[i] ))
                return
    elif nmodel == 'F':
        # Load first nn nodes from node list
        for i in range(nn):
            node[i] = i
    elif nmodel == 'R':
        # Randomly choose nn nodes from the node list
        for i in range(nn):
            flag = True
            while flag:
                flag = False
                n = randrange(NN) # pick an index for ndata
                for j in range(i):
                    if n == node[j]:
                        flag = True
                        break
                node[i] = n
    elif nmodel == 'L':
        # Choose nodes with nn largest populations
        for j in range(nn):
            value[j] = -1
        for i in range(NN):
            if ndata[i][pop] <= value[nn-1]:
                continue
            for j in range(nn-1, -1, -1):
                if ndata[i][pop] <= value[j-1]:
                    break
                node[j] = node[j-1]
                value[j] = value[j-1]
            node[j] = i
            value[j] = ndata[i][pop]
    else:
        print("Unrecognized node model (F,L,R,S): %c" % (nmodel))
        return

    # Compute distance in miles
    MaxDist = 0.0
    MaxPop  = 0.0

    for i in range(nn):
        n = node[i]
        Vcoor[i] = ndata[n][v]
        Hcoor[i] = ndata[n][h]
     
    for i in range(nn):
        ni = node[i]
        MaxPop = max(MaxPop ,ndata[ni][pop])
        for j in range(nn):
            nj = node[j]
#            inp.dist[i][j] = VHtoMiles(ndata[ni][v], ndata[nj][v], ndata[ni][h], ndata[nj][h])
#            MaxDist = max( MaxDist , inp.dist[i][j] )
            dist = VHtoMiles(ndata[ni][v], ndata[nj][v], ndata[ni][h], ndata[nj][h])
            MaxDist = max( MaxDist , dist )

    # Compute requirements
    TotReq = 0.0
    FixedTraf = config.NG_FXTRF
    VarTrafDist = config.NG_VTRFD
    VarTrafPop = config.NG_VTRFP
    RandTraf = config.NG_RNTRF
    if FixedTraf < 0.0 or FixedTraf > 1000000.0:
        print("FixedTraf out of range (0-1000000)")
        return
    if VarTrafDist < 0.0 or VarTrafDist > 1.0:
        print("VarTrafDist out of range (0-1.0)")
        return
    if VarTrafPop < 0.0 or VarTrafPop > 1.0:
        print("VarTrafPop out of range (0-1.0)")
        return
    if RandTraf < 0.0 or RandTraf > 1.0:
        print("RandTraf out of range (0-1.0)")
        return
    for i in range(nn):
        ni = node[i]
        for j in range(nn):
            nj = node[j]
            if ni == nj:
                inp.req[i][j] = 0.0
            else:
                dist = Eucl(inp.Xcoor[i], inp.Ycoor[i], inp.Xcoor[j], inp.Ycoor[j])
#                inp.req[i][j] = (int((FixedTraf
#                    * ( 1 - RandTraf + 2 * RandTraf * random() )
#                    * ( 1 - VarTrafDist * inp.dist[i][j] / MaxDist )
#                    * ( 1 + VarTrafPop  * ndata[ni][pop] * ndata[nj][pop] 
#                    / (MaxPop * MaxPop)))))
                inp.req[i][j] = (int((FixedTraf
                    * ( 1 - RandTraf + 2 * RandTraf * random() )
                    * ( 1 - VarTrafDist * dist / MaxDist )
                    * ( 1 + VarTrafPop  * ndata[ni][pop] * ndata[nj][pop] 
                    / (MaxPop * MaxPop)))))
            TotReq += inp.req[i][j]

    # Compute screen coordinates
    for i in range(nn):
        inp.Xcoor[i] = round((10000 - Hcoor[i]) / 6 - 150, 0)
        inp.Ycoor[i] = round(Vcoor[i] / 6 - 700, 0)

    # Fill in node ids
    for i in range(nn):
        inp.Nname[i] = ndata[node[i]][city]

    # Finish the job
    NetGenRpt(inp)
    config.network_present = True

def Eucl(x1, y1, x2, y2):
    t = ((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2))
    return sqrt(t)

def NetGen_PV(inp):
    global pvpop
    pvpop = [0.0 for i in range(inp.nn)]
    FixedTraf = config.NG_FXTRF
    VarTrafDist = config.NG_VTRFD
    VarTrafPop = config.NG_VTRFP
    RandTraf = config.NG_RNTRF
    MaxPop = 0
    # Coordinates, name and population
    for i in range(inp.nn):
        inp.Xcoor[i]  = randrange(0,config.canvasWidth - 45)
        inp.Ycoor[i]  = randrange(20,config.canvasHeight - 5)
        inp.Nname[i]  = "N" + str(i)
        if config.NG_NHOST != 0:
            if i < config.NG_NHOST:
                pvpop[i] = randrange(100,150)
            else:
                pvpop[i] = randrange(1,50)
        else:
            pvpop[i] = randrange(1,500)
        if pvpop[i] > MaxPop:
            MaxPop = pvpop[i]
    # distances between nodes [and line costs - replaced by distance based]
#    MaxDist = 0
#    for i in range(inp.nn):
#        for j in range(inp.nn):
#            if i == j:
#                inp.dist[i][j] = 0.0
#            else:
#                inp.dist[i][j] = Eucl(inp.Xcoor[i], inp.Ycoor[i], inp.Xcoor[j], inp.Ycoor[j])
#                if inp.dist[i][j] > MaxDist: 
#                    MaxDist = inp.dist[i][j]
    MaxDist = 0
    for i in range(inp.nn):
        for j in range(inp.nn):
            if i != j:
                dist = Eucl(inp.Xcoor[i], inp.Ycoor[i], inp.Xcoor[j], inp.Ycoor[j])
                if dist > MaxDist: 
                    MaxDist = dist

    # Requirements
    for i in range(inp.nn):
        for j in range(inp.nn):
            inp.req[i][j] = 0.0
    if config.NG_NHOST > 0:
        for i in range(inp.nn):
            for j in range(inp.nn):
                if i == j:
                    inp.req[i][j] = 0.0
                elif i < config.NG_NHOST:
                    inp.req[i][j] += (8000 / 120) * pvpop[j]     # each user 1000 bytes from host every 2 mins
                    if j < config.NG_NHOST:
                        inp.req[i][j] += (800  / 120) * pvpop[i] # each user 100 bytes to host every 2 mins
                elif j < config.NG_NHOST:
                    inp.req[i][j] += (800  / 120) * pvpop[i]     # each user 100 bytes to host every 2 mins
    else:
        for i in range(inp.nn):
            for j in range(inp.nn):
                if i == j:
                    inp.req[i][j] = 0.0
                else:
#                    inp.req[i][j] = (int((FixedTraf
#                           * ( 1 - RandTraf + 2 * RandTraf * randrange(0.0, 32767.0) / 32767.0)
#                           * ( 1 - VarTrafDist * inp.dist[i][j] / MaxDist )
#                           * ( 1 + VarTrafPop  * pvpop[i] * pvpop[j] 
#                           / (MaxPop * MaxPop)))))
                    dist = Eucl(inp.Xcoor[i], inp.Ycoor[i], inp.Xcoor[j], inp.Ycoor[j])
                    inp.req[i][j] = (int((FixedTraf
                           * ( 1 - RandTraf + 2 * RandTraf * randrange(0.0, 32767.0) / 32767.0)
                           * ( 1 - VarTrafDist * dist / MaxDist )
                           * ( 1 + VarTrafPop  * pvpop[i] * pvpop[j] 
                           / (MaxPop * MaxPop)))))
    NetGenRpt(inp)
    config.network_present = True

def NetGen(inp):
    config.network_present = False
    config.design_present = False
    if config.NG_KERSH:
        NetGen_AK(inp)
    else:
        NetGen_PV(inp)

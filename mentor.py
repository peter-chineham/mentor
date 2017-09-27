from math import ceil, sqrt

Median = -1
FINFINITY = 1.7976931348623157e+308
spPred = None
Home = None
bkbn = None
Seq = None
Npred = None
log_file = None
trace = False
MN_ALPHA = None
MN_SLACK = None
MN_DPARM = None
MN_RPARM = None
MN_WPARM = None
NetCost  = None
nl       = None
net_file = None
Weight   = None

def Mentor(model_ix, inp, alpha, slack, dparm, rparm, wparm):
    global Median, spPred, Home, bkbn, Seq, Npred, log_file 
    global trace, MN_ALPHA, MN_SLACK, MN_DPARM, MN_RPARM, MN_WPARM
    global NetCost, net_file, Weight
    MN_ALPHA = alpha
    MN_SLACK = slack
    MN_DPARM = dparm
    MN_RPARM = rparm
    MN_WPARM = wparm
    NetCost = 0.0

    net_file = open("Design%d.net" % (model_ix), 'w')
    trace = inp.MN_TRACE
    if trace:
        log_file = open('mentor.txt', 'w')
    nn = inp.nn

    # Write parameters to design file
    net_file.write("P,%d,%s,%f,%s,%d,%d,%s,%f,\n" % (inp.nn, str(inp.MN_BIFUR), 
                                                      inp.MN_DIST1, inp.MN_DUPLEX, 
                                                      inp.MN_MSGLEN, inp.MN_NCAP, 
                                                      str(inp.MN_TRACE), inp.MN_UTIL))
    for i in range(inp.MN_NCAP):
        net_file.write("C,%f,%f,%f,%f,\n" % (inp.MN_CAPS[i], inp.MN_FXCD[i], 
                                             inp.MN_VCD_1[i], inp.MN_VCD_2[i]))

    spPred = [[0 for j in range(nn)] for i in range(nn)]
    Home   = [[0 for j in range(nn)] for i in range(nn)]
    bkbn   = [0 for i in range(nn)]
    Seq    = [0.0 for i in range(nn * nn)]
    Npred  = [0 for i in range(nn)]
    Weight = [0.0 for i in range(nn)]
    
    if trace:
        log_file.write("\nMENTOR Algorithm Report\n")
    # Set the node weights
    SetWeights(inp) 
    # Find the network median of all the nodes
    Median = SetMedian(inp, False) 
    # Select backbone nodes
    Thresh(inp) 
    # Find the network median, only considering backbone nodes
    Median = SetMedian(inp, True)  
    # Find the spanning tree
    if trace:
        log_file.write("\n+++++ MENTOR Tree +++++\n")
    PrimDijk(inp)
    # Find the distances and predecessors within the tree
    SetDist(inp)
    # Find the sequence for considering node pairs
    if trace:
        log_file.write("+++++ Sequence of pairs +++++\n")
    Sequence(inp)
    # Select backbone links
    if trace:
        log_file.write("+++++ Considering pairs +++++\n")
    Compress(inp)

    # Set node types
    if trace:
        log_file.write("\n+++++ Selected node types +++++\n")
    for i in range(nn):
        if bkbn[i] == 0:
            Ntype = 'T'
        else:
            Ntype = 'M'
        if i == Median:
            Ntype = 'C'
        Nmsgrate = Weight[i] / inp.MN_MSGLEN
        # Node delay
        cap = 100.0
        while True:
            if (Nmsgrate / cap) <= inp.MN_UTIL:
                Ncap = cap
                break
            else:
                cap += 100.0
        svc_time = 1.0 / Ncap
        Nutil = Nmsgrate * svc_time
        m2 = Nmsgrate * svc_time * svc_time
        if Nutil >= 1.0:
            Ndelay = -1.0
        elif Nmsgrate == 0.0:
            Ndelay = 1.0 / Ncap
        else:
            m1 = Nutil / Nmsgrate   # Average service time
            m2 = m2 / Nmsgrate      # Second moment of service time */
            Ndelay = m1 + Nmsgrate * m2 / (2 * ( 1 - Nutil ))
        if trace:
            log_file.write("Node %5s is type %c\n" % (inp.Nname[i] , Ntype))
        net_file.write("N,%d,%s,%f,%f,%f,%f,%f,\n" % (i, Ntype, Ncap, Nmsgrate, Nutil, Ndelay, Weight[i]))
    if trace:
        log_file.write("MENTOR Done\n")
    net_file.close() 
    return(nl, NetCost)
        
# Set node weights
def SetWeights(inp):
    nn = inp.nn
    for i in range(nn):
        Weight[i] = 0.0
    for i in range(nn):
        for j in range(nn):
            Weight[i] += inp.req[i][j]
            Weight[j] += inp.req[i][j]

# Find a median
def SetMedian(inp, Flag):
    nn = inp.nn
    BestMoment = FINFINITY
    for i in range(nn):
        if Flag == False or bkbn[i] == 1:
            moment = 0.0
            for j in range(nn):
                moment += LineCost(inp, i, j, 0) * Weight[j]
            if moment < BestMoment:
                BestMoment = moment
                median = i
    if trace:
        log_file.write("Found median %d\n" % (median))
    return (median)

# Threshold backbone node assignment algorithm
def Thresh(inp):
    nn     = inp.nn
    merit  = [0.0 for i in range(nn)]
    radius = 0.0
    nassg  = 0
  
    for i in range(nn-1):
        for j in range(i+1, nn):
            radius = max(radius, LineCost(inp, i, j, 0))

    Wparm = MN_WPARM * inp.MN_UTIL * inp.MN_CAPS[0]
    nassg = 0
    for i in range(nn):
        if Weight[i] >= Wparm:
            nassg += 1
            bkbn[i] = 1
            merit[i] = -1.0
        else:
            bkbn[i] = -1
            merit[i] = (MN_DPARM * LineCost(inp, i, Median, 0) / radius + (1 - MN_DPARM) * Weight[i] / Wparm)

    radius *= MN_RPARM
    for i in range(nn):
        if bkbn[i] == 1:
            for j in range(nn):
                if (bkbn[j] == -1) and (LineCost(inp, i, j, 0) <= radius):
                    bkbn[j] = 0
                    nassg += 1
                    break

    while nassg < nn:
        BestMerit = -1.0
        for i in range(nn):
            if (bkbn[i] == -1) and (merit[i] > BestMerit):
                bestI = i
                BestMerit = merit[i]
        bkbn[bestI] = 1
        nassg += 1
        for i in range(nn):
            if (bkbn[i] == -1) and (LineCost(inp, i, bestI, 0) < radius):
                bkbn[i] = 0
                nassg += 1

# Tree finding heuristic
def PrimDijk(inp):
    nn     = inp.nn
    label  = [0.0 for i in range(nn)]
    ldist  = [0.0 for i in range(nn)]
    InTree = [False for i in range(nn)]

    for i in range(nn):
        Npred[i] = Median
        label[i] = LineCost(inp, i, Median, 0)
        ldist[i] = LineCost(inp, i, Median, 0)
        InTree[i] = False
    InTree[Median] = True

    while True:
        BestLabel = FINFINITY
        for i in range(nn):
            if (bkbn[i] == 1) and (InTree[i] == False) and (label[i] < BestLabel):
                besti = i
                BestLabel = label[i]
        if BestLabel > (.99 * FINFINITY):
            break
        InTree[besti] = True
        for i in range(nn):
            tcost = LineCost(inp, i, besti, 0)
            if (InTree[i] == False) and (label[i] > (MN_ALPHA * ldist[besti] + tcost)):
                label[i] = MN_ALPHA * ldist[besti] + tcost
                ldist[i] = ldist[besti] + tcost
                Npred[i] = besti
    if trace:
        for i in range(nn):
            log_file.write("Tree pred of %d is %d\n" % (i, Npred[i]))

# Find shortest paths through the tree
def SetDist(inp):
    nn       = inp.nn

    # Set the predecessors
    for i in range(nn):
        for j in range(nn):
            spPred[i][j] = Npred[j]
        spPred[i][i] = i
    for i in range(nn):
        if i == Median:
            continue
        p = Npred[i]
        spPred[i][p] = i
        while p != Median:
            pp = Npred[p]
            spPred[i][pp] = p
            p = pp

# Find the order in which to consider node pairs
def Sequence(inp):
    nn   = inp.nn
    nDep = [0.0 for i in range(nn * nn)]
    Dep1 = [0.0 for i in range(nn * nn)]
    Dep2 = [0.0 for i in range(nn * nn)]
    Pair = [0.0 for i in range(nn * nn)]

    npair = 0
    for i in range(nn-1):
        for j in range(i+1, nn):
            Pair[npair] = MakeIndexPair(nn, i, j)
            if trace:
                log_file.write("i: %2d   j: %2d   npair: %2d   pair: %2d\n" % (i, j, npair, Pair[npair]))
            nDep[Pair[npair]] = 0
            npair += 1

    for p in range(npair):
        i, j = SplitIndexPair(nn, Pair[p])
        p1 = spPred[i][j]   # Pred in shortest path through the tree
        p2 = spPred[j][i]
        if p1 == i:         # Tree link
            h = -1
        elif p1 == p2:      # 2-hop path; only one possible home
            h = p1
        else:               # Choose cheaper detour
            if LineCost(inp, i, p1, 0) + LineCost(inp, p1, j, 0) <= LineCost(inp, i, p2, 0) + LineCost(inp, p2, j, 0):
                h = p1
            else:
                h = p2
        Home[i][j] = h
        if trace:
            log_file.write("*** Home for pair %2d (nodes %2d %2d) is %2d\n" % (p, i, j, h))
        if h == -1:
            Dep1[Pair[p]] = -1
            Dep2[Pair[p]] = -1
            continue
        pairih = MakeIndexPair(nn, i, h)
        Dep1[Pair[p]] = pairih
        nDep[pairih] += 1
        pairjh = MakeIndexPair(nn, j, h)
        Dep2[Pair[p]] = pairjh
        nDep[pairjh] += 1
        if trace:
            log_file.write("New dependencies for pairs %2d %2d\n" % (pairih , pairjh ))

    nseq = 0
    for p in range(npair):
        pp = Pair[p]
        if nDep[pp] == 0:
            Seq[nseq] = pp
            nseq += 1
            if trace:
                log_file.write("Seq %2d is pair value %2d\n" % (nseq-1 , Seq[nseq-1]))

    iseq = 0
    while iseq < nseq:
        p = Seq[iseq]
        iseq += 1
        d = Dep1[p]
        if (d >= 0) and (nDep[d] == 1):
            Seq[nseq] = d
            nseq += 1
            if trace:
                log_file.write("Seq %2d is pair value %2d\n" % (nseq-1 , Seq[nseq-1]))
        else:
            nDep[d] -= 1
        d = Dep2[p]
        if (d >= 0) and (nDep[d] == 1):
            Seq[nseq] = d
            nseq += 1
            if trace:
                log_file.write("Seq %2d is pair value %2d\n" % (nseq-1 , Seq[nseq-1]))
        else:
            nDep[d] -= 1

    if nseq != npair:
        print("Sequence A B O R T I N G")
        if trace:
            log_file.write("Sequence A B O R T I N G\n")
        return

def MakeIndexPair(nn, i, j):
    if i < j:
        return(nn * i + j)
    else:
        return(nn * j + i)

def SplitIndexPair(nn, pair):
    i = pair // nn
    j = pair % nn
    return(i, j)

def Eucl(x1, y1, x2, y2):
    t = ((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2))
    return sqrt(t)

def LineCost(inp, a, b, tariff=0):
    # distance based costing
#    dist = inp.dist[a][b]
    dist = Eucl(inp.Xcoor[a], inp.Ycoor[a], inp.Xcoor[b], inp.Ycoor[b])
    fixed = inp.MN_FXCD[tariff]
    dist1 = inp.MN_DIST1
    vcost1 = inp.MN_VCD_1[tariff]
    vcost2 = inp.MN_VCD_2[tariff]
    if dist <= dist1:
        cost = dist * vcost1
    else:
        cost = dist1 * vcost1 + ((dist - dist1) * vcost2)
    cost += fixed
    return cost
    
def Resize(inp, n1, n2, Ltype, Lmult, Lcost):
    if inp.MN_DUPLEX == 'F':
        load = max(inp.req[n1][n2], inp.req[n2][n1])
    else:
        load = inp.req[n1][n2] + inp.req[n2][n1]
    best_type = Ltype
    best_mult = Lmult
    best_cost = Lcost * Lmult
    Lcap      = inp.MN_CAPS[Ltype] * inp.MN_UTIL
    for j in range(inp.MN_NCAP):
        m = ceil(load / (inp.MN_CAPS[j] * inp.MN_UTIL))
        if m == 0:
            m = 1
        c = LineCost(inp, n1, n2, j)
        if (m * c) >= best_cost:
            continue
        best_type = j
        best_mult = m
        best_cost = m * c
        Ltype = best_type
        Lmult = best_mult
        Lcost = c
        Lcap  = inp.MN_CAPS[Ltype] * inp.MN_UTIL
    return(Ltype, Lmult, Lcost, Lcap)

def Compress(inp):
    global nl, NetCost
    nn   = inp.nn
    
    npairs = ( nn * (nn-1) ) // 2
    nl = 0
    cap = inp.MN_UTIL * inp.MN_CAPS[0]
    for p in range(npairs):
        n1, n2 = SplitIndexPair(nn, Seq[p])
        h = Home[n1][n2]
        if inp.MN_DUPLEX == 'F':
            load = max(inp.req[n1][n2], inp.req[n2][n1])
        else:
            load = inp.req[n1][n2] + inp.req[n2][n1]
        if trace:
            log_file.write("Considering link %2d %2d and home %2d with load %8.1f\n" % (n1, n2, h, load))

        if load >= cap:
            mult = int(load / cap)
            load -= mult * cap
        else:
            mult = 0
        if ((h == -1) and (load > 0.0)) or (load >= (1 - MN_SLACK) * cap) or (mult > 0 and load > 0.0 and inp.MN_BIFUR == False):
            mult += 1
            overflow12 = 0.0
            overflow21 = 0.0
        else:
            if inp.MN_DUPLEX == 'F':
                overflow12 = max(0.0, inp.req[n1][n2] - mult * cap)
                overflow21 = max(0.0, inp.req[n2][n1] - mult * cap)
            else:
                overflow12 = max(0.0, inp.req[n1][n2] + inp.req[n2][n1] - mult * cap)
                overflow21 = 0.0
        load12 = inp.req[n1][n2] - overflow12
        load21 = inp.req[n2][n1] - overflow21

        if mult > 0:
        
            Ltype  = 0 # line type
            if h == -1:
                Ltree = True
            else:
                Ltree = False
            Lmult = mult
            Lcost = LineCost(inp, n1, n2, Ltype)
            (Ltype, Lmult, Lcost, Lcap) = Resize(inp, n1, n2, Ltype, Lmult, Lcost)
            NetCost += Lmult * Lcost
            lcap = inp.MN_CAPS[Ltype] * Lmult
            Lutil12 = load12 / lcap
            Lutil21 = load21 / lcap
            # Line delay calculations
            dist = Eucl(inp.Xcoor[n1], inp.Ycoor[n1], inp.Xcoor[n2], inp.Ycoor[n2])
            ts = (inp.MN_MSGLEN / inp.MN_CAPS[Ltype])
            if inp.MN_NCAP == 1: # Assume AKER model
                tp = 0.000005 * dist * 1.60934 # convert to km
            else:
                tp = 0.000005 * dist # treat as km
            m2 = 2 * ts * ts
            mps12 = load12 / inp.MN_MSGLEN
            tw12 = mps12 / mult * m2 / (2 * (1 - Lutil12))
            mps21 = load21 / inp.MN_MSGLEN
            tw21 = mps21 / mult * m2 / (2 * (1 - Lutil21))
            Ldelay12 = ts + tp + tw12
            Ldelay21 = ts + tp + tw21
            net_file.write("L,%d,%d,%d,%d,%d,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%f,%s,\n" % (nl, n1, n2, Ltype, Lmult, Lcost, Lcap, load12, load21, mps12, mps21, Lutil12, Lutil21, dist, ts, tp, tw12, tw21, Ldelay12, Ldelay21, str(Ltree)))
            nl += 1
            if trace:
                log_file.write("Inserting link End1 %2d End2 %2d mult %2d\n" % (n1, n2, mult))

        if overflow12 > 0.0:
            inp.req[n1][n2] = mult * cap  ##### Adjust new line flow if overflow
            inp.req[n1][h] += overflow12
            inp.req[h][n2] += overflow12
            if trace:
                log_file.write("overflow12 Lreq %2d %2d is now %6.0f\n" % (n1, h, inp.req[n1][h]))
                log_file.write("overflow12 Lreq %2d %2d is now %6.0f\n" % (h, n2, inp.req[h][n2]))

        if overflow21 > 0.0:
            inp.req[n2][n1] = mult * cap  ##### Adjust new line flow if overflow
            inp.req[n2][h] += overflow21
            inp.req[h][n1] += overflow21
            if trace:
                log_file.write("overflow21 Lreq %2d %2d is now %6.0f\n" % (n2, h, inp.req[n2][h]))
                log_file.write("overflow21 Lreq %2d %2d is now %6.0f\n" % (h, n1, inp.req[h][n1]))

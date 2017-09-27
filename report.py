from math import sqrt
import netgen
import config

def Eucl(x1, y1, x2, y2):
    t = ((x1 - x2) * (x1 - x2)) + ((y1 - y2) * (y1 - y2))
    return sqrt(t)

def writeReport(self):
    result = self.results[self.current]
    filename = "Report%d.rpt" % (self.current)
    report = open(filename, 'w')
    report.write("Mentor Network Report\n")
    report.write("Network cost: %8d\n" % (result.NetCost))

    max_name = 0
    for i in range(self.inp.nn):
        if len(self.inp.Nname[i]) > max_name:
            max_name = len(self.inp.Nname[i])
    max_name = max(4, max_name) # pad to at least "Name"!
    report.write("\n+++++ Selected node types +++++\n")
    for i in range(self.inp.nn):
        if len(self.inp.Nname[i]) > max_name:
            max_name = len(self.inp.Nname[i])
    format_str = "Node %" + str(max_name) + "s Type ___X ___Y _Pop __Weight _Msgrate Capacity _____Util ___Delay"
    for i in range(self.inp.MN_NCAP):
        cap = str(int(self.inp.MN_CAPS[i]) // 1000)
        cap += "k"
        cap = cap.rjust(6, "_")
        format_str += " " + cap
    format_str += "\n"
    str1 = "Name"
    report.write(format_str % (str1.rjust(max_name, "_")))
    format_str = "%4d %" + str(max_name) + "s %4s %4d %4d %4d %8.0f %8.2f %8d %8.2f%% %8f"
    for i in range(self.inp.MN_NCAP):
        format_str += " " + "%6d"
    format_str += "\n"
    for i in range(self.inp.nn):
        # Population
        if config.NG_KERSH:
            pop = netgen.ndata[netgen.node[i]][4]
        else:
            pop = netgen.pvpop[i]
        # Link count
        links = [0 for i in range(self.inp.MN_NCAP)]
        for j in range(result.nl):
            if self.End1[j] == i or self.End2[j] == i:
                links[self.Ltype[j]] += 1
        util = self.Nutil[i] * 100.0
        if self.inp.MN_NCAP == 1:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i], 
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0]))
        elif self.inp.MN_NCAP == 2:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i], 
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1]))
        elif self.inp.MN_NCAP == 3:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i],
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1], links[2]))
        elif self.inp.MN_NCAP == 4:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i],
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1], links[2], links[3]))
        elif self.inp.MN_NCAP == 5:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i],
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1], links[2], links[3], 
                                       links[4]))
        elif self.inp.MN_NCAP == 6:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i],
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1], links[2], links[3], 
                                       links[4], links[5]))
        elif self.inp.MN_NCAP == 7:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i],
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1], links[2], links[3], 
                                       links[4], links[5], links[6]))
        else:
            report.write(format_str % (i, self.inp.Nname[i], self.Ntype[i], 
                                       self.inp.Xcoor[i], self.inp.Ycoor[i], 
                                       pop, self.Weight[i], self.Nmsgrate[i],
                                       self.Ncap[i], util, self.Ndelay[i],
                                       links[0], links[1], links[2], links[3], 
                                       links[4], links[5], links[6], links[7]))
    report.write("\n+++++ Selected links +++++\n")
    if config.NG_KERSH:
        format_str = "Index %" + str(max_name) + "s %" + str(max_name)
        format_str += "s Dist_ml Capacity Mult Dup Linecost ___Req12 ___Req21 ___Util12 ___Util21 _Delay12 _Delay21\n"
    else:
        format_str = "Index %" + str(max_name) + "s %" + str(max_name) 
        format_str += "s Dist_km Capacity Mult Dup Linecost ___Req12 ___Req21 ___Util12 ___Util21 _Delay12 _Delay21\n"
    str1 = "End1"
    str2 = "End2"
    report.write(format_str % (str1.rjust(max_name, "_"), str2.rjust(max_name, "_")))
    format_str = "%5d %" + str(max_name) + "s %" + str(max_name) + "s %7d %8d %4d %3s %8d %8d %8d %8.2f%% %8.2f%% %8f %8f\n"
    for i in range(result.nl):
        end1 = self.End1[i]
        end2 = self.End2[i]
        dist = Eucl(self.inp.Xcoor[end1], self.inp.Ycoor[end1], 
                    self.inp.Xcoor[end2], self.inp.Ycoor[end2])
        report.write(format_str % (i, self.inp.Nname[end1], self.inp.Nname[end2], dist,
                                   self.inp.MN_CAPS[self.Ltype[i]], self.Lmult[i], self.inp.MN_DUPLEX, 
                                   self.Lcost[i] * self.Lmult[i], self.Lreq12[i], self.Lreq21[i],
                                   self.Lutil12[i] * 100, self.Lutil21[i] * 100, self.Ldelay12[i], self.Ldelay21[i]))
    report.write("\n+++++ Parameters +++++\n")
    report.write("MN_ALPHA  %8.2f\n" % (result.alpha))
    report.write("MN_SLACK  %8.2f\n" % (result.slack))
    report.write("MN_DPARM  %8.2f\n" % (result.dparm))
    report.write("MN_RPARM  %8.2f\n" % (result.rparm))
    report.write("MN_WPARM  %8.2f\n" % (result.wparm))
    report.write("MN_BIFUR  %8s\n"   % (self.inp.MN_BIFUR))
    report.write("MN_CAPS:  ")
    for i in range(self.inp.MN_NCAP):
        if i == 0:
            report.write("[")
        else:
            report.write(", ")
        report.write(str(self.inp.MN_CAPS[i]))
    report.write("]\n")
    report.write("MN_DIST1  %8d\n"   % (self.inp.MN_DIST1))
    report.write("MN_DUPLEX %8s\n"   % (self.inp.MN_DUPLEX))
    report.write("MN_FXCD:  ")
    for i in range(self.inp.MN_NCAP):
        if i == 0:
            report.write("[")
        else:
            report.write(", ")
        report.write(str(self.inp.MN_FXCD[i]))
    report.write("]\n")
#    report.write("MN_LCOLOR:")
#    for i in range(self.inp.MN_NCAP):
#        if i == 0:
#            report.write("[")
#        else:
#            report.write(", ")
#        report.write(str(self.inp.MN_LCOLOR[i]))
#    report.write("]\n")
    report.write("MN_MSGLEN %8d\n"   % (self.inp.MN_MSGLEN))
    report.write("MN_NCAP   %8d\n"   % (self.inp.MN_NCAP))
    report.write("MN_TRACE  %8s\n"   % (self.inp.MN_TRACE))
    report.write("MN_UTIL   %8.2f\n" % (self.inp.MN_UTIL))
    report.write("MN_VCD_1: ")
    for i in range(self.inp.MN_NCAP):
        if i == 0:
            report.write("[")
        else:
            report.write(", ")
        report.write(str(self.inp.MN_VCD_1[i]))
    report.write("]\n")
    report.write("MN_VCD_2: ")
    for i in range(self.inp.MN_NCAP):
        if i == 0:
            report.write("[")
        else:
            report.write(", ")
        report.write(str(self.inp.MN_VCD_2[i]))
    report.write("]\n")
    report.close()

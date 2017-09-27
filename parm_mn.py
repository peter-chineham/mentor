# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 19:16:43 2017

@author: vinntec
"""
MN_ALPHA_min = None
MN_ALPHA_max = None
MN_ALPHA_inc = None
MN_SLACK_min = None
MN_SLACK_max = None
MN_SLACK_inc = None
MN_DPARM_min = None
MN_DPARM_max = None
MN_DPARM_inc = None
MN_RPARM_min = None
MN_RPARM_max = None
MN_RPARM_inc = None
MN_WPARM_min = None
MN_WPARM_max = None
MN_WPARM_inc = None

def setMN(inp):
    global MN_ALPHA_min, MN_ALPHA_max, MN_ALPHA_inc
    global MN_SLACK_min, MN_SLACK_max, MN_SLACK_inc
    global MN_DPARM_min, MN_DPARM_max, MN_DPARM_inc
    global MN_RPARM_min, MN_RPARM_max, MN_RPARM_inc
    global MN_WPARM_min, MN_WPARM_max, MN_WPARM_inc
    
    # Mentor Parameters for the example in AKER's book
#    MN_ALPHA_min = 0.0
#    MN_ALPHA_max = 1.0
#    MN_ALPHA_inc = 0.5
#    MN_SLACK_min = 0.0
#    MN_SLACK_max = 1.0
#    MN_SLACK_inc = 0.2
#    MN_DPARM_min = 0.0
#    MN_DPARM_max = 1.0
#    MN_DPARM_inc = 0.5
#    MN_RPARM_min = 0.0
#    MN_RPARM_max = 1.0
#    MN_RPARM_inc = 0.5
#    MN_WPARM_min = 1.0
#    MN_WPARM_max = 3.0
#    MN_WPARM_inc = 1.0
#    inp.MN_BIFUR    = True     # Bifurcate traffic - split flow onto multiple routes?
#    inp.MN_CAPS[0]  = 56000.0
#    inp.MN_DIST1    = 99999.0
#    inp.MN_DUPLEX   = "F"
#    inp.MN_FXCD[0]  = 1000.0
#    inp.MN_NCAP     = 1
#    inp.MN_TRACE    = False
#    inp.MN_UTIL     = 0.6
#    inp.MN_VCD_1[0] = 3.0
#    inp.MN_VCD_2[0] = 3.0

    # Mentor Parameters for PV
    MN_ALPHA_min = 0.0
    MN_ALPHA_max = 1.0
    MN_ALPHA_inc = 0.5
    MN_SLACK_min = 0.0
    MN_SLACK_max = 1.0
    MN_SLACK_inc = 0.5
    MN_DPARM_min = 0.0
    MN_DPARM_max = 1.0
    MN_DPARM_inc = 0.5
    MN_RPARM_min = 0.0
    MN_RPARM_max = 1.0
    MN_RPARM_inc = 0.5
    MN_WPARM_min = 3.0
    MN_WPARM_max = 3.0
    MN_WPARM_inc = 1.0
    inp.MN_BIFUR  = True       # Bifurcate traffic - split flow onto multiple routes?
    inp.MN_DUPLEX = "F"
    inp.MN_TRACE  = False
    inp.MN_UTIL   = 0.6        # 60% utilisation max

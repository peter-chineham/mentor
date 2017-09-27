# -*- coding: utf-8 -*-
"""
Created on Thu Aug 17 19:14:42 2017

@author: vinntec
"""
import config

def setNG():

    # Parameters to gen network in AKER's book
#    config.NG_CFNAME = "TOWNS.TXT"
#    config.NG_FXTRF  = 8000.0
#    config.NG_NMODEL = 'S'
#    config.NG_NN     = 10

    # Parameters for NetGen_PV
    config.NG_FXTRF = 1000.0     # fixed traf/pair
    config.NG_KERSH = False      # PV random network
    config.NG_NHOST = 5
    config.NG_NN    = 100
    config.NG_RNTRF = 1.0        # random traf/pair 0-1
    config.NG_VTRFD = 1.0        # variable traf/dist 0-1
    config.NG_VTRFP = 1.0        # variable traf/pop 0-1

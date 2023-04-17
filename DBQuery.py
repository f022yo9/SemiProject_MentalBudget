#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 24 16:46:16 2023

@author: f___yo_
"""

select address kind from hospital
where address like %'서울특별시'% and kind in ('병원', '의원')
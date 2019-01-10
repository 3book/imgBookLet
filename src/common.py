#!/bin/env python
# -*-coding:utf-8-*-
#pylint: disable = C0103
'''
Copyright 2019 @3book.
'''
import re
from types import FunctionType
from collections.abc import Iterable

def string2KV(string):
    '''
    dawd
    '''
    # PAGE_FRONT_INSERT_RE = r"[^\d]*([1-9]?\d*)(p->)([1-9]?\d*)"
    PAGE_BACK_INSERT_RE = r"[^\d]*([1-9]?\d*)\s*:\s*([1-9]?\d*)p"
    strDict = {}
    start = 0
    while string[start:]:
        pageRangeStr = re.search(PAGE_BACK_INSERT_RE, string[start:])
        if pageRangeStr is None:
            start += len(string[start:])
        else:
            start += pageRangeStr.end()
            key = pageRangeStr.group(1)
            value = pageRangeStr.group(2)
            strDict[key] = value
    return strDict

class objListSlice(object):
    '''
    pass
    '''

    def __init__(self, objList):
        if isinstance(objList, Iterable):
            self.objList = objList
            self.sliceList = None

    def strSliceList(self, string):
        '''
        convert string to slice.
        parm   string.     i.e. string='1,-2,3-5,3- 5-8 3:897--- 54++34'
        return sliceList. i.e. [slice(1, None, None), slice(None, 2, None), slice(3, 5, None)]
        '''
        if not isinstance(string, str):
            raise TypeError
            # return slice(None,None,None)
        PAGE_RANGE_RE = r"[^\d-]*(\d*)(-*)([1-9]?\d*)[^\d-]*"
        sliceList = []
        start = -1
        while string[start:]:
            pageRangeStr = re.search(PAGE_RANGE_RE, string[start:])
            if pageRangeStr is None:
                start += len(string[start:])
            else:
                start += pageRangeStr.end()
                sstr = pageRangeStr.group(1)
                mstr = pageRangeStr.group(2)
                estr = pageRangeStr.group(3)
            if not mstr:
                s = None if not sstr else int(sstr)-1
                e = s
            else:
                s = None if not sstr else int(sstr)-1
                e = None if not estr else int(estr)
            sliceList.append(slice(s, e))
        self.sliceList = sliceList
        # return self.sliceList

    def reorganize(self, slicestring):
        '''
        Reorganize object list.

        param objs: object list.
        param sliceList: slice list.
        return objList: object list after reorganize.
        '''
        self.strSliceList(slicestring)
        objList = []
        for i in self.sliceList:
            objList += self.objList[i]
        return objList

    def extract(self, slicestring):
        '''
        extract objects.
        param objs: object list.
        param sliceList: slice list.
        return set(objList): slice and set object list .
        '''
        return set(self.reorganize(slicestring))

    def doFunc(self, slicestring, func=None):
        '''
        pass
        '''
        if isinstance(func, FunctionType):
            for obj in set(self.extract(slicestring)):
                i = self.objList.index(obj)
                obj = func(obj)
                self.objList.pop(i)
                self.objList.insert(i, obj)
            return
        else:
            raise TypeError('FunctionType error')

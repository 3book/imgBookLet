#!/bin/env python
# -*-coding:utf-8-*-
#pylint: disable = C0103
'''
Copyright 2019 @3book.
'''
import re
import logging
# from types import FunctionType
from collections.abc import Iterable

class strObj(object):
    '''
    TODO
    '''
    def __init__(self, obj):
        if isinstance(obj, str):
            self.obj = obj

    @staticmethod
    def str2slice(string):
        '''
        convert string to slice.
        parm   string.     i.e. string='1,-2,3-5'
        return sliceList. i.e. [slice(1, None, None), slice(None, 2, None), slice(3, 5, None)]
        '''
        if not isinstance(string, str):
            raise TypeError
            # return slice(None,None,None)
        PAGE_RANGE_RE = r"[^\d-]*(\d*)(-*)([1-9]?\d*)[^\d-]*"
        sliceList = []
        start = 0
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
                s = None if not sstr else int(sstr) - 1
                e = s + 1
            else:
                s = None if not sstr else int(sstr) - 1
                e = None if not estr else int(estr)
            sliceList.append(slice(s, e))
        return sliceList

    @staticmethod
    def str2dict(string):
        '''
        convert strings to dict
        match Num:Num
        '''
        PAGE_BACK_INSERT_RE = r"[^\d]*([1-9]?\d*)\s*:\s*([1-9]?\d*)"
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


class listObj(object):
    '''
    list object
    '''

    def __init__(self, objs):
        if isinstance(objs, Iterable):
            self.objs = objs
            self.sliceList = None

    def organize(self, arg):
        '''
        organize object list.
        '''
        if isinstance(arg, str):
            orgList = strObj.str2slice(arg)
        elif isinstance(arg, list):
            orgList = arg
        else:
            raise TypeError
        objs = []
        for i in orgList:
            objs += self.objs[i]
        return objs

    def extract(self, args):
        '''
        extract objects.
        '''
        objs = list(set(self.organize(args)))
        objs.sort(key=self.objs.index)
        return objs

    # def group(self, *args):
    #     '''
    #     ppp
    #     '''
    #     objs = []
    #     while self.objs:
    #         group = []
    #         for i in args:
    #             group.append(self.objs[i])
    #             del self.objs[i]
    #         objs.append(group)
    #     return objs

    # def doFunc(self, slicestring=None, func=None):
    #     '''
    #     pass
    #     '''
    #     if isinstance(func, FunctionType):
    #         for obj in self.extract(slicestring):
    #             i = self.objs.index(obj)
    #             obj = func(obj)
    #             self.objs.pop(i)
    #             self.objs.insert(i, obj)
    #         return
    #     else:
    #         raise TypeError('FunctionType error')


def setLog():
    '''
    setting logging basic config.
    '''
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '%(levelname)-10s|%(asctime)s|%(filename)s[line:%(lineno)d] [func:%(funcName)s] %(message)s',
        # datefmt='%a, %d %b %Y %H:%M:%S',
        filename='log.log',
        filemode='w')

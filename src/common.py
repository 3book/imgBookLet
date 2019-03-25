#!/usr/bin/env python3
# -*-coding:utf-8-*-
#pylint: disable = C0103
'''
Copyright 2019 @3book.
'''
import re
import logging
from types import FunctionType
from collections.abc import Iterable

class dictObj(dict):
    '''
    . access to dictionary attributes
    '''
    # def __init__(self,dict):
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

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
        # sliceList = []
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
            yield slice(s, e)
            # sliceList.append(slice(s, e))
        # return sliceList
    @staticmethod
    def str2list(string, maxLen):
        '''
        string to list
        '''
        list1 = []
        for i in strObj.str2slice(string):
            if i.start is None:
                start = 0
            else:
                start = i.start
            if i.stop is None:
                stop = maxLen
            else:
                stop = i.stop
            list1 += list(range(start, stop))
        return list1

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

    def __indexGen__(self, arg, oType=slice):
        if isinstance(arg, str):
            if oType == slice:
                indexs = strObj.str2slice(arg)
            elif oType == list:
                indexs = strObj.str2list(arg, len(self.objs))
        elif isinstance(arg, Iterable):
            indexs = arg
        else:
            raise TypeError
        return indexs

    def organize(self, arg):
        '''
        organize object list.
        '''
        indexs = self.__indexGen__(arg)
        objs = []
        for i in indexs:
            objs += self.objs[i]
        self.objs = objs

    def extract(self, args):
        '''
        extract object list.
        '''
        objs = list(set(self.organize(args)))
        objs.sort(key=self.objs.index)
        return objs

    def __group(self, arg):
        if isinstance(arg, int):
            yield self.objs[0, arg]
            del self.objs[0, arg]
        elif isinstance(arg, list):
            for i in arg:
                yield self.objs[i]
            for i in arg:
                del self.objs[i]

    def group(self, arg):
        '''
        group object
        '''
        self.objs = list(self.__group(arg))

    def attach(self, arg, obj=None):
        '''
        attach object in object list
        '''
        indexs = self.__indexGen__(arg, oType=list)
        for i in indexs:
            if isinstance(self.objs[i], list):
                self.objs[i][1].append(obj)
            else:
                self.objs[i] = [[self.objs[i]], [obj]]

    def modify(self, arg, func=None):
        '''
        modify object in object list
        '''
        if isinstance(func, FunctionType):
            indexs = self.__indexGen__(arg, oType=list)
            for i in indexs:
                if isinstance(self.objs[i], list):
                    self.objs[i][0] = func(self.objs[i][0])
                else:
                    self.objs[i] = list(func(self.objs[i]))

    @staticmethod
    def __flatten(objs):
        '''
        flatten object list
        '''
        for obj in objs:
            if not isinstance(obj, list):
                yield obj
            else:
                yield from listObj.__flatten(obj)

    def flatten(self):
        '''
        flatten object list
        '''
        self.objs = list(self.__flatten(self.objs))


# def flatten(objs):
#     '''
#     flatten object list
#     '''
#     for obj in objs:
#         if not isinstance(obj, Iterable):
#             yield obj
#         else:
#             yield from flatten(obj)


# def getItem(objs, index):
#     '''
#     get item
#     '''
#     obj = objs[index]
#     item = obj if not isinstance(obj, Iterable) else getItem(obj, 0)
#     return item


def setLog():
    '''
    setting logging basic config.
    '''
    logging.basicConfig(
        level=logging.DEBUG,
        format=
        '%(levelname)-10s|%(asctime)s|\
        %(filename)s[line:%(lineno)d] [func:%(funcName)s] %(message)s',
        # datefmt='%a, %d %b %Y %H:%M:%S',
        filename='log.log',
        filemode='w')

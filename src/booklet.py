#!/bin/env python
# -*-coding:utf-8-*-
#pylint: disable = C0103
'''
Copyright 2019 @3book.
Format PDF file to printable booklet.
'''
__author__ = '3book'
__version__ = '0.0.1'

import os
import argparse
import logging
from functools import reduce
from pdfrw import PdfReader, PdfWriter, PageMerge
from pdfrw.findobjs import page_per_xobj
from common import dictObj
from common import listObj
from common import setLog

PRINT_LAYOUT_DICT = {
    'A5': {
        'x': 2,
        'y': 1,
        'z': 2
    },
    'A6': {
        'x': 2,
        'y': 2,
        'z': 2
    },
    'A7': {
        'x': 4,
        'y': 2,
        'z': 2
    }
}
PRINT_SIZE_DICT = {
    'A4': {
        'w': 595,
        'h': 842
    },
    'A5': {
        'w': 421,
        'h': 595
    },
    'A6': {
        'w': 297,
        'h': 421
    },
    'A7': {
        'w': 210,
        'h': 297
    }
}

class booklet(listObj):
    '''
    booklet class
    '''

    def __init__(self, args):
        with open(args.inputFilePath, 'rb') as pdfFile:
            pdfRead = PdfReader(pdfFile)
        ipages = pdfRead.pages
        listObj.__init__(self, ipages)
        self.__inArgs = args
        self.initInfo()
        self.opages = []
        self.__needFlatten = 0
        self.__gen = 0

    def initInfo(self):
        '''
        initial booklet information
        '''
        # initial booklet
        info = dictObj()
        if self.__inArgs.bookletSize:
            info['outBookSize'] = self.__inArgs.bookletSize
            info.update(PRINT_LAYOUT_DICT[info['outBookSize']])
            info.update(PRINT_SIZE_DICT[info['outBookSize']])
            self.info = info
            # blank page
            blank = PageMerge()
            blank.mbox = [0, 0, info.w, info.h]
            self.__blank = blank.render()
            # counter layout
            self.__counter = reduce(
                lambda x, y: x * y,
                [self.info['x'], self.info['y'], self.info['z']])

    def genBook(self, outputFile=None):
        '''
        generate booklet
        '''
        args = self.__inArgs
        if args.scanRotateAngle:
            self.objs = list(page_per_xobj(self.objs))
            self.rotate(int(args.scanRotateAngle))
            # self.modify('0-', self.splitPage)
            # self.__needFlatten = 1
            # obj = self.objs.pop(0)
            # self.objs.append(obj)
            self.__gen = 1
        if args.organizePages:
            self.organize(args.organizePages)
            self.__gen = 1
        if args.insertPage:
            self.attach(args.insertPage, self.__blank)
            self.__needFlatten = 1
            self.__gen = 1
        if args.vCutPage:
            self.modify(args.vCutPage, self.splitPage)
            self.__needFlatten = 1
            self.__gen = 1
        if self.__needFlatten:
            self.flatten()
        # if args.group:
        #     self.group(args.group)
        if args.bookletSize:
            self.booklet()
            self.__gen = 1
        if self.__gen  and outputFile is None:
            outputFile = os.path.splitext(
                args.inputFilePath)[0] + '_booklet' + '.pdf'
            PdfWriter(outputFile).addpages(self.objs).write()

    def booklet(self):
        '''
        TODO
        '''
        self.autoInsertBlank()
        for seed in range(0, len(self.objs), self.__counter):
            self.pageLayout(int(seed / 2))
        self.objs = self.opages

    def autoInsertBlank(self):
        '''
        auto insert blank page
        '''
        length = len(self.objs)
        tailBlanks = -(length) % 4
        self.objs += [self.__blank] * tailBlanks
        length = len(self.objs)
        m = int(length / 2)
        midBlanks = -(length) % self.__counter
        self.objs = self.objs[0:m] + [self.__blank] * midBlanks + self.objs[m:]

    def genIndex(self, seed):
        '''
        generate index
        '''
        x, y = self.info.x, self.info.y
        m = seed
        a = []
        l, r = [], []
        for _ in range(y):
            lr, rr = [], []
            for _ in range(x):
                if m % 2 == 0:
                    lr.insert(0, m)
                    rr.append(m + 1)
                else:
                    lr.insert(0, -m)
                    rr.append(-m - 1)
                m += 1
            l.append(lr)
            r.append(rr)
        a.append(l)
        a.append(r)
        return a

    def pageLayout(self, seed):
        '''
        page layout
        '''
        pageLayoutList = self.genIndex(seed)
        for i in pageLayoutList:
            page = PageMerge()
            y_pos = 0
            for j in i:
                x_pos = 0
                for k in j:
                    page.add(self.objs[k])
                    page[-1].scale(self.info.w / page[-1].w,
                                   self.info.h / page[-1].h)
                    page[-1].x = x_pos * self.info.w
                    page[-1].y = y_pos * self.info.h
                    x_pos += 1
                y_pos += 1
            self.opages.append(page.render())


    def rotate(self, angle):
        '''
        rotate all page
        '''
        for page in self.objs:
            page.Rotate = (int(page.inheritable.Rotate or 0) + angle) % 360

    @staticmethod
    def splitPage(page):
        '''
        Split a page into two (left and right)
        '''
        # return two half of the page
        leftHalf = PageMerge().add(page, viewrect=(0, 0, 0.5, 1)).render()
        rightHalf = PageMerge().add(page, viewrect=(0.5, 0, 0.5, 1)).render()
        # page=[leftHalf, rightHalf]
        return leftHalf, rightHalf


def parseArgs():
    '''
    parse arguments

    :param:None
    :return args: arguments after parse
    '''
    parser = argparse.ArgumentParser(
        description='make printable booklet[A5/A6/A7] from picbook(pdf file).')
    parser.add_argument('inputFilePath', help='Input pdf/img file path.')
    parser.add_argument(
        '-ra',
        '--scanRotateAngle',
        choices=['0', '90', '180', '270'],
        default='',
        help='option pdf file need image extract.')
    parser.add_argument(
        '-or', '--organizePages', default='', help='organize pages.')
    parser.add_argument(
        '-ip',
        '--insertPage',
        default='',
        type=str,
        help='insert blank page. i.e 1:3,insert 3 page after index 1')
    parser.add_argument(
        '-vc',
        '--vCutPage',
        default='',
        help='vertical cutting page range.i.e 1-5')
    parser.add_argument(
        '-bs',
        '--bookletSize',
        choices=['A5', 'A6', 'A7'],
        default='',
        help='option output booklet size.')
    # parser.add_argument(
    #     '-pn',
    #     # '--insertPageNumber',
    #     action='store_true',
    #     help='on/off insert page number,default=off.')
    args = parser.parse_args()
    return args


def main():
    '''
    only main
    '''
    setLog()
    logging.info('Parse input arguments')
    args = parseArgs()
    logging.info('Generate booklet')
    book = booklet(args)
    book.genBook()

if __name__ == '__main__':
    main()

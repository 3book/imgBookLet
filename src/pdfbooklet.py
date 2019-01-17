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
import copy
import logging
import math
# from time import time
from PyPDF2.pdf import PdfFileReader, PdfFileWriter, PageObject
from common import strObj
from common import listObj
from common import setLog

pageLayoutDict = {'A5': (2, 1, 2), 'A6': (2, 2, 2), 'A7': (2, 2, 4)}
printSizeDict = {'A4': (595, 842), 'A5': (421, 595), 'A6': (297, 421)}


def bookletIndexGen(pageNum):
    '''
    TODO
    page number must great 6
    '''
    if pageNum % 4 == 3:
        n, A1, A2, B1, B2 = 0, -1, 0, 1, None
        yield A1, B1
        yield A2, B2
        n, A1, A2, B1, B2 = 3, -3, 2, 3, -2
    elif pageNum % 4 == 2:
        n, A1, A2, B1, B2 = 0, -1, 0, 1, None
        yield A1, B1
        yield A2, B2
        n, A1, A2, B1, B2 = 3, None, 2, 3, -2
        yield A1, B1
        yield A2, B2
        n, A1, A2, B1, B2 = 6, -3, 4, 5, -4
    elif pageNum % 4 == 1:
        n, A1, A2, B1, B2 = 0, -1, 0, 1, None
        yield A1, B1
        yield A2, B2
        n, A1, A2, B1, B2 = 3, None, 2, 3, None
        yield A1, B1
        yield A2, B2
        n, A1, A2, B1, B2 = 5, -3, 2, 3, -2
    elif pageNum % 4 == 0:
        n, A1, A2, B1, B2 = 0, -1, 0, 1, -2
    while n < pageNum:
        yield A1, B1
        yield A2, B2
        A1, A2 = A1 - 2, A2 + 2
        B1, B2 = B1 + 2, B2 - 2
        n += 4


class pdfpage(object):
    '''
    TODO
    '''

    def __init__(self, pageObj, landscape=True, pageSize=None):
        # PageObject.__init__(self)
        self.pageObj = pageObj
        self.landscape = landscape
        self.w = pageObj.mediaBox.getUpperRight_x(
        ) - pageObj.mediaBox.getLowerLeft_x()
        self.h = pageObj.mediaBox.getUpperRight_y(
        ) - pageObj.mediaBox.getLowerLeft_y()
        if pageSize:
            if landscape:
                self.w = max(pageSize)
                self.h = min(pageSize)
            else:
                self.w = min(pageSize)
                self.h = max(pageSize)
            self.pageObj.scaleTo(self.w, self.h)
        # self.pageObj=PageObject
    @staticmethod
    def vsplit(pageObj):
        '''
        TODO
        '''
        leftHalfPage = copy.copy(pageObj)
        rightHalfPage = copy.copy(pageObj)
        x0, y0, x1, y1 = leftHalfPage.mediaBox
        lbox = (x0, y0, x0 + (x1 - x0) / 2, y1)
        for box in (leftHalfPage.artBox, leftHalfPage.bleedBox,
                    leftHalfPage.cropBox, leftHalfPage.mediaBox,
                    leftHalfPage.trimBox):
            box.lowerLeft = lbox[:2]
            box.upperRight = lbox[2:]
        x0, y0, x1, y1 = rightHalfPage.mediaBox
        rbox = (x0 + (x1 - x0) / 2, y0, x1, y1)
        for box in (rightHalfPage.artBox, rightHalfPage.bleedBox,
                    rightHalfPage.cropBox, rightHalfPage.mediaBox,
                    rightHalfPage.trimBox):
            box.lowerLeft = rbox[:2]
            box.upperRight = rbox[2:]
        return leftHalfPage, rightHalfPage

    def mergeCalc(self, **kw):
        '''
        TODO
        '''
        # sx = 1 / kw['xn']
        # sy = 1 / kw['yn']
        sx, sy = 1, 1
        tx = kw['x'] * float(self.w) * sx
        ty = kw['y'] * float(self.h) * sy
        ctm = [sx, 0, 0, sy, tx, ty]
        return ctm

def pdfBookLet(inputFile, outputFile, bookletSize):
    '''
    Make a printable PDF booklet.

    :inputFile  : Input PDF file .
    :outputFile : Output PDF file .
    :bookletsize: Output booklet size.
    :return: None
    :exception :None
    '''
    logging.info('start. args=%s', (inputFile, bookletSize))
    with open(outputFile, 'wb') as file:
        pass
    with open(inputFile, 'rb') as pdfFileObj:
        pdfReader = PdfFileReader(pdfFileObj, strict=True)
        pageNum = pdfReader.getNumPages()
        pdfWrite = PdfFileWriter()
        pageIndex = bookletIndexGen(pageNum)
        pageLayout = pageLayoutDict[bookletSize]
        w, h = printSizeDict[bookletSize]
        ww = w * pageLayout[2]
        hh = h * pageLayout[1]
        pageBlank = PageObject.createBlankPage(width=w, height=h)
        pageA = PageObject.createBlankPage(width=ww, height=hh)
        pageB = PageObject.createBlankPage(width=ww, height=hh)
        xn, yn = pageLayout[2], pageLayout[1]
        logging.info('Booklet information. srcNumPages=%5s snkPageLayout=%10s', pageNum,pageLayout)
        n = 0
        for index in pageIndex:
            x = n % xn
            y = int(n / xn) % yn
            A, B = index
            lastPage = 0 if 2 * n < pageNum else 1
            pageObjA = pdfReader.getPage(A) if A is not None else pageBlank
            # pageObjA.mediaBox.lowerLeft=(31,596)
            # pageObjA.mediaBox.upperRight=(581,197)
            pdfpageObjA = pdfpage(
                pageObjA, landscape=False, pageSize=printSizeDict[bookletSize])
            ctm = pdfpageObjA.mergeCalc(xn=xn, yn=yn, x=x, y=y)
            pageA.mergeTransformedPage(pdfpageObjA.pageObj, ctm, expand=False)
            #write back page
            pageObjB = pdfReader.getPage(B) if B is not None else pageBlank
            pdfpageObjB = pdfpage(
                pageObjB, landscape=False, pageSize=printSizeDict[bookletSize])
            ctm = pdfpageObjB.mergeCalc(xn=xn, yn=yn, x=x, y=y)
            pageB.mergeTransformedPage(pdfpageObjB.pageObj, ctm, expand=False)
            n += 1
            logging.info('Front merge. srcPageNum=%-4sLocation=%s', A,(x,y))
            logging.info('Back merge.  srcPageNum=%-4sLocation=%s', B,(x,y))
            if n % (xn * yn) == 0 or lastPage:
                pageA.compressContentStreams()
                pageB.compressContentStreams()
                pdfWrite.addPage(pageA)
                pdfWrite.addPage(pageB)
                with open(outputFile, 'ab') as file:
                    pdfWrite.write(file)
                    logging.info('write page. snkPageNum=%s', math.ceil(n/(xn*yn)))
                pageA = PageObject.createBlankPage(width=ww, height=hh)
                pageB = PageObject.createBlankPage(width=ww, height=hh)
    logging.info('End. output=%s', outputFile)


def pdfOrganize(inputFile, outputFile, args):
    '''
    Organize input PDF file. include extra,cut,insert blank page,insert page number

    :inputFile  : Input PDF file .
    :outputFile : Output PDF file .
    :args       : Organize arguments.
    :return: None
    :exception :None
    '''
    logging.debug('start. input=%s', (inputFile, args))
    with open(outputFile, 'wb') as file:
        pass
    with open(inputFile, 'rb') as pdfFileObj:
        try:
            pdfReader = PdfFileReader(pdfFileObj, strict=False)
            pdfWrite = PdfFileWriter()
        except IOError:
            logging.error('IOError. inputfile=%s', inputFile)
        pageNum = listObj(range(pdfReader.numPages))
        pageOrderIdx = pageNum.organize(args.organizePages)
        pageCutIdx = pageNum.extract(args.vCutPage)
        pageInsertIdx = strObj.str2dict(args.insertPage)
        if pageCutIdx or pageInsertIdx:
            pageOrderIdx = pageOrderIdx if pageOrderIdx else range(
                pdfReader.numPages)
        if pageOrderIdx:
            for i in pageOrderIdx:
                pageObj = pdfReader.getPage(i)
                pageObj.compressContentStreams()
                if i in pageCutIdx:
                    l, r = pdfpage.vsplit(pageObj)
                    pdfWrite.addPage(l)
                    pdfWrite.addPage(r)
                    logging.info('split page %s to two halves.', i)
                else:
                    pdfWrite.addPage(pageObj)
                    logging.info('Extract page %s.', i) 
                if pageInsertIdx:
                    key = str(i + 1)  #index=0 mean page number 1
                    if key in pageInsertIdx:
                        logging.info('Insert %s blank page after page %s.', int(pageInsertIdx[key]), i)
                        for _ in range(int(pageInsertIdx[key])):
                            pdfWrite.addBlankPage()
                with open(outputFile, 'ab') as file:
                    pdfWrite.write(file)
    logging.info('End. output=%s', outputFile)


def parseArgs():
    '''
    parse arguments

    :param:None
    :return args: arguments after parse
    '''
    logging.info('Start.')
    parser = argparse.ArgumentParser(
        description='make printable booklet[A5/A6/A7] from picbook(pdf file).')
    parser.add_argument('InputFilePath', help='Input pdf/img file path.')
    parser.add_argument(
        '-bs',
        '--bookletSize',
        choices=['A5', 'A6', 'A7'],
        default='',
        help='option output booklet size.')
    parser.add_argument(
        '-ip',
        '--insertPage',
        default='',
        type=str,
        help='insert blank page. i.e 1:3,insert 3 page after index 1')
    parser.add_argument(
        '-ro', '--organizePages', default='', help='reorganize pages.')
    parser.add_argument(
        '-vc',
        '--vCutPage',
        default='',
        help='vertical cutting page range.i.e 1-5')
    parser.add_argument(
        '-pn',
        '--insertPageNumber',
        action='store_true',
        help='on/off insert page number,default=off.')
    args = parser.parse_args()
    logging.info('End. output=%s',args)
    return args


def main():
    '''
    only main
    '''
    logging.info('Start')
    args = parseArgs()
    inputFilePathCfg = args.InputFilePath
    bookletSizeCfg = args.bookletSize
    insertPageCfg = args.insertPage
    organizePagesCfg = args.organizePages
    vCutPageCfg = args.vCutPage
    # insertPageNumber = args.insertPageNumber
    outputFile1 = os.path.splitext(inputFilePathCfg)[0] + '_organize' + '.pdf'
    outputFile2 = os.path.splitext(
        inputFilePathCfg)[0] + '_' + bookletSizeCfg + '.pdf'
    if organizePagesCfg or vCutPageCfg or insertPageCfg:
        pdfOrganize(inputFilePathCfg, outputFile1, args)
    if bookletSizeCfg:
        inputFile = outputFile1 if os.path.exists(
            outputFile1) else inputFilePathCfg
        pdfBookLet(inputFile, outputFile2, args.bookletSize)
    logging.info('End.')


if __name__ == '__main__':
    setLog()
    main()
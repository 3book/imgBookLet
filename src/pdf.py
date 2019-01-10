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
from PyPDF2 import PdfFileReader, PdfFileWriter
from utils import string2KV
from utils import objListSlice

logging.basicConfig(
    level=logging.DEBUG,
    format=
    '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%a, %d %b %Y %H:%M:%S',
    filename='log.log',
    filemode='w')
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def pdfBookLet(pdf, bookletSize, outputFileName):
    '''
    Make a printable pdf booklet.

    :param pdf: A pdf file list.
    :return: None
    :exception :None
    '''
    #first fold for paper A5/A6
    if bookletSize in ['A5', 'A6', 'A7']:
        imList = []
        ims = insertBlankpage(ims, 0)
        for i in range(int(len(ims) / 2)):
            if i % 2 == 0:
                im = imMerge(2, ims.pop(0), ims.pop())
            else:
                im = imMerge(2, ims.pop(), ims.pop(0))
            imList.append(im)
    #second fold for paper A6
    if bookletSize in ['A6', 'A7']:
        ims = imList
        imList = []
        ims = insertBlankpage(ims)
        for i in range(int(len(ims) / 2)):
            im = imMerge(1, ims.pop(), ims.pop(0))
            imList.append(im)
    #third fold for paper A7
    if bookletSize in ['A7']:
        ims = imList
        imList = []
        ims = insertBlankpage(ims)
        for i in range(int(len(ims) / 2)):
            if i % 2 == 0:
                im = imMerge(2, ims.pop(0), ims.pop())
            else:
                im = imMerge(2, ims.pop(), ims.pop(0))
            imList.append(im)
    imList[0].save(
        outputFileName,
        'pdf',
        resolution=100.0,
        save_all=True,
        append_images=imList[1:])



class pdfPage:
    def __init__(self, page):
        self.page = page

    def cropPage(self, cropBox):
        '''
        crop page
        '''
        # x0, y0 = page.cropBox.lowerLeft
        # x1, y1 = page.cropBox.upperRight
        # # x0, y0, x1, y1 = float(x0), float(y0), float(x1), float(y1)
        # # x0, x1 = x0+crop[0]*(x1-x0), x1-crop[2]*(x1-x0)
        # y0, y1 = y0+crop[3]*(y1-y0), y1-crop[1]*(y1-y0)
        # Note that the coordinate system is up-side down compared with Qt.
        # Update the various PDF boxes
        page = self.page
        for box in (page.artBox, page.bleedBox, page.cropBox, page.mediaBox,
                    page.trimBox):
            box[0] = cropBox[0]
            box[1] = cropBox[1]
            box[2] = cropBox[2]
            box[3] = cropBox[3]
            #     box.lowerLeft = (x0, y0)
            #     box.upperRight = (x1, y1)
            # if rotate != 0:
            #     page.rotateClockwise(rotate)
        return page

    def vsplit(self):
        x0, y0, x1, y1 = self.page.cropBox
        leftHalfBox = (x0, y0, int(x1 / 2), y1)
        leftHalfPage = self.cropPage(leftHalfBox)
        rightHalfBox = (int(x1 / 2), y0, x1, y1)
        rightHalfPage = self.cropPage(rightHalfBox)
        return leftHalfPage, rightHalfPage


def parseArgs():
    '''
    parse arguments
    :param:None
    :return args: arguments after parse
    '''
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
    return args


def main():
    '''
    only main
    '''
    args = parseArgs()
    logging.info('input %s:', args)
    inputFilePathCfg = args.InputFilePath
    bookletSizeCfg = args.bookletSize
    insertPageCfg = args.insertPage
    organizePagesCfg = args.organizePages
    vCutPageCfg = args.vCutPage
    # insertPageNumber = args.insertPageNumber
    outputFilePath = os.path.splitext(
        inputFilePathCfg)[0] + '_booklet_' + bookletSizeCfg + '.pdf'
    with open(inputFilePathCfg, 'rb') as pdfFileObj:
        try:
            pdfReader = PdfFileReader(pdfFileObj, strict=False)
            pdfWrite = PdfFileWriter()
        except IOError:
            logging.error('%s read error!', inputFilePathCfg)
        # string = '1,5-9,2-4,10-,4'
        rangeSlice = objListSlice(range(pdfReader.numPages))
        pageOrderIdx = rangeSlice.reorganize(organizePagesCfg)
        pageCutIdx = rangeSlice.extract(vCutPageCfg)
        pageInsertIdx = string2KV(insertPageCfg)
        logging.info('pageOrderIdx=%s pageCutIdx=%s pageInsertIdx=%s:',
                     pageOrderIdx, pageCutIdx, pageInsertIdx)
        if pageCutIdx or pageInsertIdx:
            pageOrderIdx = pageOrderIdx if pageOrderIdx else range(
                pdfReader.numPages)
        if pageOrderIdx:
            for i in pageOrderIdx:
                # TODO
                # objWrite = []
                pageObj = pdfReader.getPage(i)
                # objWrite += pageObj
                if i in pageCutIdx:
                    # page = pdfPage(pageObj)
                    import copy
                    leftHalfPage = copy.copy(pageObj)
                    rightHalfPage = copy.copy(pageObj)
                    leftHalfPage.mediaBox.upperRight = (
                        leftHalfPage.mediaBox.getUpperRight_x() / 2,
                        leftHalfPage.mediaBox.getUpperRight_y())
                    box=leftHalfPage.mediaBox
                    pdfWrite.addPage(leftHalfPage)

                    rightHalfPage.mediaBox.upperLeft = leftHalfPage.mediaBox.getUpperRight(
                    )
                    pdfWrite.addPage(rightHalfPage)
                else:
                    pdfWrite.addPage(pageObj)
                if pageInsertIdx:
                    key = str(i+1)  #index=0 mean page number 1 
                    if key in pageInsertIdx:
                        for _ in range(int(pageInsertIdx[key])):
                            pdfWrite.addBlankPage()
                with open(outputFilePath, 'wb') as file:
                    pdfWrite.write(file)


if __name__ == '__main__':
    main()

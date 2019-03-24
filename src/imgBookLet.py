#!/bin/env python
# -*-coding:utf-8-*-
#pylint: disable = C0103
'''
Copyright 2019 @3book.
Format Scanned-pdf/image file to printable booklet.
Only image in pdf will be output.so Scanned document is most suitable.
'''
__author__ = '3book'
__version__ = '0.0.1'

import os
import argparse
from io import BytesIO
import PyPDF2
from PIL import Image, ImageDraw


def pdfExtractIm(pdfFilePath, needVcut):
    '''
    Extract images from a pdf file.

    :param pdfFile: A pdf file path.
    :param size: The requested size, in points.
    :return: a image-list.
    :exception TypeError: If no image inside the file.
    '''
    ims = []
    with open(pdfFilePath, 'rb') as pdfFileObj:
        try:
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj, strict=False)
        except IOError:
            print('Error,input file read error!')
        for i in range(pdfReader.numPages):
            pageObj = pdfReader.getPage(i)
            try:
                xObject = pageObj['/Resources']['/XObject'].getObject()
                for obj in xObject:
                    if xObject[obj].get('/Subtype', None) == '/Image':
                        im = extractImData(xObject[obj])
                        if needVcut:
                            ims += list(imVcut(im))
                        else:
                            ims.append(im)
                    # else:
            except KeyError:
                print('KeyError,pdfFilePath %s page has no XObject' % i)

    if ims == []:
        raise TypeError(pdfFilePath, ' can not find image')
    else:
        return ims


def extractImData(obj):
    '''
    Extract image data from pdf Object.
    :param obj: element within a pdf file page.
    :return: a image object.
    :exception IOError: the image data has not support!.
    '''
    size = (obj['/Width'], obj['/Height'])
    if obj['/ColorSpace'] == '/DeviceRGB':
        mode = 'RGB'
    else:
        mode = 'P'
    if obj.get('/Filter', None) == '/FlateDecode':
        data = obj.getData()
        im = Image.frombytes(mode, size, data)
    elif obj.get('/Filter', None) == '/DCTDecode':
        data = obj._data
        im = Image.open(BytesIO(data))
    elif obj.get('/Filter', None) == '/JPXDecode':
        data = obj._data
        im = Image.open(BytesIO(data))
    else:
        raise TypeError('the image in this pdf file has not support!')
    return im


def openIms(inputFilePath):
    '''
    Open all images file from gived file path.
    '''
    fileList = [
        os.path.join(inputFilePath, x) for x in os.listdir(inputFilePath)
    ]
    fileList.sort()
    try:
        ims = list(map(Image.open, fileList))
    except TypeError as ImageFileNotSupported:
        raise ImageFileNotSupported
    if 'transparency' in ims[0].info:
        ims = [pngConvert(im) for im in ims]
    return ims


def pngConvert(im):
    '''
    Convert 'P' mode  to 'RGBA'.
    '''
    im = im.convert(mode='RGBA', palette=0)
    imBlank = Image.new('RGBA', im.size, (255, 255, 255))
    imBlank.paste(im, (0, 0), im)
    return imBlank


def imVcut(im):
    '''
    Cut image vertically into two halves.

    :param im: A image object.
    :return: a image tuple.
    :exception :None
    '''
    size = im.size
    imLeftPart = im.crop((0, 0, size[0] / 2, size[1]))
    imRrightPart = im.crop((size[0] / 2, 0, size[0], size[1]))
    return imLeftPart, imRrightPart


def insertBlankpage(ims, frontInsertPages=None):
    '''
    Insert blank image.

    :param ims: A image object list.
    :return: A image object list.
    :exception :None
    '''
    length = len(ims)
    index = int(length / 4)*2
    imsBlank = [Image.new('RGB', ims[0].size, (255, 255, 255))] * (-length % 4)
    if frontInsertPages == None:
        imList = ims[:index] + imsBlank + ims[index:]
    else:
        imsBlankFront = imsBlank[:frontInsertPages]
        imsBlankback = imsBlank[frontInsertPages:]
        imList = ims[0:1] + imsBlankFront + ims[1:-1] + imsBlankback + ims[-1:]
    return imList


def insertPageNumber(index, im):
    '''
    insert page number
    '''
    size = im.size
    xy = (size[0] / 2, size[1] - 50)
    ImageDraw.Draw(im).text(xy, str(index), fill=(0, 0, 0))
    xy = (size[0] / 2, 50)
    ImageDraw.Draw(im).text(xy, '3book', fill=(196, 196, 196, 196))
    # return im


def imModify(ims, needVcut, bookLetSize, needPageNumber):
    '''
    Modify image to be printable.
        Resize image to page size.
        Insert page number.
    '''
    #
    if needVcut:
        ims.append(ims.pop(0))

    #A4 72dpi   595×841
    #A4 96dpi   794×1126
    #A4 150dpi  1240×1754
    #A4 300dpi  2480×3508
    printSizeDict = {'A5': (595, 842), 'A6': (421, 595), 'A7': (297, 421)}
    # ims=map(setPageSize,ims)
    # ims=map(pageNumber,ims)
    imList = []
    for index, im in enumerate(ims):
        # resize image
        im = im.resize(printSizeDict[bookLetSize], Image.ANTIALIAS)
        #insert page number
        if needPageNumber:
            if index not in (0, len(ims) - 1):
                insertPageNumber(index, im)
        imList.append(im)
    return imList


def imMerge(hNum, *ims):
    '''
    Merge Multiple images to one page.

    :param hNum: Number of pictures placed horizontally.
    :param ims: A image object list.
    :return: A image obgect.
    :exception :None
    '''
    w, h = ims[0].size[0], ims[0].size[1]
    vNum = int(len(ims) / hNum) + (len(ims) % hNum > 0)
    im = Image.new('RGB', (w * hNum, h * vNum), (255, 255, 255))
    ims = list(ims)
    for yn in range(vNum):
        for xn in range(hNum):
            im.paste(ims.pop(), (w * xn, h * yn))
    return im


def imgBookLet(ims, bookLetSize, outputFileName):
    '''
    Make a printable pdf booklet.

    :param ims: A image object list.
    :return: None
    :exception :None
    '''
    #first fold for paper A5/A6
    if bookLetSize in ['A5', 'A6', 'A7']:
        imList = []
        ims = insertBlankpage(ims,0)
        for i in range(int(len(ims) / 2)):
            if i % 2 == 0:
                im = imMerge(2, ims.pop(0), ims.pop())
            else:
                im = imMerge(2, ims.pop(), ims.pop(0))
            imList.append(im)
    #second fold for paper A6
    if bookLetSize in ['A6', 'A7']:
        ims = imList
        imList = []
        ims = insertBlankpage(ims)
        for i in range(int(len(ims) / 2)):
            im = imMerge(1, ims.pop(), ims.pop(0))
            imList.append(im)
    #third fold for paper A7
    if bookLetSize in ['A7']:
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
        '-bs',
        '--bookSize',
        choices=['A5', 'A6', 'A7'],
        default='A6',
        help='option output booklet size,default=A6.')
    parser.add_argument(
        '-vc',
        '--verticalCutting',
        action='store_true',
        help='on/off vertical cutting every page,default=off.')
    parser.add_argument(
        '-pg',
        '--pageNumber',
        action='store_true',
        help='on/off insert page number,default=off.')
    args = parser.parse_args()
    return args


def main():
    '''
    only main
    '''
    args = parseArgs()
    inputFilePath = args.inputFilePath
    bookLetSize = args.bookSize
    needVcut = args.verticalCutting
    needPageNumber = args.pageNumber
    outputFilePath = os.path.splitext(
        inputFilePath)[0] + '_booklet_' + bookLetSize + '.pdf'

    # try:
    if os.path.isfile(inputFilePath) and os.path.splitext(
            inputFilePath)[1] == '.pdf':
        imgs = pdfExtractIm(inputFilePath, needVcut)
    elif os.path.isdir(inputFilePath):
        imgs = openIms(inputFilePath)
    else:
        raise FileNotFoundError('paf/img file do not find')
    imgs = imModify(imgs, needVcut, bookLetSize, needPageNumber)

    # except Exception:
    # print(Exception)
    imgBookLet(imgs, bookLetSize, outputFilePath)


if __name__ == '__main__':
    main()

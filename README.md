
# booklet
Format PDF files to printable booklet.

![test](https://img.shields.io/badge/script-Yes-00ff00.svg)
![test](https://img.shields.io/badge/exe-No-ff0000.svg)

--------
## Requirement
- [pdfrw]()
<!--
## Features
- Extract image in pdf file. So scanned document is suitable.
- Format every image to output booklet size.
- Output printable booklet.
- Supported booklet page sizes include A5/A6/A7. 
- Insert blank page when the number of images is not multiple of 4.
- Add page numbers.
- Cut image vertically into two halves.
--> 
## Usage 
```
./booklet.py -h
usage: booklet.py [-h] [-ra {0,90,180,270}] [-or ORGANIZEPAGES]
                  [-ip INSERTPAGE] [-vc VCUTPAGE] [-bs {A5,A6,A7}]
                  inputFilePath

make printable booklet[A5/A6/A7] from picbook(pdf file).

positional arguments:
  inputFilePath         Input pdf/img file path.

optional arguments:
  -h, --help            show this help message and exit
  -ra {0,90,180,270}, --scanRotateAngle {0,90,180,270}
                        option pdf file need image extract.
  -or ORGANIZEPAGES, --organizePages ORGANIZEPAGES
                        organize pages. i.e -3 4-6 8- 7
  -ip INSERTPAGE, --insertPage INSERTPAGE
                        insert blank page. i.e 1:3, insert 3 pages after index
                        1
  -vc VCUTPAGE, --vCutPage VCUTPAGE
                        vertical cutting page range. i.e 1-5
  -bs {A5,A6,A7}, --bookletSize {A5,A6,A7}
                        option output booklet size.
```
<!--
## To do
- [x] Extract images from a pdf file.
- [x] Open all images file from gived file path.
- [x] Cut image vertically into two halves.
- [x] Resize image to page size.
- [x] Insert blank image.
- [x] Insert page number
- [x] Merge Multiple images to one page.
- [x] Make a printable pdf booklet.
- [ ] Add page Margins.
- [ ] Test and provided example.
- [ ] Provided executable file.
--> 
## Example
https://freekidsbooks.org/wp-content/uploads/2018/09/where-is-lulu_en_20180503-FKB.pdf

./booklet.py where-is-lulu_en_20180503-FKB.pdf -vc 3-17
./booklet.py where-is-lulu_en_20180503-FKB_booklet.pdf -or '1 3 2 5-' -bs A5
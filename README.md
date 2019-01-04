
# booklet
Format image files or scanned documents (PDF)  to printable booklet.

![test](https://img.shields.io/badge/script-Yes-00ff00.svg)
![test](https://img.shields.io/badge/exe-No-ff0000.svg)

--------
## First
**The most important thing is to forgive my poor English.**

## Requirement
- [PyPDF2]()
- [Pillow]()
## Features
- Extract image in pdf file. So scanned document is suitable.
- Format every image to output booklet size.
- Output printable booklet.
- Supported booklet page sizes include A5/A6/A7. 
- Insert blank page when the number of images is not multiple of 4.
- Add page numbers.
- Cut image vertically into two halves.
## Usage 
```
python bookLet.py [-h] [-bs {A5,A6,A7}] [-vc] [-pg] inputFilePath
 
positional arguments:
  inputFilePath         Input pdf/img file path.

optional arguments:
  -h, --help            show this help message and exit
  -bs {A5,A6,A7}, --bookSize {A5,A6,A7}
                        option output booklet size,default=A6.
  -vc, --verticalCutting
                        on/off vertical cutting every page,default=on.
  -pg, --pageNumber     on/off insert page number,default=on.
```
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
<!--
## Example

--> 
import re
import shutil

import fitz

import fetch_dampt, fetch_dpmms
import requests
import os
import base64


def get_base64(s:str) -> str:
   return base64.b64encode(s.encode()).decode()


if not os.path.exists('pdfs'):
   os.makedirs('pdfs')

# sheetarr [url, name, number]
def fetch_sheet(sheetarr) -> str:
   if not os.path.exists('pdfs'):
      os.makedirs('pdfs')

   id = get_base64(sheetarr[0]) # url -> b64 to avoid collisions
   filepath = f"pdfs/{id}.pdf"

   if not os.path.exists(filepath):
      print(f"couldn't find {sheetarr[1]}, sheet number {sheetarr[2]}, fetching to {filepath}")
      with requests.get(sheetarr[0], stream=True) as r:
         with open(filepath, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

   return filepath


def get_start_end(doc, q, course, formats):
   # fuck sheet formatting
   startstr = f"\n{q}."
   endstr = f"\n{q+1}."
   # if type == "grm":
   #    startstr = f"\n({q})"
   #    endstr = f"\n({q + 1})"
   for arr in formats:
      if course.lower() == arr[0].lower():
         print(f"newformat: {arr[1]}")
         startstr = arr[1].replace("questionnum",str(q))
         endstr = arr[1].replace("questionnum",str(q+1))

   # bad and open to bugs but fine here
   def findall(full_string, sub_string):
      return [index for index in range(len(full_string)) if full_string.startswith(sub_string, index)]
   start = [0,0]
   for x in range(len(doc)):
      page = doc.load_page(x)
      text:str= page.get_text()
      starts = findall(text, startstr)
      if text.startswith(startstr.strip()):
         starts+=[0]
      ends = findall(text, endstr)
      print(startstr)
      if text.startswith(endstr.strip()):
         ends+=[0]
      if starts:
         start = [starts[0], x]
      if ends:
         end = [ends[0], x]
      else:
         continue
      return [start,end]

   end = [-1, len(doc)-1]
   return [start,end]


# cursed code, pymupdf cant parse text that includes "-\n" for some god forsaken reason
# didn't open an issue but pls do
# also probably will have a few lopsided qs if the - is the furthest thing on the right :)
def get_rects(start, end, page):
   text = page.get_text()[start:end]
   textbits = text.split("-\n")
   # print(textbits)
   rectdict = []
   for i, t2 in enumerate(textbits):
      # some sheets like vp, i hate this
      t = t2.strip("Copyright © 2022 University of Cambridge. Not to be quoted or reproduced without permission.")
      if page.search_for(t):
         rectdict += page.search_for(t)
   return rectdict

def fetch_question(filepath: str, q: int, course, formats,debug=False) -> None:
   doc = fitz.open(filepath)
   start, end = get_start_end(doc,q,course,formats)
   if debug:
      print(start,end)
   # if 1 page q
   if start[1] == end[1]:
      page = doc.load_page(start[1])
      text = page.get_text()
      rectdict = get_rects(start[0],end[0],page)
      # rectdict = page.search_for(text[start[0]:end[0]])
      for rectd in range(len(rectdict) - 1):
         rectdict[0].include_rect(rectdict[rectd + 1])
      delta = fitz.Point(8, 3)
      deltay = fitz.Point(0, 4)
      rectf = fitz.Rect(rectdict[0].tl - delta -deltay, rectdict[0].br + delta)
      if debug:
         page.get_pixmap(clip=rectf, dpi=300).save("out.png")
      return page.get_pixmap(clip=rectf, dpi=300).tobytes()
   else:
      page = doc.load_page(start[1])
      text = page.get_text()
      rectdict = get_rects(start[0],-1,page)#page.search_for(text[start[0]:-1])
      for rectd in range(len(rectdict) - 1):
         rectdict[0].include_rect(rectdict[rectd + 1])

      delta = fitz.Point(8, 3)
      deltay = fitz.Point(0, 4)
      rectf = fitz.Rect(rectdict[0].tl - delta - deltay, rectdict[0].br + delta)
      # page.get_pixmap(clip=rectf, dpi=300).save("out.png")

      img1 = page.get_pixmap(clip=rectf, dpi=300)

      page = doc.load_page(end[1])
      text = page.get_text()
      rectdict = get_rects(0,end[0],page)#page.search_for(text[0:end[0]])
      # hacky fix
      if not rectdict:
         if debug:
            img1.save("out.png")
         return img1.tobytes()
      for rectd in range(len(rectdict) - 1):
         rectdict[0].include_rect(rectdict[rectd + 1])

      delta = fitz.Point(8, 3)
      deltay = fitz.Point(0, 4)
      topleft = fitz.Point(rectf.x0,(rectdict[0].tl - delta - deltay).y)
      bottomright = fitz.Point(rectf.x1,(rectdict[0].br +delta).y)
      rectf2 = fitz.Rect(topleft, bottomright)


      img2 = page.get_pixmap(clip=rectf2, dpi=300)
      col = 1  # tiles per row
      lin = 2 # tiles per column
      hgt = img1.height + img2.height #src.width * col  # width of target
      wid = img1.width # height of target
      # create target pixmap
      src = fitz.Pixmap(img1.colorspace, (0, 0, wid, hgt), img1.alpha)

      # now fill target with the tiles

      img1.set_origin(0,0)
      img2.set_origin(0,0)

      src.set_origin(0,0)
      src.copy(img1, (0,0,img1.irect.x1,img1.irect.y1))
      src.set_origin(0, -img1.height)
      src.copy(img2, (0,0,img2.irect.x1,img2.irect.y1))
      if debug:
         src.save("out.png")
      return src.tobytes()

# other method, maybe better
# def fetch_question_2(filepath: str, q: int, course, formats) -> None:
#    print("fetching")
#    # fuck sheet formatting, this allows for custom formats to be recognised, below is by far the most common
#    startstr = f"\n{q}."
#    endstr = f"\n{q + 1}."
#    # if type == "grm":
#    #    startstr = f"\n({q})"
#    #    endstr = f"\n({q + 1})"
#    for arr in formats:
#       if course.lower() == arr[0].lower():
#          print(f"newformat: {arr[1]}")
#          startstr = arr[1].replace("questionnum", str(q))
#          endstr = arr[1].replace("questionnum", str(q + 1))
#
#    doc:fitz.Document = fitz.open(filepath)
#    for i, page in enumerate(doc):
#       startrects = page.search_for(startstr)
#       endrects  =  page.search_for(endstr)
#
#       print(endrects,startrects)

if __name__ == "__main__":
   sheet = ['https://www.dpmms.cam.ac.uk/study/IB/LinearAlgebra/2022-2023/lin-alg-ex4-2022.pdf', 'VP', 2]
   # print(fetch_dpmms.fetch_dpmms()[0])
   fetch_question("pdfs/aHR0cDovL3d3dy5kcG1tcy5jYW0uYWMudWsvc3R1ZHkvSUIvTGluZWFyQWxnZWJyYS8yMDIyLTIwMjMvbGluLWFsZy1leDItMjAyMi5wZGY=.pdf",7,"La",[],debug=True)

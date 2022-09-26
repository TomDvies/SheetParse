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


def get_start_end(doc, q, type, alias_data):
   # fuck sheet formatting
   startstr = f"\n{q}."
   endstr = f"\n{q+1}."
   # if type == "grm":
   #    startstr = f"\n({q})"
   #    endstr = f"\n({q + 1})"
   for arr in alias_data["exceptions"]:
      if type == arr[1]:
         print(f"newformat: {arr[2]}")
         startstr = arr[2].replace("questionnum",str(q))
         endstr = arr[2].replace("questionnum",str(q+1))

   # bad and open to bugs but fine here
   def findall(full_string, sub_string):
      return [index for index in range(len(full_string)) if full_string.startswith(sub_string, index)]
   start = [0,0]
   for x in range(len(doc)):
      page = doc.load_page(x)
      text:str= page.get_text()
      starts = findall(text, startstr)
      ends = findall(text, endstr)
      if starts:
         start = [starts[0], x]
      if ends:
         end = [ends[0], x]
      else:
         continue
      return [start,end]

   end = [-1, len(doc)-1]
   return [start,end]



def fetch_question(filepath: str, q: int, type, alias_data) -> None:

   # input = "IA 2001 2 II 12F" example input
   # course, year, paper, section, question = input.split(" ")
   print("fetching")
   doc = fitz.open(filepath)
   start, end = get_start_end(doc,q,type,alias_data)
   # print(start,end)
   # if 1 page q
   # print(start,end)
   if start[1] == end[1]:
      page = doc.load_page(start[1])
      text = page.get_text()
      rectdict = page.search_for(text[start[0]:end[0]])
      for rectd in range(len(rectdict) - 1):
         rectdict[0].include_rect(rectdict[rectd + 1])

      delta = fitz.Point(8, 3)
      deltay = fitz.Point(0, 4)
      rectf = fitz.Rect(rectdict[0].tl - delta -deltay, rectdict[0].br + delta)
      # page.get_pixmap(clip=rectf, dpi=300).save("out.png")

      return page.get_pixmap(clip=rectf, dpi=300).tobytes()
   else:
      page = doc.load_page(start[1])
      text = page.get_text()
      rectdict = page.search_for(text[start[0]:-1])
      for rectd in range(len(rectdict) - 1):
         rectdict[0].include_rect(rectdict[rectd + 1])

      delta = fitz.Point(8, 3)
      deltay = fitz.Point(0, 4)
      rectf = fitz.Rect(rectdict[0].tl - delta - deltay, rectdict[0].br + delta)
      # page.get_pixmap(clip=rectf, dpi=300).save("out.png")

      img1 = page.get_pixmap(clip=rectf, dpi=300)

      page = doc.load_page(end[1])
      text = page.get_text()
      rectdict = page.search_for(text[0:end[0]])
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
      src.save("out.png")
      return src.tobytes()

if __name__ == "__main__":
   sheet = ['http://www.dpmms.cam.ac.uk/study/IB/GroupsRings%2BModules/2021-2022/Example%20sheet%202.pdf', 'Analysis I ', 1]
   # print(fetch_dpmms.fetch_dpmms()[0])
   fetch_question(fetch_sheet(sheet),8,"grm")

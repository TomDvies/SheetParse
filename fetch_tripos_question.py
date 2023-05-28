import base64
import os
import shutil
# import fetch_dampt, fetch_dpmms
import fitz
import requests


def get_base64(s: str) -> str:
    return base64.b64encode(s.encode()).decode()


if not os.path.exists('pdfs'):
    os.makedirs('pdfs')


# sheetarr [url, name, number]
def fetch_paper_year(paperarr) -> str: # [link,year,part,number/type]
    if not os.path.exists('pdfs'):
        os.makedirs('pdfs')
    fileid = get_base64(paperarr[0])  # url -> b64 to avoid collisions
    filepath = f"pdfs/{fileid}.pdf"

    if not os.path.exists(filepath):
        print(f"couldn't find {paperarr[1]} {paperarr[2]} {paperarr[3]}, fetching to {filepath}")
        with requests.get(paperarr[0], stream=True) as r:
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(r.raw, f)
    return filepath


def get_start_end(doc,paper,question,part,year):
    def findall(full_string, sub_string):
        return [index for index in range(len(full_string)) if full_string.startswith(sub_string, index)]
    start = [0, 0]
    for x in range(len(doc)):
        for startstr,endstr in [[f"Paper {paper}, Section I\n{question}",f"\nPaper "],[f"Paper {paper}, Section II\n{question}",f"\nPaper "]]:
            page = doc.load_page(x)
            text: str = page.get_text()
            starts = findall(text, startstr)
            if text.startswith(startstr.strip()):
                starts += [0]
            if starts:
                start = [starts[0], x]
            else:
                continue
            if text[start[0] + len(startstr)].isnumeric():
                continue
            ends = [ item for item in findall(text, endstr) if item>start[0]] + findall(text,f"Part {part}, {year}\nList of Questions") \
                   + findall(text,f"Part {part}, Paper")# [start, end]
            print(ends)
            if ends:
                end = [ends[0], x]
            else:
                end = [-1,x]#+-1*len(f"Part {part}, {year} List of Questions"),x]
            print(text[start[0]:end[0]])
            return [start, end]

    end = [-1, len(doc) - 1]
    return [start, end]


# cursed code, pymupdf cant parse text that includes "-\n" for some godforsaken reason
# didn't open an issue but pls do
# also probably will have a few lopsided qs if the - is the furthest thing on the right :)
def get_rects(start, end, page):
    text = page.get_text()[start:end]
    textbits = text.split("-\n")
    # print(textbits)
    rectdict = []
    for i, t2 in enumerate(textbits):
        # some sheets like vp, i hate this
        # t = t2.strip("Copyright © 2022 University of Cambridge. Not to be quoted or reproduced without permission.")
        if page.search_for(t2):
            rectdict += page.search_for(t2)
    # print(rectdict)
    return rectdict


def fetch_tripos_question(paperarr, paper, question,part,year, debug=False) -> None:
    filepath = fetch_paper_year(paperarr)
    doc = fitz.open(filepath)
    start, end = get_start_end(doc, paper,question, part,year)
    page = doc.load_page(start[1])
    rectdict = get_rects(start[0], end[0], page)
    # rectdict = page.search_for(text[start[0]:end[0]])
    for rectd in range(len(rectdict) - 1):
        rectdict[0].include_rect(rectdict[rectd + 1])
    delta = fitz.Point(8, 0)
    deltay = fitz.Point(0, 5)
    rectf = fitz.Rect(rectdict[0].tl - delta - deltay, rectdict[0].br + delta+deltay)
    if debug:
        return page.get_pixmap(clip=rectf, dpi=300).save("out.png")
    return page.get_pixmap(clip=rectf, dpi=300).tobytes()


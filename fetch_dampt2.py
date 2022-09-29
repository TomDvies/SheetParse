import string
import requests
from bs4 import BeautifulSoup


# after writing fetch_dampt.py i found this url
# http://www.damtp.cam.ac.uk/user/examples/codes.html
# it would be dumb to not use it and means you can drop the pandas dependancy
# urlscheme is http://www.damtp.cam.ac.uk/user/examples/{code}{letter}.pdf
# think letter may be non present in courses w/ 1 sheet
dampt_base_url = "http://www.damtp.cam.ac.uk/user/examples/"

# test if pdf for code exists, picks up too many files (vp notes for example) but thats fine as we only care about collecting the ones we want
# will break if they stop ordering via alphabet
def fetch_sheets_for_dampt_course(code, course):
    number = 0
    sheets = []
    for i, letr in enumerate(string.ascii_lowercase):
        if requests.head(f"http://www.damtp.cam.ac.uk/user/examples/{code}{letr}.pdf").status_code != 200:
            break
        sheets.append([f"http://www.damtp.cam.ac.uk/user/examples/{code}{letr}.pdf",course.strip(),i+1])
    return sheets




def fetch_dampt():
    # fetch table as pandas df
    codes_html =requests.get(f"{dampt_base_url}codes.html").content.decode()
    # print(codes_html)
    parsed_html = BeautifulSoup(codes_html, features="lxml")
    tables = parsed_html.find_all("table")
    courses = []
    sheets = []
    for table in tables[1::]:
        for i,obj in enumerate(table.find_all("tr")):
            if i==0:
                continue
            # no one should do these courses :)
            if obj.find_all("td")[0].contents[0] in ["A10","A11"]:
                continue
            sheets += fetch_sheets_for_dampt_course(obj.find_all("td")[0].contents[0],obj.find_all("td")[1].contents[0])
            # courses.append([x.contents[0] for x in obj.find_all("td")])
    # parsed_courses_list = parsed_html.find_all("div",{"class":"tex2jax"})[0]

    return sheets

if __name__ == "__main__":
    print(requests.head("http://www.damtp.cam.ac.uk/user/examples/B6d.pdf").status_code)
    print(fetch_dampt())
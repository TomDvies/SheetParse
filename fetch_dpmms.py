import requests
from bs4 import BeautifulSoup # w/ lxml
from urllib.parse import urljoin

# probably less resilient than dampt as pdfs in weird places

def fetch_dpmms_sheets_for_course(url:str, coursename:str):
    resp = requests.get(url)
    html = resp.content.decode()
    parsed_html = BeautifulSoup(html, features="lxml")
    parsed_main = parsed_html.find_all("div",{"id":"content-primary"})[0].find_all("ul")[0]
    sheets = []
    # assuming well ordered sheets pls be true
    for i, entry in enumerate(parsed_main.find_all("li")):
        try:
            if str(entry.a["href"]).startswith("http") or str(entry.a["href"]).startswith("https") or str(entry.a["href"]).startswith("www"):
                sheets.append([str(entry.a["href"]), coursename, i+1])
            else:
                sheets.append([urljoin(url,str(entry.a["href"])), coursename.strip(), i + 1])
        except:
            pass

    return sheets


def fetch_dpmms():
    url = "http://www.dpmms.cam.ac.uk/study"
    resp = requests.get(url)
    html = resp.content.decode()
    # print(dpmms_html)
    parsed_html = BeautifulSoup(html, features="lxml")
    courses = []
    sheets = []
    parsed_courses_list = parsed_html.find_all("div",{"class":"tex2jax"})[0].find_all("ul")[3::]
    for list in parsed_courses_list:
        for entry in list.find_all("li"):
            # filters weird courses like catam and VM
            if ("www.dpmms.cam.ac.uk/study/" in str(entry.a["href"])) and (str(entry.a.contents[0]) not in  ["Vectors and Matrices", "*Metric and Topological Spaces","*Analysis II"]):
                courses.append([str(entry.a["href"]), entry.a.contents[0]])
    # print(courses)
    # course = courses[0]
    for course in courses:
        sheets += fetch_dpmms_sheets_for_course(course[0],course[1])
    return sheets
# fetch_dpmms()



import requests
import pandas as pd # w/ lxml, html5lib
import roman
import re


# DEPRECATED, use fetch_dampt2.py instead


def placeholder1(arr, stri):
    for x in arr:
        if x in stri:
            return True
    return False

# would probably to be better to retain the pandas dataframe
def fetch_dampt():
    # fetch table as pandas df
    dampt_url = "http://www.damtp.cam.ac.uk/user/examples/"
    dampt_resp = requests.get(dampt_url)
    dampt_html = dampt_resp.content.decode()
    df_list = pd.read_html(dampt_html)
    # drop title headers which are in the table for some reason
    df = df_list[-1]
    df = df.drop(0)
    # move from df to list of lists & retain 2 cols, the code and the name 0, 1 respectively
    sheet_primitive_arr = list(zip(df[0], df[1]))
    sheets = []
    passes = ["study sheet", "old syllabus"]
    for i,file_tuple in enumerate(sheet_primitive_arr):
        if "sheet" in str(file_tuple[1]).lower() or "example" in str(file_tuple[1]).lower():
            if placeholder1(passes, str(file_tuple[1]).lower()):
                continue
            number = str(file_tuple[1]).lower().split("sheet")[-1].strip()
            if number == "":
                number = "1"
            # some are roman numeral
            elif not number.isdigit():
                try:
                    number = str(roman.fromRoman(number.upper()))
                except Exception as e:
                    print(e)
                    print(f"number: {number}")
                    number = "1"
            course = re.split("example sheet",str(file_tuple[1]).split(":")[0].split("sheet")[0],flags=re.IGNORECASE)[0].strip()
            course = re.split("Equations sheet", course,flags=re.IGNORECASE)[0].strip()
            sheets.append([f"http://www.damtp.cam.ac.uk/user/examples/{sheet_primitive_arr[i][0]}.pdf",course,int(number)])
    # i hate whoever did this
    sheets.append(["http://www.damtp.cam.ac.uk/user/examples/B6a.pdf", "Variational Principles",1])
    sheets.append(["http://www.damtp.cam.ac.uk/user/examples/B6b.pdf", "Variational Principles",2])
    return sheets

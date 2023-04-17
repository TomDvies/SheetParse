from fetch_sheet_question import fetch_sheet, fetch_sheet_question
from fetch_tripos_question import fetch_tripos_question
import json
from cmsfetch.fetch_dpmms import fetch_dpmms
from cmsfetch.fetch_dampt import fetch_dampt
from cmsfetch.fetch_papers import fetch_papers
#notes
# can match dampt by code, add extra command



sheets = fetch_dampt()
sheets += fetch_dpmms()
papers = fetch_papers()
courses =[]
for x in sheets:
    if x[1] not in courses:
        courses.append(x[1])
courses.sort()
# print(courses)
# exit()
# print(sheets)
with open("jsons/shortcutsdata.json", "r") as f:
    shortcuts = (json.loads(f.read()))
with open("jsons/formatsdata.json", "r") as f:
    formats = (json.loads(f.read()))


def parse_tripos_input(stin):
    course = year = paper = section = question = None
    components = [x for x in stin.upper().split(" ") if x != ""]
    if "IA" in components:
        course = "IA"
        components.remove("IA")
    elif "1A" in components:
        course = "IA"
        components.remove("1A")
    elif "IB" in components:
        course = "IB"
        components.remove("IB")
    elif "1B" in components:
        course = "IB"
        components.remove("1B")
    elif "II" in components:
        course = "II"
        components.remove("II")
    else:
        course = "IB"
    if "II" in components:
        section = "II"
        components.remove("II")
    elif "I" in components:
        section = "I"
        components.remove("I")
    year = components[0]
    if len(year) == 2:
        year = "20" + year
    paper = components[1]
    question = components[2]
    return course, year, paper, section, question


def get_tripos_image(searchstr):
    course, year, paper, section, question = parse_tripos_input(searchstr)
    # print(sheets)
    # for y in sheets:
    #     print(y[2], num)
    #     if str(y[2]) == str(num):
    #         print(1)
    papersoptions = [paperarr for paperarr in papers if paperarr[1]==year and paperarr[2]==course and paperarr[3]=="All questions"]
    if papersoptions:
        paperarr = papersoptions[0]
    print(paperarr, paper, question, course,year)
    img = fetch_tripos_question(paperarr, paper, question, course,year)
    return img, year, course,question






# format: course sheetnum questionnum
def get_sheet_image(searchstr):
    splits = searchstr.split(" ")
    ex = ""
    course = " ".join(splits[0:-2])
    for shortcut, longname in shortcuts:
        if course.lower() == shortcut.lower():
            course=longname
    # for exception, code, sol in formats:
    #     if exception.lower() in course.lower():
    #         ex = code
    #         print("exception",ex)
    sheet = splits[-2]
    num = splits[-1]
    print()
    if num.startswith("q"):
        num = num[1::]
    num = int(num)
    # print(sheets)
    # for y in sheets:
    #     print(y[2], num)
    #     if str(y[2]) == str(num):
    #         print(1)
    sheetsavailable = [y for y in [x for x in sheets if str(x[2]) == str(sheet)] if course.lower() == y[1].lower()]
    if not sheetsavailable:
        sheetsavailable = [y for y in [x for x in sheets if str(x[2]) == str(sheet)] if course.lower() in y[1].lower()]
    sheetl = sheetsavailable[0]
    img = fetch_sheet_question(fetch_sheet(sheetl), int(num), course, formats)
    formalcourse = sheetl[1]
    return img, formalcourse, num, sheet

# get_image("opti 1 11")
# exit()
def add_shortcut(string):
    fullname = string.split('"')[-2]
    shortname = string.split('"')[1]
    for i,x in enumerate(shortcuts):
        if x[0]==shortname:
            shortcuts[i][1] = fullname
            with open("jsons/shortcutsdata.json", "w") as f:
                json_data = json.dumps(shortcuts)
                f.write(json_data)
                return
    shortcuts.append([shortname,fullname])
    json_data = json.dumps(shortcuts)
    with open("jsons/shortcutsdata.json", "w") as f:
        f.write(json_data)

# like 90% sure this is bad for running smth every hour, and hogs a thread for way too much time, but it works
# https://gist.github.com/allanfreitas/e2cd0ff49bbf7ddf1d85a3962d577dbf
import time, traceback

exits=0
def every(delay, task):
  next_time = time.time() + delay
  while True:
    time.sleep(max(0, next_time - time.time()))
    try:
      task()
    except Exception:
      traceback.print_exc()
      # in production code you might want to have this instead of course:
      # logger.exception("Problem while executing repetitive task.")
    # skip tasks if we are behind schedule:
    next_time += (time.time() - next_time) // delay * delay + delay

def foo():
    global sheets
    print("fetching sheets")
    sheets2 = fetch_dampt()
    sheets2 += fetch_dpmms()
    sheets = sheets2

import threading
task  = threading.Thread(target=lambda: every(60*60, foo))
task.start()


# try:
#     loop.run_until_complete(task)
# except asyncio.CancelledError:
#     pass

import discord
import sys
import signal
import io
# this means systemd doesn't cry about it timing out
def handler(signum, frame):
    print('Got SIGTERM!')
    sys.exit(0)  # raises a SystemExit exception


# Register a handler (function) for the SIGTERM signal
signal.signal(signal.SIGTERM, handler)
# signal.signal(signal.SIGSTOP,handler)



client = discord.Client(intents=discord.Intents.all())

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(discord.__version__)
    print('------')
    print('Servers connected to:')
    for guild in client.guilds:
        print(guild.name)


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("?h"):
        embed = discord.Embed(title="Help:",
                              # description="Format requests as '?q IA 2011 2 II 12F'",
                              color=0x00ff00)
        embed.add_field(name="?q:", value=str("coursename, sheetnum, questionnum"))
        embed.add_field(name="?tq:", value=str("IA/IB/II (defaults to IB) year, paper, question"))
        await message.channel.send(embed=embed)
        return
    if message.content.startswith("?s"):
        try:
            string = message.content.split("?s ")[1]
            add_shortcut(string)
            fullname = string.split('"')[-2]
            shortname = string.split('"')[1]
            embed = discord.Embed(  # description="Format requests as '?q IA 2011 2 II 12F'",
                                  color=0x00ff00)
            embed.add_field(name="Added shortcut", value=str(f"{shortname} -> {fullname}"))
            await message.channel.send(embed=embed)
            return
        except Exception as e:
            print(e)
        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name="Something went wrong.", value=str("Format requests as '?q coursename sheetnum questionnum'"))
        await message.channel.send(embed=embed)
        return
    if message.content.startswith("?l"):
        try:
            if message.content.split("?l")[1].strip():
                if message.content.split("?l")[1].strip() not in courses+[x[0] for x in shortcuts]:
                    embed = discord.Embed(color=0x00ff00)
                    embed.add_field(name="Course not found", value=str("Format requests as '?l (coursename)'"))
                    await message.channel.send(embed=embed)
                    return
                embed = discord.Embed(  # description="Format requests as '?q IA 2011 2 II 12F'",
                    color=0x00ff00)
                strs=""
                for short, long in shortcuts:
                    print(short.lower())
                    if message.content.split("?l")[1].strip().lower() in [long.lower(),short.lower()]:
                        strs+=f"{short} -> {long}\n"
                strs = strs.strip()
                if not strs:
                    strs = "No shortcuts set yet."
                print(strs)
                embed.add_field(name=f"Shortcuts for {message.content.split('?l')[1].strip()}",value=strs)
                await message.channel.send(embed=embed)
                return
            else:
                secs =[]
                stsr=""
                n=1024
                for course in courses:
                    if len(stsr)+len(", ")+len(course) >= n:
                        secs.append(stsr.strip(", "))
                        stsr=""
                    else:
                        stsr+=f", {course}"
                if stsr:
                    secs.append(stsr.strip(", "))
                for i,section in enumerate(secs):
                    # enumerate
                    embed = discord.Embed(                          # description="Format requests as '?q IA 2011 2 II 12F'",
                                          color=0x00ff00)
                    embed.add_field(name=f"Courses ({i+1}/{len(secs)}):",value=section)
                    await message.channel.send(embed=embed)
                return
        except Exception as e:
            print(e)
        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name="Something went wrong.", value=str("Format requests as '?l (coursename)'"))
        await message.channel.send(embed=embed)
        return
    if message.content.startswith('?q'):
        try:
            image,name,num, sheetnum = get_sheet_image(message.content.split("?q ")[1])
            embed = discord.Embed(title=f"{name}, sheet {sheetnum}, q{num}",
                                  # description="Format requests as '?q IA 2011 2 II 12F'",
                                  color=0x00ff00)
            file = discord.File(fp=io.BytesIO(image), filename='SPOILER_.png')
            embed.set_image(url="attachment://SPOILER_.png")
            await message.channel.send(file=file, embed=embed)
            return
        except Exception as e:
            print(e)
        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name="Something went wrong.", value=str("Format requests as '?q coursename sheetnum questionnum'"))
        await message.channel.send(embed=embed)
        return
    if message.content.startswith('?tq'):
        try:
            image,year, course,question = get_tripos_image(message.content.split("?tq ")[1])
            embed = discord.Embed(title=f"{course}, {year}, q{question}",
                                  # description="Format requests as '?q IA 2011 2 II 12F'",
                                  color=0x00ff00)
            file = discord.File(fp=io.BytesIO(image), filename='SPOILER_.png')
            embed.set_image(url="attachment://SPOILER_.png")
            await message.channel.send(file=file, embed=embed)
            return
        except Exception as e:
            print(e)
        embed = discord.Embed(color=0x00ff00)
        embed.add_field(name="Something went wrong.", value=str("Format requests as '?q IA/IB/II (defaults to IB) year paper question'"))
        await message.channel.send(embed=embed)
        return

with open("token.txt", "r") as f:
    token = f.read()
client.run(token)

# if __name__ == "__main__":
#     get_image("Vectors and Matrices 1 2")
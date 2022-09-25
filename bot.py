# import discord
from fetch_dpmms import fetch_dpmms
from fetch_dampt import fetch_dampt
from fetch_question import fetch_sheet, fetch_question
import json
#notes
# can match dampt by code, add extra command



sheets = fetch_dampt()
sheets += fetch_dpmms()
# print(sheets)
with open("aliasdata.json", "r") as f:
    alias_data = (json.loads(f.read()))



# format: course sheetnum questionnum
def get_image(searchstr):
    splits = searchstr.split(" ")
    ex = ""
    course = " ".join(splits[0:-2])
    for shortcut, longname in alias_data["shortcuts"]:
        if course.lower() == shortcut.lower():
            course=longname
    for exception, code, sol in alias_data["exceptions"]:
        if exception.lower() in course.lower():
            ex = code
            print("exception",ex)
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
    sheetsavailable = [y for y in [x for x in sheets if str(x[2]) == str(sheet)] if course.lower() in y[1].lower()]
    sheet = sheetsavailable[0]
    img = fetch_question(fetch_sheet(sheet), int(num), ex, alias_data)
    return img

get_image("grm 4 5")

def add_shortcut(string):
    fullname = string.split('"')[-2]
    shortname = string.split('"')[1]
    alias_data["shortcuts"].append([shortname,fullname])
    json_data = json.dumps(alias_data)
    with open("aliasdata.json", "w") as f:
        f.write(json_data)



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
        embed.add_field(name="?q:", value=str("help yourself"))
        await message.channel.send(embed=embed)
        return
    if message.content.startswith("?s"):
        try:
            string = message.content.split("?s ")[1]
            add_shortcut(string)
            fullname = string.split('"')[-2]
            shortname = string.split('"')[1]
            embed = discord.Embed(title="Added shortcut:",
                                  # description="Format requests as '?q IA 2011 2 II 12F'",
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
    if message.content.startswith('?q'):
        try:
            if image:=get_image(message.content.split("?q ")[1]):
                embed = discord.Embed(title=message.content.split("?q ")[1],
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

with open("token.txt", "r") as f:
    token = f.read()
client.run(token)

# if __name__ == "__main__":
#     get_image("Vectors and Matrices 1 2")
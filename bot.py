import discord
from discord.ext import commands
import datetime
import json
import base64
import os
import aiohttp
import subprocess
import sys

# TODO:
#   - Reddit integration
#   - Minigames

TOKEN = "NTkzOTgzMjA0NzY0MDI0ODMy.XRV1jw.fGvmnYoIpIwDObFFaStPi3wBuLA"

prefix = "rito "
adminIDs = ["Flaming_Dorito#0001"]
blacklistRoastCommandGuildIDs = ["547155755308941312"]
images = {
    "bye": "https://res.cloudinary.com/teepublic/image/private/s--b4YQ-RHz--/t_Preview/b_rgb:6e2229,c_limit,f_jpg,h_630,q_90,w_630/v1516782493/production/designs/2304606_0.jpg"
}

bot = commands.Bot(command_prefix=prefix, case_insensitive=True)
bot.remove_command("help")


def embed_mc_server_data(data, emb, serverName):
    keys = data.keys()
    if data['online']:
        emb.add_field(name="Online", value=data['online'], inline=True)
        emb.add_field(name="IP:Port", value=f"{data['ip']}:{data['port']}", inline=True)
        emb.add_field(name="MOTD", value=f"{data['motd']['clean'][0]}\n{data['motd']['clean'][1]}", inline=False)
        if 'players' in keys:
            emb.add_field(name="Player Count", value=f"{data['players']['online']}/{data['players']['max']}", inline=False)
            if 'list' in data['players'].keys():
                val = f"{', '.join(data['players']['list'])}"
                if len(val) > 1024:
                    val = val[:950] + "... [No more names can fit in this embed field]"
                emb.add_field(name="Online Player List", value=val, inline=False)
        if 'software' in keys and 'version' in keys:
            emb.add_field(name="Server version", value=f"{data['software']} {data['version']}", inline=False)
        if 'hostname' in keys:
            emb.add_field(name="Hostname", value=data['hostname'], inline=False)
        if 'map' in keys:
            emb.add_field(name="map", value=data['map'], inline=False)
        if 'plugins' in keys:
            val = ", ".join(data['plugins']['raw'])
            if len(val) > 1024:
                val = val[:950] + "... [No more plugins can fit in this embed field]"
            emb.add_field(name="Plugins", value=val, inline=False)
        if 'mods' in keys:
            val = ", ".join(data['mods']['raw'])
            if len(val) > 1024:
                val = val[:950] + "... [No more mods can fit in this embed field]"
            emb.add_field(name="Mods", value=val, inline=False)
        if 'info' in keys:
            infoString = ""
            for line in data['info']['clean']:
                infoString += line + "\n"
            if len(infoString) > 1024:
                infoString = infoString[:950] + "... [No more info can fit in this embed field]"
            emb.add_field(name="Info", value=infoString, inline=False)
        if 'icon' in keys:
            newImgTxt = data['icon']
            imgData = bytes(newImgTxt[22:], 'utf-8')
            g = open("icon.png", "wb")
            g.write(base64.decodebytes(imgData))
            g.close()

            f = discord.File("icon.png", filename="icon.png")
            emb.set_thumbnail(url="attachment://icon.png")
            emb.set_author(name=serverName, icon_url="attachment://icon.png")
    else:
        emb.add_field(name="Online", value=data['online'])
        f = None
    return f, emb


def embed_player_data(data, emb, playerName):
    if data['data']['online'] == 1:
        emb.add_field(name="Online", value="True", inline=True)
    else:
        emb.add_field(name="Online", value="False", inline=True)
    emb.add_field(name="Total Time Played", value=f"{round(data['data']['total_time_play']/60, 2)} hours", inline=True)
    last_played = str(datetime.datetime.utcfromtimestamp(data['data']['last_play']))
    emb.add_field(name="Last Played", value=last_played, inline=True)
    if 'license' in data['data'].keys():
        if data['data']['license'] == 1:
            emb.add_field(name="Licensed", value="True", inline=False)
        else:
            emb.add_field(name="Licensed", value="False", inline=True)
    emb.add_field(name="Player Name", value=data['data']['name'], inline=True)
    if data['data']['uuid'] is not False:
        emb.add_field(name="UUID", value=data['data']['uuid'], inline=True)
    return emb


@bot.event
async def on_ready():
    print("Baby-Dorito has been started!")


@bot.event
async def on_message(message):
    print(message.content)
    await bot.process_commands(message)


@bot.command()
async def ping(ctx, website=None):
    if website is None:
        emb = discord.Embed(title="Error: No server website entered", type="rich", description="Enter a website to ping.", color=0xff0000, timestamp=datetime.datetime.utcnow())
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)
    else:
        packetCount = 6
        emb = discord.Embed(title=f"Pinging {website}", type="rich", description=f"Pinging {packetCount} times now, please allow up to 3 seconds...", color=0x00ff00, timestamp=datetime.datetime.utcnow())
        emb.set_footer(text=f"Requested by {ctx.author}")
        msg = await ctx.send(embed=emb)

        if sys.platform == 'linux':
            result = subprocess.run(['ping', "-c", str(packetCount), website], stdout=subprocess.PIPE).stdout.decode('utf-8')
        if sys.platform == 'win32':
            result = subprocess.run(['ping', "-n", str(packetCount), website], stdout=subprocess.PIPE).stdout.decode('utf-8')
        if result == "":
            result = "Invalid/Unresponsive website."
        print(result)
        emb.add_field(name="Ping results:", value="```" + result + "```")
        await msg.edit(embed=emb)


@bot.command()
async def mcping(ctx, ip=None):
    if ip is None:
        emb = discord.Embed(title="Error: No server IP entered", type="rich", description="Enter a minecraft server IP to ping.", color=0xff0000, timestamp=datetime.datetime.utcnow())
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)
    else:
        url = "https://api.mcsrvstat.us/2/" + ip
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            dictData = await resp.json()
        emb = discord.Embed(title=f"Pinging {ip}...", type="rich", description="Here is all the available data:", color=0x00ff00, timestamp=datetime.datetime.utcnow())
        f, emb = embed_mc_server_data(dictData, emb, ip)
        if dictData['online']:
            await ctx.send(files=[f], embed=emb)
        else:
            await ctx.send(embed=emb)
        if os.path.exists("icon.png"):
            os.remove("icon.png")


@bot.command()
async def mcplayer(ctx, player=None):
    if player is None:
        emb = discord.Embed(title="Error: No player name entered", type="rich", description="Enter a minecraft player name to ping.", color=0xff0000, timestamp=datetime.datetime.utcnow())
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)
    else:
        url = "https://minecraft-statistic.net/api/player/info/" + player
        async with aiohttp.ClientSession() as session:
            resp = await session.get(url)
            dictData = await resp.json()
        if dictData['status'] == "ok":
            emb = discord.Embed(title=f"Loading {player}'s stats...", type="rich", description="Here is all the available data:", color=0x00ff00, timestamp=datetime.datetime.utcnow())
            emb = embed_player_data(dictData, emb, player)
        else:
            emb = discord.Embed(title=f"Error loading {player}'s stats...", type="rich", description=f"Error: {dictData['msg']}.", color=0xff0000, timestamp=datetime.datetime.utcnow())
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)


@bot.command()
async def roast(ctx, person=None):
    if str(ctx.author) in adminIDs and ctx.message.guild.id not in blacklistRoastCommandGuildIDs:
        if person is None:
            emb = discord.Embed(title=f"Error: No person entered", type="rich", description="Enter who you want to roast.", color=0xff0000, timestamp=datetime.datetime.utcnow())
            emb.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=emb)
        else:
            template = "You are as <adjective> as <article target=adj1> <adjective min=1 max=3 id=adj1> <amount> of <adjective min=1 max=3> <animal> <animal_part>"
            if person.lower() == "me":
                who = None
                url = "https://insult.mattbas.org/api/insult.json?template=" + template
            else:
                who = "abc"
                url = "https://insult.mattbas.org/api/insult.json?template=" + template + "&who=" + who
            async with aiohttp.ClientSession() as session:
                resp = await session.get(url)
                plainData = await resp.read()
                dictData = json.loads(plainData)
            if dictData['error']:
                emb = discord.Embed(title=f"Error: Error loading roast...", type="rich", description=f"Error: {dictData['error_message']}.", color=0xff0000, timestamp=datetime.datetime.utcnow())
            else:
                insult = dictData['insult']
                insult = insult.replace("abc", person)
                emb = discord.Embed(title="Owww Roasted!!", type="rich", description=insult, color=0x00ff00, timestamp=datetime.datetime.utcnow())
            emb.set_footer(text=f"Requested by {ctx.author}")
            await ctx.send(embed=emb)


@bot.command()
async def stop(ctx):
    if str(ctx.author) in adminIDs:
        emb = discord.Embed(title="Stopping Baby-Dorito", type="rich", description="Baby-Dorito is stopping.", color=0x00ff00, timestamp=datetime.datetime.utcnow())
        emb.set_thumbnail(url=images["bye"])
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)
        await bot.logout()
    else:
        emb = discord.Embed(title="Error: Not authorised", type="rich", description="You are not authorised to use this command.", color=0xff0000, timestamp=datetime.datetime.utcnow())
        emb.set_footer(text=f"Requested by {ctx.author}")
        await ctx.send(embed=emb)


@bot.command()
async def help(ctx):
    emb = discord.Embed(title="Baby-Dorito Help Menu", type="rich", description="Hey there! I'm Baby-Dorito and here is how you can use me.\nSome commands may not be completely functional at the time since the bot is still under development.", color=0x00ff00, timestamp=datetime.datetime.utcnow())
    emb.add_field(name="PREFIX:", value=prefix, inline=False)
    emb.add_field(name="Help", value="Display this menu.", inline=False)
    emb.add_field(name="Stop", value="Stop Baby-Dorito :(.", inline=False)
    emb.add_field(name="Roast [person]", value="Roast somebody.", inline=False)
    emb.add_field(name="Ping [website/ip]", value="Ping any website or IP address.")
    emb.add_field(name="MCPing [ip]", value="Get information about a minecraft server. (Port will be found automatically", inline=False)
    emb.add_field(name="MCPlayer [ign]", value="Get information about a minecraft player.", inline=False)
    emb.add_field(name="Coming SOON:", value="Reddit integration, minigames and more!", inline=False)
    emb.add_field(name="Source", value="[Github link](https://github.com/Flaming-Dorito/Baby-Dorito)", inline=False)
    emb.add_field(name="Suggestions please", value="Have a suggesion for the bot. Anything at all? Contact Flaming_Dorito#0001 pls.")
    emb.set_footer(text=f"Requested by {ctx.author}")
    await ctx.send(embed=emb)

bot.run(TOKEN)

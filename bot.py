import discord
from discord.ext import commands
import json


with open("token.json", 'r') as f:
    data = json.load(f)
TOKEN = data['token']
prefix = "d."
extensions = ['cogs.mainCog', 'cogs.ownerCog', 'cogs.listenerCog']

bot = commands.Bot(command_prefix=prefix, owner_ids={"205333110731046913"})
bot.remove_command("help")

if __name__ == '__main__':
    for ext in extensions:
        bot.load_extension(ext)


@bot.event
async def on_ready():
    print(f'\n\nLogged in as: {bot.user.name} - {bot.user.id}\nVersion: {discord.__version__}\n')
    print(f'Successfully logged in and booted...!')

bot.run(TOKEN, reconnect=True)

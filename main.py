import os
from time import sleep
import datetime
import requests
import json
import discord
from discord.ext import commands
from discord.ext import tasks
from server import keep_alive

my_secret = os.environ['TOKEN']
CHANNEL_ID = os.environ['CHANNEL']  #チャンネルID

discord_intents = discord.Intents.all()
discord_intents.typing = False
discord_intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=discord_intents)
# p1: {regular|bankara-challenge|bankara-open|fest|coop-grouping-regular}
# p2: {now|next|schedule}


@bot.event
# Botの準備完了時に呼び出されるイベント
async def on_ready():
  print('We have logged in as {0}'.format(bot.user))


@bot.command()
async def salmon(ctx):
  apiurl = 'https://spla3.yuu26.com/api/coop-grouping-regular/schedule/'
  r = requests.get(apiurl)
  result = r.json()["results"]

  print(
    result[0]["stage"]["name"],
    result[0]["weapons"][0]["name"],
    result[0]["weapons"][1]["name"],
    result[0]["weapons"][2]["name"],
    result[0]["weapons"][3]["name"],
  )
  #2022-11-02T17:00:00+09:00
  str_time_start = datetime.datetime.fromisoformat(
    result[0]["start_time"]).strftime('%y/%m/%d %H:%M:%S')
  str_time_end = datetime.datetime.fromisoformat(
    result[0]["end_time"]).strftime('%y/%m/%d %H:%M:%S')

  str_salmonrun_stage = result[0]["stage"]["name"]
  str_salmonrun_weapon_A = result[0]["weapons"][0]["name"]
  str_salmonrun_weapon_B = result[0]["weapons"][1]["name"]
  str_salmonrun_weapon_C = result[0]["weapons"][2]["name"]
  str_salmonrun_weapon_D = result[0]["weapons"][3]["name"]

  str_weapons = str_salmonrun_weapon_A + "," + str_salmonrun_weapon_B + "," + str_salmonrun_weapon_C + "," + str_salmonrun_weapon_D

  if ctx.author == bot.user:
    return

  await ctx.send('''\
```asciidoc
%s 〜 %s
[サーモンラン]
%s
%s
```\
        ''' % (str_time_start, str_time_end, str_salmonrun_stage, str_weapons))


@tasks.loop(seconds=60)
async def loop():
  t_delta = datetime.timedelta(hours=9)
  JST = datetime.timezone(t_delta, 'JST')
  now = datetime.datetime.now(JST).strftime('%H:%M')
  #print(now)
  if now == '00:00' or now == '12:00':
    await bot.wait_until_ready()
    channel = bot.get_channel(int(CHANNEL_ID))
    apiurl = 'https://spla3.yuu26.com/api/coop-grouping-regular/schedule/'
    r = requests.get(apiurl)
    result = r.json()["results"]

    print(
      result[0]["stage"]["name"],
      result[0]["weapons"][0]["name"],
      result[0]["weapons"][1]["name"],
      result[0]["weapons"][2]["name"],
      result[0]["weapons"][3]["name"],
    )

    str_time_start = datetime.datetime.fromisoformat(
      result[0]["start_time"]).strftime('%y/%m/%d %H:%M:%S')
    str_time_end = datetime.datetime.fromisoformat(
      result[0]["end_time"]).strftime('%y/%m/%d %H:%M:%S')

    str_salmonrun_stage = result[0]["stage"]["name"]
    str_salmonrun_weapon_A = result[0]["weapons"][0]["name"]
    str_salmonrun_weapon_B = result[0]["weapons"][1]["name"]
    str_salmonrun_weapon_C = result[0]["weapons"][2]["name"]
    str_salmonrun_weapon_D = result[0]["weapons"][3]["name"]

    str_weapons = str_salmonrun_weapon_A + "," + str_salmonrun_weapon_B + "," + str_salmonrun_weapon_C + "," + str_salmonrun_weapon_D

    await channel.send('''\
```asciidoc
%s 〜 %s
[サーモンラン]
%s
%s
```\
        ''' % (str_time_start, str_time_end, str_salmonrun_stage, str_weapons))


@bot.listen()
async def on_ready():
  loop.start()  # important to start the loop


keep_alive()
try:
  bot.run(my_secret)
except discord.errors.HTTPException:
  print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
  os.system("python restarter.py")
  os.system('kill 1')

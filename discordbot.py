# discord.pyの大事な部分をimport
from discord.ext import commands
import discord
import os
import asyncio
from dotenv import load_dotenv
import openai
from history import History


load_dotenv()

# デプロイ先の環境変数にトークンをおいてね
APITOKEN = os.environ["DISCORD_BOT_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]

# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


channels = [985409309246644254, 1081461365694267453, 1082634484253466674]


history = {channel: History(channel) for channel in channels}


def completion(history):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )


@bot.command()
async def reboot(ctx):
    await history[ctx.channel.id].reset()

"""
@bot.event
# botの起動が完了したとき
async def on_ready():
    for channelID in channels:
        channel = bot.get_channel(channelID)
        await channel.send("起動したよ！")
"""


@bot.event
async def on_message(message):
    if not message.author.bot and message.content[:2] != "//" and message.content[0] != "!":
        channelID = message.channel.id

        print(channelID, message.content)
        if channelID in channels:
            history[channelID].history.append(
                {"role": "user", "content": message.content})
            result = completion(history[channelID].history)
            history[channelID].history.append(result["choices"][0]["message"])
            await message.channel.send(result["choices"][0]["message"]["content"])
    await bot.process_commands(message)


async def main():
    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())

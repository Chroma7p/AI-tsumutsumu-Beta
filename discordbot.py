# discord.pyの大事な部分をimport
from discord.ext import commands
import discord
import os
import asyncio
from dotenv import load_dotenv
import openai
from channel import Channel


load_dotenv()

# デプロイ先の環境変数にトークンをおいてね
APITOKEN = os.environ["DISCORD_BOT_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]

# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


channels = {channel: Channel(channel) for channel in [
    985409309246644254, 1081461365694267453, 1082634484253466674]}


def completion(history):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )


@bot.command()
async def reboot(ctx):
    await channels[ctx.channel.id].reset()

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
    channelID = message.channel.id
    # チャンネルIDが該当しない場合の排除
    if channelID not in channels:
        return
    # メッセージ主がボットなら排除
    if message.author.bot:
        return
    # コマンドや二重スラッシュは無視
    if message.content[:2] == "//" and message.content[0] == "!":
        return
    channels[channelID].history.append(
        {"role": "user", "content": message.content})
    try:
        result = completion(channels[channelID].history)
        channels[channelID].history.append(
            result["choices"][0]["message"])
        await message.channel.send(result["choices"][0]["message"]["content"])
    except openai.error.InvalidRequestError:
        channels[channelID].reset()
        await message.channel.send("情報の取得に失敗したみたい\n会話ログを削除するからもう一回試してみてね")

    await bot.process_commands(message)


async def main():
    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())

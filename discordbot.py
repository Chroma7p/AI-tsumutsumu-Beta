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


def is_question(message):
    # チャンネルIDが該当しない場合の排除
    if message.channel.id not in channels:
        return False
    # メッセージ主がボットなら排除
    if message.author.bot:
        return False
    # コマンドや二重スラッシュは無視
    if message.content[:2] == "//" and message.content[0] == "!":
        return False
    return True


@bot.command()
async def reboot(ctx):
    channels[ctx.channel.id].reset()
    await ctx.send("リセットしたよ！")

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
    if is_question(message):
        print(message.channel.id, message.author, message.content)
        channel = channels[message.channel.id]
        try:
            reply = channel.send(message.content)
            await message.channel.send(reply)
        # APIの応答エラーを拾う
        except openai.error.InvalidRequestError:
            channel.reset()
            await message.channel.send("情報の取得に失敗したみたい\n会話ログを削除するからもう一回試してみてね")
    # コマンド側にメッセージを渡して終了
    await bot.process_commands(message)


async def main():
    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())

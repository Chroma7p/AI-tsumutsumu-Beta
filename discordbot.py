# discord.pyの大事な部分をimport
from discord.ext import commands
import discord
import os
import asyncio

# デプロイ先の環境変数にトークンをおいてね
APITOKEN = os.environ["DISCORD_BOT_TOKEN"]
# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(command_prefix="!",intents=discord.Intents.all())

async def cog_setup(cogs):
    for c in cogs:
        await c.setup()


# コマンドを設定
@bot.command()
# "!hello"と送信された時
async def hello(ctx):
    await ctx.send("hello!")  # 送信された場所に"hello!"と送り返す


# イベントを検知
@bot.event
# botの起動が完了したとき
async def on_ready():
    print("Hello!")  # コマンドラインにHello!と出力


# メッセージ編集時に発動(編集前(before)と後(after)のメッセージを送信)
@bot.event
async def on_message_edit(before, after):
    txt = f"{before.author} がメッセージを編集しました！\nbefore:```{before.content}```\nafter:```{after.content}```"
    await after.add_reaction()
    await before.channel.send(txt)


# メッセージ削除時に発動(削除されたメッセージを送信)
@bot.event
async def on_message_delete(message):
    txt = f"{message.channel}:{message.author} がメッセージを削除しました！\n```{message.content}```"
    await message.author.send(txt)
    await message.channel.send(txt)

@bot.event
async def on_typing(channel,user,when):
    txt=f"{user} がメッセージを入力しています！"
    await channel.send(txt)


async def main():
    # do other async things
    # コグのフォルダ
    cogfolder = "cogs."
    # そして使用するコグの列挙(拡張子無しのファイル名)
    cogs = ["sample_cog"]

    for c in cogs:
        await bot.load_extension(cogfolder + c)

    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())


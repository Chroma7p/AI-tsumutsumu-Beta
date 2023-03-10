# discord.pyの大事な部分をimport
from discord.ext import commands
import discord
import os
import asyncio
from dotenv import load_dotenv
import openai
from channel import Channel, Mode
import io
import aiohttp
import MeCab

load_dotenv()
m = MeCab.tagger()

# デプロイ先の環境変数にトークンをおいてね
APITOKEN = os.environ["DISCORD_BOT_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]

# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(
    command_prefix="!",
    intents=discord.Intents.all(),
    # activity=discord.Activity(name="準備中")
)


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
    if message.content[:2] == "//" or message.content[0] == "!":
        return False
    return True


@bot.command()
async def reboot(ctx):
    channels[ctx.channel.id].reset()
    await ctx.send("リセットしたよ！")


@bot.command()
async def token(ctx):
    channel = channels[ctx.channel.id]
    await ctx.send(f"現在の利用しているトークンの数は{channel.get_now_token()}だよ！\n{channel.TOKEN_LIMIT}に達すると古いログから削除されていくよ！")


@bot.command()
async def talk_history(ctx):
    channel = channels[ctx.channel.id]
    text = ""
    for msg in channel.history:
        c = msg.content[:10].replace('\n', '')
        text += f"{msg.token}:{c}{'...' if len(msg.content)>10 else ''}\n"
    await ctx.send(text)


@bot.command()
async def generate(ctx, *, arg):
    if arg == "":
        await ctx.send("`!generate rainbow cat`のように、コマンドの後ろに文字列を入れてね！")
    else:
        try:
            response = openai.Image.create(
                prompt=arg,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as resp:
                    if resp.status != 200:
                        return await ctx.send('画像のロードに失敗しちゃった!')
                    data = io.BytesIO(await resp.read())
                    await ctx.send(file=discord.File(data, arg.replace(" ", "_") + ".png"))
        except Exception:
            await ctx.send("何かわかんないけど失敗しちゃった！")
            await ctx.send("`!generate rainbow cat`のように、コマンドの後ろに文字列を入れてね！")


@bot.command()
async def normal(ctx):
    channel = channels[ctx.channel.id]
    if channel.mode == Mode.chatgpt:
        return await ctx.send("既に現在ChatGPTモードです")
    else:
        channel.mode = Mode.chatgpt
        channel.reset()
        return await ctx.send("ChatGPTモードに変更しました")


@bot.command()
async def tsumugi(ctx):
    channel = channels[ctx.channel.id]
    if channel.mode == Mode.tsumugi:
        return await ctx.send("もうつむつむモードだよ")
    else:
        channel.mode = Mode.tsumugi
        channel.reset()
        return await ctx.send("つむつむモードに変更したよ")


@bot.command()
async def mecab(ctx, *, arg):
    ctx.send(m.parse(arg))


"""
@bot.event
# botの起動が完了したとき
async def on_ready():
    activity = discord.Activity(name='準備完了！')
    await bot.change_presence(activity=activity)
"""


@bot.event
async def on_message(message):
    if is_question(message):
        async with message.channel.typing():
            channel = channels[message.channel.id]
            try:
                reply = channel.send(message.content)
            # APIの応答エラーを拾う
            except openai.error.InvalidRequestError:
                channel.reset()
                reply = "情報の取得に失敗したみたい\n会話ログを削除するからもう一回試してみてね"
            except Exception as e:
                reply = f"err:{e}"
            finally:
                for i in range(len(reply) // 1500 + 1):
                    await message.channel.send(reply[i * 1500:(i + 1) * 1500])
    # コマンド側にメッセージを渡して終了
    await bot.process_commands(message)


async def main():
    # start the client
    async with bot:
        await bot.start(APITOKEN)

asyncio.run(main())

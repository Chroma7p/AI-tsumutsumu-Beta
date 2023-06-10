# discord.pyの大事な部分をimport

import discord
from discord.ext import commands
import os
import asyncio
import openai
from channel import Channel, Mode
from discord import app_commands
from judging_puns import scoring
import MeCab
import random
from hashlib import sha1
import time
import struct

from dotenv import load_dotenv
load_dotenv(".env")
m = MeCab.Tagger()

# デプロイ先の環境変数にトークンをおいてね
API_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
openai.api_key = os.environ["OPENAI_API_KEY"]

# botのオブジェクトを作成(コマンドのトリガーを!に)
bot = commands.Bot(
    command_prefix="/",
    intents=discord.Intents.all(),
    application_id=os.environ["APPLICATION_ID"],
    # activity=discord.Game(name="XX") #"XXをプレイ中"にする

)

tree = bot.tree

rooms = os.environ["ROOM_ID"].split(",")

channels = {int(channel): Channel(int(channel)) for channel in rooms}


def is_question(message: discord.Message):
    # コマンドや二重スラッシュは無視
    if message.content[:2] == "//" or message.content[0] == "/":
        return False
    # チャンネルIDが該当しない場合の排除
    if message.channel.id not in channels:
        return False
    # 自分自身の排除
    if message.author.id == bot.user.id:
        return False
    # ボット許可
    if channels[message.channel.id].unconditional:
        return True
    # メッセージ主がボットなら排除
    if message.author.bot:
        return False

    return True


@tree.command(name="join", description="臨時でチャンネルに参加するよ、しばらくたつと反応しなくなるよ")
async def join(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.channel.id in channels:
        return await interaction.followup.send("既に参加しているよ")

    channels[interaction.channel.id] = Channel(
        interaction.channel.id, is_temporary=True)
    return await interaction.followup.send("こんちゃ！！")


@tree.command(name="bye", description="臨時で参加しているチャンネルから脱退するよ")
async def bye(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.channel.id not in channels:
        return await interaction.followup.send("いないよ……")
    if channels[interaction.channel.id].is_temporary:
        del channels[interaction.channel.id]
        return await interaction.followup.send("ばいばい！！")
    else:
        return await interaction.followup.send("何らかの理由で退場できないよ！")


@tree.command(name="reset", description="そのチャンネルの会話ログをリセットするよ")
async def reboot(interaction: discord.Interaction):
    channels[interaction.channel.id].reset()
    await interaction.response.send_message("リセットしたよ！")


@tree.command(name="token", description="現在のトークン消費状況を表示するよ")
async def token(interaction: discord.Interaction):
    channel = channels[interaction.channel.id]
    await interaction.response.send_message(f"現在の利用しているトークンの数は{channel.get_now_token()}だよ！\n{channel.TOKEN_LIMIT}に達すると古いログから削除されていくよ！")


@tree.command(name="history", description="現在残っている会話ログを表示するよ、結構出るよ")
async def talk_history(interaction: discord.Interaction):
    channel = channels[interaction.channel.id]
    text = ""
    if not channel.history:
        return await interaction.response.send_message("会話ログはまだないよ！")
    for msg in channel.history:
        c = msg.content[:20].replace('\n', '')
        text += f"{msg.token}:{c}{'...' if len(msg.content)>20 else ''}\n"

    await interaction.response.send_message(text)


@tree.command(name="generate", description="OpenAIのAPIにアクセスして画像を生成するよ")
@app_commands.describe(prompt="生成する画像を指定する文章を入力してね")
async def generate(interaction: discord.Interaction, prompt: str):
    print(f"prompt:'{prompt}'")
    if prompt == "":
        await interaction.response.send_message("`/generate rainbow cat`のように、コマンドの後ろに文字列を入れてね！")
    else:
        #  考え中にする 送信するときはinteraction.followupを使う
        await interaction.response.defer()
        try:
            response = openai.Image.create(
                prompt=prompt,
                n=1,
                size="512x512"
            )
            image_url = response['data'][0]['url']
            img: discord.Embed = discord.Embed(title=prompt, color=0xffffff)
            img.set_image(url=image_url)
            print(image_url)
            await interaction.followup.send(embed=img)
        except Exception:
            await interaction.followup.send("何かわかんないけど失敗しちゃった！\n/generate rainbow cat`のように、コマンドのうしろに文字列を入れてね！")


@tree.command(name="normal", description="通常のChatGPTモードに切り替えるよ 会話ログは消えるよ")
async def normal(interaction: discord.Interaction):
    await interaction.response.defer()
    channel = channels[interaction.channel.id]
    if channel.mode == Mode.chatgpt:
        return await interaction.followup.send("既に現在ChatGPTモードです")
    else:
        channel.mode = Mode.chatgpt
        channel.reset()
        return await interaction.followup.send("ChatGPTモードに変更しました")


@tree.command(name="tsumugi", description="つむつむモードに切り替えるよ 会話ログは消えるよ")
async def tsumugi(interaction: discord.Interaction):
    await interaction.response.defer()
    channel = channels[interaction.channel.id]
    if channel.mode == Mode.tsumugi:
        return await interaction.followup.send("もうつむつむモードだよ")
    else:
        channel.mode = Mode.tsumugi
        channel.reset()
        return await interaction.followup.send("つむつむモードに変更したよ")


@tree.command(name="mecab", description="mecabの導入が出来ているかのテストコマンドだよ 形態素解析できるよ")
async def mecab(interaction: discord.Interaction, arg: str):
    await interaction.response.send_message(m.parse(arg))
    # await interaction.response.send_message("工事中！ごめんね！")


@tree.command(name="test", description="スラッシュコマンドが機能しているかのテスト用コマンドだよ")
async def test(interaction: discord.Interaction):
    print("ちゃろ～☆")
    await interaction.response.send_message("ちゃろ～☆")


@tree.command(name="allow", description="botとの会話を許可するよ、ボット相手に無限に話す可能性があるから注意！")
async def allow(interaction: discord.Interaction):
    channel = channels[interaction.channel.id]
    if channel.unconditional:
        return await interaction.response.send_message("既に許可されているよ")
    else:
        channel.set_unconditional(True)
        return await interaction.response.send_message("会話対象を無条件にしたよ")


@tree.command(name="disallow", description="ボットとの会話の許可を取り消すよ")
async def disallow(interaction: discord.Interaction):
    channel = channels[interaction.channel.id]
    if channel.unconditional:
        channel.set_unconditional(False)
        return await interaction.response.send_message("会話対象の設定を元に戻したよ")
    else:

        return await interaction.response.send_message("元々許可されていないよ")


@tree.command(name="dajare", description="ダジャレモードを切り替えるよ(WIP)")
async def dajare(interaction: discord.Interaction):
    channel = channels[interaction.channel.id]
    if channel.dajare:
        channel.dajare = False
        return await interaction.response.send_message("ダジャレモードをオフにしたよ")
    else:
        channel.dajare = True
        return await interaction.response.send_message("ダジャレモードをオンにしたよ")


@tree.command(name="minesweeper", description="マインスイーパーを生成するよ")
async def minesweeper(interaction: discord.Interaction, x: int = 10, y: int = 10, bomb: int = 10):
    field = [[0 for _ in range(x)] for _ in range(y)]
    zenkaku = ["０", "１", "２", "３", "４", "５", "６", "７", "８", "９"]
    if bomb > x * y:
        return await interaction.response.send_message("爆弾の数が多すぎるよ")
    pair = [(i, j) for i in range(x) for j in range(y)]

    for i in random.sample(pair, k=bomb):
        field[i[1]][i[0]] = 9

    for i in range(x):
        for j in range(y):
            if field[j][i] == 9:
                continue
            for ii in range(max(0, i - 1), min(x, i + 2)):
                for jj in range(max(0, j - 1), min(y, j + 2)):
                    if field[jj][ii] == 9:
                        field[j][i] += 1

    text = ""
    for i in range(x):
        text += "# "
        for j in range(y):
            if field[j][i] == 9:
                text += "|| Ｘ || "
            else:
                text += f"|| {zenkaku[field[j][i]]} || "
        text += "\n"
    if len(text) > 1000:
        return await interaction.response.send_message("フィールドが大きすぎるよ")
    await interaction.response.send_message(text)


@bot.event
# botの起動が完了したとき
async def on_ready():
    print("hi bro")
    now_commands: list[discord.app_commands.Command] = tree.get_commands()
    for command in now_commands:
        print(command.name, command.description)
    try:
        await tree.sync()
    except Exception as e:
        print(e)
    print("-synced-")

errmsg = "err:The server had an error processing your request."


@bot.event
async def on_message(message: discord.Message):
    # print(channels, message.channel.id)
    channel = channels[message.channel.id]
    # print(channel, message.content)
    if not is_question(message):
        return await bot.process_commands(message)
    try:
        if channel.dajare:
            score, rep = scoring(message.content)
            if rep:
                channel.hiscore = max(channel.hiscore, score)
                rep += "\n現在のハイスコア:" + str(channel.hiscore)
                await message.channel.send(rep)
                return await bot.process_commands(message)

    except Exception as e:
        print(e)

    async with message.channel.typing():
        try:
            if channel.mode == Mode.tsumugi:
                timehash = sha1(struct.pack('<f', time.time())).hexdigest()
                content = f"{timehash}\n{message.author.name}:{message.content}\n{timehash}"

            reply = channel.send(content)
        # APIの応答エラーを拾う
        except openai.error.InvalidRequestError:
            channel.reset()
            reply = "情報の取得に失敗したみたい\n会話ログを削除するからもう一回試してみてね"
        except Exception as e:
            reply = f"err:{e}"
        finally:
            if reply[:4] == "err:":
                reply = f"なにかエラーが起こってるみたい、なんかいろいろ書いとくから、開発者に見せてみて\n```{reply}```"
            for i in range(len(reply) // 1500 + 1):
                await message.channel.send(reply[i * 1500:(i + 1) * 1500])
    # コマンド側にメッセージを渡して終了
    await bot.process_commands(message)


async def main():
    # start the client
    async with bot:
        try:
            await bot.start(API_TOKEN)
        except KeyboardInterrupt:
            await bot.close()
        except Exception as e:
            print(e)

asyncio.run(main())

from discord.ext import commands

# samplecogクラス
class SampleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Cogが読み込まれた時に発動
    @commands.Cog.listener()
    async def on_ready(self):
        print('SampleCog on ready!')

    # コマンドの記述
    @commands.command()
    async def chkcog(self, ctx):
        await ctx.send("using cog!")

    


# Cogとして使うのに必要なsetup関数
def setup(bot):
    return bot.add_cog(SampleCog(bot))

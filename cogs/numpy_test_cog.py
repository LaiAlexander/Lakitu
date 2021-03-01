from discord.ext import commands
import numpy as np

class NumpyTest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"{self.__class__.__name__} cog has been loaded\n-----", flush=True)

    @commands.command(name="numpytest")
    async def numpy_test(self, ctx):
        a = np.arange(15).reshape(3, 5)
        await ctx.send(str(a))

def setup(bot):
    bot.add_cog(NumpyTest(bot))

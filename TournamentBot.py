"""
MIT License

Copyright (c) 2018 Breee@github

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from config.Configuration import Configuration
from discord.ext import commands
import discord
import datetime
import aiohttp
import logging
import os
import challonge
import pprint
import requests
import shutil
import cairosvg



LOGGER = logging.getLogger('discord')
if os.path.isfile('help_msg.txt'):
    with open('help_msg.txt', 'r') as helpfile:
        HELP_MSG = helpfile.read()

class TournamentBot(commands.Bot):
    def __init__(self, prefix, description, config_file):
        super().__init__(command_prefix=prefix, description=description, pm_help=None, help_attrs=dict(hidden=True))
        self.config = Configuration(config_file)
        self.add_command(self.ping)
        self.add_command(self.uptime)
        self.remove_command("help")
        self.add_command(self.help)
        self.add_command(self.create)
        self.add_command(self.select)
        self.add_command(self.destroy)
        self.add_command(self.index)
        self.add_command(self.join)
        self.add_command(self.bracket)
        self.start_time = 0
        self.selected_tournament = ""
        self.session = aiohttp.ClientSession(loop=self.loop)
        #

    """
    ################ EVENTS ###############
    """

    async def on_ready(self):
        LOGGER.info("Bot is ready.")
        self.start_time = datetime.datetime.utcnow()
        await self.change_presence(game=discord.Game(name=self.config.playing))
        # Tell pychal about your [CHALLONGE! API credentials](http://api.challonge.com/v1).
        challonge.set_credentials(self.config.user_name, self.config.api_key)

    def run(self):
        super().run(self.config.token, reconnect=True)

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_resumed(self):
        print('resumed...')


    """
    ################ COMMANDS ###############
    """

    @commands.command(hidden=True)
    async def ping(self):
        await self.say("pong!")

    @commands.command(hidden=True)
    async def uptime(self):
        await self.say("Online for %s" % str(datetime.datetime.utcnow() - self.start_time))

    @commands.command(pass_context=True)
    async def help(self, ctx):
        msg = "Help:\n"\
               "%s\n"\
               "admin_roles: %s\n"\
               "manager_roles:%s" % (HELP_MSG, "".join(["<@&%s>" % x for x in self.config.admin_roles]), "".join(["<@&%s>" % x for x in self.config.manager_roles]))

        await self.say(msg)

    @commands.command(pass_context=True)
    async def create(self, ctx, name, type):
        url = "%s" % name.replace(" ", "_")
        tour = challonge.tournaments.create(name=name, url=url, tournament_type=type, subdomain=self.config.subdomain, open_signup=True)
        self.selected_tournament = ("%s-%s" % (self.config.subdomain, url))
        msg = "__**Created new tournament**__\n" \
              "**Name:** %s\n" \
              "**Selector:** %s\n" \
              "**URL:** <%s>\n" \
              "**ID:** %s\n" \
              "**Live Image URL:** <%s>\n" \
              "**SIGNUP URL:** <%s>\n" % (tour['name'],"%s-%s" % (self.config.subdomain, tour['url']), tour['full_challonge_url'], tour['id'], tour['live_image_url'], tour['sign_up_url'])
        await self.send_message(destination=ctx.message.channel,content=msg)

    @commands.command(pass_context=True)
    async def select(self,ctx, selector):
        try:
            challonge.tournaments.show(selector)
            self.selected_tournament = selector
        except requests.exceptions.HTTPError:
            await self.say("tournament does not exist")

    @commands.command(pass_context=True)
    async def destroy(self,ctx,url):
        challonge.tournaments.destroy("%s-%s" % (self.config.subdomain, url))
        await self.send_message(destination=ctx.message.channel,content="destroyed %s" % url)

    @commands.command(pass_context=True)
    async def index(self, ctx):
        index = challonge.tournaments.index(state="all", subdomain=self.config.subdomain)
        msg = "__**Tournaments:**__ \n"
        for tour in index:
            msg += "-----------------\n" \
                   "**Name:** %s\n" \
                   "**Selector:** %s\n" \
                   "**URL:** <%s>\n" \
                   "**ID:** %s\n" \
                   "**Live Image URL:** <%s>\n" \
                   "**SIGNUP URL:** <%s>\n" \
                   "-----------------\n" % (tour['name'],"%s-%s" % (self.config.subdomain, tour['url']), tour['full_challonge_url'], tour['id'], tour['live_image_url'], tour['sign_up_url'])

        await self.send_message(destination=ctx.message.channel, content=msg)

    @commands.command(pass_context=True)
    async def join(self,ctx, name=None):
        if not self.selected_tournament:
            await self.say("ERROR: No tournament selected")
            return
        if name:
            user = await self.get_user_info(name.replace("<@", "").replace(">", ""))
            try:
                challonge.participants.create(tournament=self.selected_tournament, name=user.display_name)
            except challonge.ChallongeException as ex:
                await self.say("%s - %s." % (user.mention, ex))
                return
            await self.say("Added %s to tournament %s" % (user.mention, self.selected_tournament))

    @commands.command(pass_context=True)
    async def bracket(self, ctx):
        await self.send_message(ctx.message.channel, "Preparing bracket, this might take a few seconds!")
        tour = challonge.tournaments.show(self.selected_tournament)
        r = requests.get(tour['live_image_url'], stream=True)
        if r.status_code == 200:
            with open("%s.svg" % tour['name'], 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            cairosvg.svg2png(url="%s.svg" % tour['name'], write_to="%s.png" % tour['name'])
        await self.send_file(ctx.message.channel, "%s.png" % tour['name'])

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

import logging
import json
from configparser import ConfigParser

logger = logging.getLogger('discord')

class Configuration(object):

    def __init__(self, config_file):
        self.token = ""
        self.playing = ""
        self.admin_roles = []
        self.manager_roles = []
        self.api_key = ""
        self.subdomain = ""
        self.user_name = ""
        self.read_config_file(config_file)

    def read_config_file(self, filename='config.ini.example'):
        """ Read configuration file and return a dictionary object
        :param filename: name of the configuration file
        :param section: section of database configuration
        :return: a dictionary of database parameters
        >>> c = Configuration(config_file='config.ini.example')
        >>> c.token
        '<bot_token>'
        >>> c.playing
        'u mom lel'
        >>> c.admin_roles
        ['role_id1', 'role_id2']
        >>> c.manager_roles
        ['role_id3', 'role_id4']
        >>> c.api_key
        'xyz'
        """
        # create parser and read ini configuration file
        parser = ConfigParser()
        parser.read(filename)

        # get section, default to mysql
        conf = {}
        if parser.has_section('bot'):
            items = parser.items('bot')
            for item in items:
                conf[item[0]] = item[1]
        else:
            raise Exception('{0} section not found in the {1} file'.format('bot', filename))

        if parser.has_section('discord'):
            items = parser.items('discord')
            for item in items:
                conf[item[0]] = item[1]
        else:
            raise Exception('{0} section not found in the {1} file'.format('discord', filename))

        if parser.has_section('challonge'):
            items = parser.items('challonge')
            for item in items:
                conf[item[0]] = item[1]
        else:
            raise Exception('{0} section not found in the {1} file'.format('challonge', filename))

        if 'token' in conf.keys():
            self.token = conf['token']
        else:
            raise Exception("No Bot Token specified, this is required")

        if 'playing' in conf.keys():
            self.playing = conf['playing']

        if 'admin_roles' in conf.keys():
            self.admin_roles = json.loads(conf['admin_roles'])
        else:
            raise Exception("No admin roles specified, this is required, you can find out the ID of a discord_role by typing \@ROLE")

        if 'manager_roles' in conf.keys():
            self.manager_roles = json.loads(conf['manager_roles'])
        else:
            logger.info("No manager_roles specified")

        if 'api_key' in conf.keys():
            self.api_key = conf['api_key']
        else:
            raise Exception("No challonge api_key specified, this is required, create one at https://challonge.com/settings/developer")

        if 'user_name' in conf.keys():
            self.user_name = conf['user_name']
        else:
            raise Exception("No challonge user_name specified, this is required.")

        if 'subdomain' in conf.keys():
            self.subdomain = conf['subdomain']


















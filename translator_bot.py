# Translator Bot for Telegram
# Copyright (C) 2017 Rodrigo Martínez <dev@brunneis.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import yaml
import sys
import ast
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from urllib.request import urlopen, Request
from urllib.parse import quote


class TranslatorBot(object):
    def __init__(self):
        logging.basicConfig(filename='translator_bot.log',
                            level=logging.INFO,
                            format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger()

        with open('./conf.yaml', 'r') as stream:
            try:
                conf = yaml.safe_load(stream)
            except yaml.YAMLError as e:
                logging.error(e, exc_info=True)
                sys.exit(1)

        # Token
        try:
            self.__dict__['token'] = conf['token']
        except KeyError:
            logging.error(e, exc_info=True)
            sys.exit(1)

        # Source language
        try:
            self.__dict__['source_lang'] = conf['source_lang']
        except KeyError:
            self.__dict__['source_lang'] = 'auto'

        # Target language
        try:
            self.__dict__['target_lang'] = conf['target_lang']
        except KeyError:
            self.__dict__['target_lang'] = 'en'

        # Start message
        try:
            self.__dict__['start_message'] = conf['start_message']
        except KeyError:
            self.__dict__['start_message'] = ''

    def get_translation(self, input_text):
        url = 'https://translate.googleapis.com/translate_a/single' \
            + '?client=gtx&sl=' + self.__dict__['source_lang'] + '&tl=' \
            + self.__dict__['target_lang'] + '&dt=t&q=' + quote(input_text)

        request = Request(
            url=url,
            data=None,
            headers={
                'user-agent': 'Mozilla/5.0 RUC/0.1 (Linux; en)',
                'accept-language': 'en-US,en;q=0.8,gl;q=0.6,es;q=0.4,pt;q=0.2',
                'accept': 'text/html,application/xhtml+xml,application/xml;'
                + 'q=0.9,image/webp,*/*;q=0.8',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'dnt': '1',
                'upgrade-insecure-requests': '1'
            }
        )

        response = urlopen(request).read().decode('utf-8').replace('null',
                                                                   'None')
        translations = ast.literal_eval(response)[0]

        result = ''
        for translation in translations:
            result += translation[0]

        return result

    def start_handler(self, bot, update):
        bot.send_message(chat_id=update.message.chat_id,
                         text=self.__dict__['start_message'])

    def translate_handler(self, bot, update):
        message_text = update.message.text[2:]
        logging.info(str(update.message.from_user.id)
                     + ':' + update.message.from_user.username + ":"
                     + message_text)
        translation = self.get_translation(message_text)
        bot.send_message(chat_id=update.message.chat_id, text=translation)

    def run(self):
        updater = Updater(token=self.__dict__['token'])
        dispatcher = updater.dispatcher

        start_handler = CommandHandler('start', self.start_handler)
        translate_handler = CommandHandler('t', self.translate_handler)

        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(translate_handler)

        updater.start_polling()


if __name__ == "__main__":
    app = TranslatorBot()
    app.run()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import urwid

class MessageSendWidget(urwid.Filler):
    def __init__(self, Telegram_ui):
        self.Telegram_ui = Telegram_ui
        self.updateLockedauto = False
        self.current_status = ('?', False)

        self.status_bar = urwid.Text(('status_bar', ' '), align='left')
        self.attr = urwid.AttrMap(self.status_bar, 'status_bar')

        self.widgetEdit = urwid.Edit(" >> ", "", multiline=False)

        self.pile = urwid.Pile([self.attr, self.widgetEdit])
        super().__init__(self.pile)

        self.update_send_widget()


    def update_send_widget(self):
        if 'when' in self.Telegram_ui.current_chan:
            self.current_status = (self.Telegram_ui.current_chan['when'], False)
        else:
            self.current_status = ('?', False)

        self.widgetEdit.set_edit_text('')
        self.update_status_bar()


    def update_status_bar(self):
        chan_name = self.Telegram_ui.current_chan['print_name'].replace('_', ' ')
        chan_type = self.Telegram_ui.current_chan['type']

        if chan_type == 'chat':
            chan_num = self.Telegram_ui.current_chan['members_num']
            text = ' [ ' + chan_name + " ] --- [ " + str(chan_num) + " members ]"
        else:
            text = ' [ ' + chan_name + ' ]'
            (when, status) = self.current_status

            if status:
                text = text + ' --- [ Online ]'
            elif when == '?':
                text = text + ' --- [ Offline ]'
            else:
                current_date = time.strftime('%d/%m/%Y', time.localtime(int(time.time())))
                pattern = '%Y-%m-%d %H:%M:%S'
                when_epoch = int(time.mktime(time.strptime(when, pattern)))
                when_date = time.strftime('%d/%m/%Y', time.localtime(when_epoch))
                when_hour = time.strftime('%H:%M', time.localtime(when_epoch))

                if when_date == current_date:
                    text = text + ' --- [ last seen at ' + when_hour + ' ]'
                else:
                    text = text + ' --- [ last seen ' + when_date + ' at ' + when_hour + ' ]'

        self.status_bar.set_text(text)


    def update_online(self, when, status):
        self.current_status = (when, status)
        self.update_status_bar()


    def autocomplete(self):
        while (self.updateLockedauto):
            time.sleep(0.5)
        self.updateLockedauto = True

        type_chan = self.Telegram_ui.current_chan['type']
        print_name_chan = self.Telegram_ui.current_chan['print_name']

        username_list = []

        # récupération des username possibles
        if type_chan == 'chat':
            chat_info = self.Telegram_ui.sender.chat_info(print_name_chan)
            for user in chat_info['members']:
                if 'username' in user:
                    username_list.append(user['username'])

        elif type_chan == 'user' and 'username' in self.Telegram_ui.current_chan:
            username_list = [self.Telegram_ui.current_chan['username']]

        elif type_chan == 'channel':
            channel_info = self.Telegram_ui.sender.channel_info(print_name_chan)
            for user in channel_info['members']:
                if 'username' in user:
                    username_list.append(user['username'])

        text = self.widgetEdit.get_edit_text()[1:]

        self.updateLockedauto = False

        # autocompletion avec le premier résultat
        for user in username_list:
            if user.startswith(text):
                to_complete = user[len(text):]
                self.widgetEdit.insert_text(to_complete + ' ')
                break


    def keypress(self, size, key):
        key = super(MessageSendWidget, self).keypress(size, key)

        if key == 'enter':
            msg = self.widgetEdit.get_edit_text()

            if msg == '/quit':
                self.Telegram_ui.exit()

            dst = self.Telegram_ui.current_chan['print_name']

            self.Telegram_ui.sender.send_msg(dst, msg)
            self.widgetEdit.set_edit_text("")

        # Autocompletion
        elif key == 'tab' and self.widgetEdit.get_edit_text().startswith("@") and \
                not ' ' in self.widgetEdit.get_edit_text():
            try:
                self.autocomplete()
            except:
                pass

        # Supprimer le texte courant
        elif key == 'ctrl w' or key == 'ctrl k':
            self.widgetEdit.set_edit_text("")

        # donner le focus à la liste
        elif key == 'up' or key == 'page up' or key == 'esc':
            self.Telegram_ui.right_side.focus_position = 0


# vim: ai ts=4 sw=4 et sts=4

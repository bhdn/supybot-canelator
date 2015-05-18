# -*- encoding: utf-8
###
# Copyright (c) 2012, Bogdano Arendartchuk
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#   * Redistributions of source code must retain the above copyright notice,
#     this list of conditions, and the following disclaimer.
#   * Redistributions in binary form must reproduce the above copyright notice,
#     this list of conditions, and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#   * Neither the name of the author of this software nor the name of
#     contributors to this software may be used to endorse or promote products
#     derived from this software without specific prior written consent.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

###

import supybot.utils as utils
from supybot.commands import *
import supybot.plugins as plugins
import supybot.ircutils as ircutils
import supybot.callbacks as callbacks
from supybot import ircmsgs
import re
import sys

ENCODING = "utf-8"

class Canelator(callbacks.Plugin):
    """canelatr

    !topic Somewhere 1/1/2011 19:00
    !clear
    foolano++
    folano--
    """

    RE_INC =  u"(?P<name>[\\w0-9_.-]+)\\+\\+"
    RE_DEC =  u"(?P<name>[\\w0-9_.-]+)\\-\\-"

    def __init__(self, irc):
        super(callbacks.Plugin, self).__init__(irc)
        self.re_inc = re.compile(self.RE_INC, re.U|re.I)
        self.re_dec = re.compile(self.RE_DEC, re.U|re.I)

    def _channelTopic(self, irc):
        topic = irc.state.channels[channel].topic.decode(ENCODING)
        return topic

    def _parseTopic(self, irc, msg):
        channel = msg.args[0]
        topic = self._channelTopic(irc)
        try:
            rawdescr, rawcount, rawnicks = topic.rsplit("|", 2)
        except ValueError:
            return "", set()
        descr = rawdescr.strip()
        nicks = set(filter(None, (nick.strip()
                    for nick in rawnicks.strip().split(", "))))
        return descr, nicks

    def _setTopic(self, irc, msg, descr, players):
        channel = msg.args[0]
        playersline = ", ".join(sorted(players))
        topic = "%s | %d | %s" % (descr, len(players), playersline)
        irc.queueMsg(ircmsgs.topic(channel, topic.encode(ENCODING)))

    def clear(self, irc, msg, args, channel):
        """
        Clears the players list
        """
        self._setTopic(irc, msg, "Onde? Quando?", ())
    clear = wrap(clear, ["channel"])

    def topic(self, irc, msg, args, text):
        """
        Sets the game description
        """
        if text:
            descr, nicks = self._parseTopic(irc, msg)
            self._setTopic(irc, msg, text.decode(ENCODING), nicks)
        else:
            irc.reply(self._channelTopic())
    topic = wrap(topic, [additional("text")])

    def doPrivmsg(self, irc, msg):
        irc = callbacks.SimpleProxy(irc, msg)
        channel = msg.args[0]
        if not msg.isError and channel in irc.state.channels:
            try:
                umsg = msg.args[1].decode(ENCODING)
            except UnicodeDecodeError, e:
                sys.stderr.write("unicodedecodeerror: %r: %s\n" %
                (msg.args[1], e))
                return
            descr, nicks = self._parseTopic(irc, msg)
            orig = frozenset(nicks)
            match = None
            for match in self.re_dec.finditer(umsg):
                try:
                    nicks.remove(match.group("name"))
                except KeyError:
                    continue
            for match in self.re_inc.finditer(umsg):
                nicks.add(match.group("name"))
            if nicks != orig:
                self._setTopic(irc, msg, descr, nicks)

Class = Canelator

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

###
# Copyright (c) 2011, Bogdano Arendartchuk
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

class Canelator(callbacks.PluginRegexp):
    """Add the help for "@plugin help Canelator" here
    This should describe *how* to use this plugin."""

    regexps = ["inc", "dec"]

    def _parseTopic(self, irc, msg):
        channel = msg.args[0]
        topic = irc.state.channels[channel].topic
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
        irc.queueMsg(ircmsgs.topic(channel, topic))

    def inc(self, irc, msg, match):
        "(?P<name>[a-zA-Z0-9_.-]+)\\+\\+"
        name = match.group("name")
        descr, nicks = self._parseTopic(irc, msg)
        nicks.add(name)
        self._setTopic(irc, msg, descr, nicks)

    def dec(self, irc, msg, match):
        "(?P<name>[a-zA-Z_.-]+)\\-\\-"
        name = match.group("name")
        descr, nicks = self._parseTopic(irc, msg)
        try:
            nicks.remove(name)
        except KeyError:
            irc.error("uh?")
        else:
            self._setTopic(irc, msg, descr, nicks)

    def clear(self, irc, msg, args, channel):
        """
        Limpa a lista de jogadores e a descricao.
        """
        self._setTopic(irc, msg, "Aonde? Quando?", ())
    clear = wrap(clear, ["channel"])

    def topic(self, irc, msg, args, text):
        """
        Define a descricao. (duh!)
        """
        descr, nicks = self._parseTopic(irc, msg)
        self._setTopic(irc, msg, text, nicks)
    topic = wrap(topic, [additional("text")])

Class = Canelator

# vim:set shiftwidth=4 softtabstop=4 expandtab textwidth=79:

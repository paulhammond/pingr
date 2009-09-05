# Copyright (c) 2009 Paul Hammond
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.api import xmpp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp import xmpp_handlers
import os
import logging

class User(db.Model):
  """People who can be pinged"""
  im = db.IMProperty(required=True)
  subscribed = db.BooleanProperty()
  create= db.DateTimeProperty(required=True, auto_now_add=True)

  def __set_subscribe(self,state):
    user = User.get(self.key())
    user.subscribed = state
    user.put()
  
  def set_subscribe(self, state=True):
    db.run_in_transaction(self.__set_subscribe, state)


class XmppHandler(xmpp_handlers.BaseHandler):
  """Handler class for all XMPP activity."""

  def message_received(self, message):
    jid, resource = message.sender.split("/")
    sender = User.get_or_insert("xmpp:"+jid, im=db.IM("xmpp", jid ))
    if(message.body == "stop"):
      sender.set_subscribe(False)
      message.reply("Bye!")
    else:
      sender.set_subscribe(True)
      message.reply("Hello there!")

class MainPage(webapp.RequestHandler):
  """Web handler class"""
  
  def get(self):
    user = User.get_by_key_name("xmpp:" + self.request.get('jid'))
    if(user and user.subscribed):
      xmpp.send_message([user.im.address], 'ping')
      ok = True
    else:
      ok = False
    path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
    self.response.out.write(template.render(path, {'ok':ok}))

application = webapp.WSGIApplication([
  ('/_ah/xmpp/message/chat/', XmppHandler),
  ('/', MainPage)
],debug=True)
        
def main():
  run_wsgi_app(application)

if __name__ == "__main__":
  main()
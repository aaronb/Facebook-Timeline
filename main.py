#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
import os

class MainHandler(webapp.RequestHandler):
    def get(self):
        #self.response.out.write('<html><body>Hello world!</body></html>')

	guestbook_name=self.request.get('guestbook_name')
        #greetings_query = Greeting.all().ancestor(
        #    guestbook_key(guestbook_name)).order('-date')
        greetings = 'lala'#greetings_query.fetch(10)
	url = 'this is url'
        '''if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
	'''
        template_values = {
            'greetings': greetings,
            'url': url,
	    'data': 'examples/jfk/jfk.xml',
            #'url_linktext': url_linktext,
        }
	
	path = os.path.join(os.path.dirname(__file__), 'index.html')
	self.response.out.write(template.render(path, template_values))

def main():
    application = webapp.WSGIApplication([
       ('/', MainHandler),
       ('/canvas', MainHandler),
       ('/canvas/', MainHandler)
       #('/examples/jfk/', MainHandler)
       ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()

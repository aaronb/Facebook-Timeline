#!/usr/bin/env python
#
# Copyright 2010 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.



"""A barebones AppEngine application that uses Facebook for login."""

from appid import *

import facebook
import os.path
import wsgiref.handlers
from django.utils import simplejson
import re
import author

from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template


class User(db.Model):
    id = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)
    name = db.StringProperty(required=True)
    profile_url = db.StringProperty(required=True)
    access_token = db.StringProperty(required=True)


class BaseHandler(webapp.RequestHandler):
    """Provides access to the active Facebook user in self.current_user

    The property is lazy-loaded on first access, using the cookie saved
    by the Facebook JavaScript SDK to determine the user ID of the active
    user. See http://developers.facebook.com/docs/authentication/ for
    more information.
    """
    @property
    def current_user(self):
        if not hasattr(self, "_current_user"):
            self._current_user = None
            cookie = facebook.get_user_from_cookie(
                self.request.cookies, FACEBOOK_APP_ID, FACEBOOK_APP_SECRET)
            if cookie:
                # Store a local instance of the user data so we don't need
                # a round-trip to Facebook on every request
                user = User.get_by_key_name(cookie["uid"])
                if not user:
                    graph = facebook.GraphAPI(cookie["access_token"])
                    profile = graph.get_object("me")
                    user = User(key_name=str(profile["id"]),
                                id=str(profile["id"]),
                                name=profile["name"],
                                profile_url=profile["link"],
                                access_token=cookie["access_token"])
                    user.put()
                elif user.access_token != cookie["access_token"]:
                    user.access_token = cookie["access_token"]
                    user.put()
                self._current_user = user
        return self._current_user

    @property
    def graph(self):
        """Returns a Graph API client for the current user."""
        if not hasattr(self, "_graph"):
            if self.current_user:
                self._graph = facebook.GraphAPI(self.current_user.access_token)
            else:
                self._graph = facebook.GraphAPI()
        return self._graph


class HomeHandler(BaseHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), "index.html")
        args = dict(current_user=self.current_user,
                    facebook_app_id=FACEBOOK_APP_ID)
        self.response.out.write(template.render(path, args))
    def post(self):
       self.get()

def make_event(post):
   event = {}
   event["start"] = post["created_time"]

   if "icon" in post:
      event["icon"] = post["icon"]

   if "picture" in post:
      event["image"] = post["picture"]

   auth = None
   if "from" in post and "name" in post["from"]:
      auth = post["from"]["name"]

   description = []
   for field in ["message", "story", "description"]:
      if field in post:
         description.append(post[field])
   
   event["description"] = "<br>".join(description)

   event["title"] = event["description"][:40]

   event["description"] += " <b>" + auth + "</b>"

   return event


class WallHandler(BaseHandler):
    def get(self):
        graph = self.graph
        pargs = None
        events = list()
        for i in range(10):
           if pargs is None:
              feed = graph.get_connections("me", "feed")
           else:
              feed = graph.get_connections("me", "feed", **pargs)
           if "data" not in feed or len(feed["data"]) == 0:
              break

           for post in feed["data"]:
              events.append(make_event(post))

           user = self.current_user

           new_wall = author.generate_wall_posts(user, graph, 1)[0]
           events.append(make_event(new_wall))

           new_post = author.generate_status_updates(user, graph, 1)[0]
           events.append(make_event(new_post))

           if "paging" in feed and "next" in feed["paging"]:
              nextpage = feed["paging"]["next"]
              until = re.search('until=([0-9]+)', nextpage).group(1)
              #pargs = [("until", until), ("limit", "25")]
              pargs = {"until": until, "limit": "25"}
           else:
              break

        self.response.out.write(simplejson.dumps({"events": events}))

def main():
    util.run_wsgi_app(webapp.WSGIApplication([
       ("/", HomeHandler),
       ("/wall", WallHandler)
       ]))


if __name__ == "__main__":
    main()

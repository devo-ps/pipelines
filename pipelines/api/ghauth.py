# -*- coding: utf-8 -*-
import functools
import json
import logging

import os
from urllib.parse import urlencode

import requests
import tornado
from tornado import escape, httpclient
from tornado.auth import AuthError
from tornado.httputil import url_concat
from tornado.web import RequestHandler


log = logging.getLogger('pipelines')

class GithubOAuth2Mixin(object):
    """
    see
    https://docs.github.com/en/developers/apps/building-oauth-apps/authorizing-oauth-apps#web-application-flow
    """
    _OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    _OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
    _OAUTH_USER_BASE_URL = "https://api.github.com"
    _OAUTH_SETTINGS_KEY = "github_oauth"

    def get_auth_url(self, scopes: list[str] = None):
        args = {
            "client_id": self.gh_settings[self._OAUTH_SETTINGS_KEY]["key"],
            "response_type": 'code'
        }
        if scopes:
            args["scope"] = ",".join(scopes)
        return url_concat(self._OAUTH_AUTHORIZE_URL, args)

    @tornado.gen.coroutine
    def get_authenticated_user(self, code):
        """Handles the login for the Github user, returning a user object.

        Example usage::
            class GithubOAuth2LoginHandler(tornado.web.RequestHandler,
                                           GithubOAuth2Mixin):
                @tornado.gen.coroutine
                def get(self):
                    if self.get_argument("code", False):
                        user = yield self.get_authenticated_user(code=self.get_argument("code"))
                        # Save the user with e.g. set_secure_cookie
                    else:
                        return self.redirect(self.get_auth_url(scope=["user:email"]))
        """
        http = self.get_auth_http_client()
        body = urlencode({
            "client_id": self.gh_settings[self._OAUTH_SETTINGS_KEY]["key"],
            "client_secret": self.gh_settings[self._OAUTH_SETTINGS_KEY]["secret"],
            "code": code
        })

        # retrieve access token
        resp = yield http.fetch(
            self._OAUTH_ACCESS_TOKEN_URL,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
            body=body
        )
        if resp.error:
            raise AuthError("Github auth error: %s" % str(resp))
        args = escape.json_decode(escape.native_str(resp.body))
        access_token = args.get("access_token", None)
        if not access_token:
            log.warn("no access_token in token request")
            return None

        # retrieve user info
        user = yield self.github_request(
            path="/user",
            access_token=access_token
        )
        user['access_token'] = access_token

        scopes = args["scope"].split(",")
        has_user_email_scope = scopes.count("user:email") > 0
        if not has_user_email_scope:
            return user

        # retrieve email info
        emails = yield self.github_request(
            path="/user/emails",
            access_token=access_token
        )
        user["private_emails"] = emails
        return user

    @tornado.gen.coroutine
    def github_request(self, path, access_token=None, post_args=None, **args):
        url = self._OAUTH_USER_BASE_URL + path
        all_args = {}
        if access_token:
            all_args.update(args)
        if all_args:
            url += "?" + urlencode(all_args)

        http = self.get_auth_http_client()

        ua = "tornado"
        if post_args is not None:
            resp = yield http.fetch(
                url, method="POST", body=urlencode(post_args),
                user_agent=ua,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                auth_mode='basic', auth_username='_', auth_password=access_token)
        else:
            resp = yield http.fetch(
                url, method="GET", user_agent=ua,
                headers={"Accept": "application/json"}, auth_mode='basic',
                auth_username='_', auth_password=access_token)

        if resp.error:
            raise AuthError("Error response %s fetching %s" %
                            (resp.text, url))

        return escape.json_decode(resp.body)

    @staticmethod
    def get_auth_http_client():
        impl = 'tornado.simple_httpclient.SimpleAsyncHTTPClient'
        # debug support
        proxy_host = os.environ.get("PROXY_HOST")
        proxy_port = os.environ.get("PROXY_PORT")
        defaults = {
            'user_agent': 'tornado',
        }
        if proxy_host and proxy_port:
            log.debug('>> enable proxy support for tornado.httpclient')
            log.debug('>> proxy: %s:%s', proxy_host, proxy_port)
            # as for torado 6.0, proxy is only supported in
            # curl_httpclient, need to install pycurl
            defaults.update({
                'proxy_host': proxy_host,
                'proxy_port': int(proxy_port),
            })
            impl = 'tornado.curl_httpclient.CurlAsyncHTTPClient'

        httpclient.AsyncHTTPClient.configure(
            impl=impl,
            defaults=defaults)

        return httpclient.AsyncHTTPClient()


class GithubOAuth2LoginHandler(RequestHandler,
                               GithubOAuth2Mixin):

    gh_settings = {
        'github_oauth': {
            "key": os.getenv('GH_OAUTH_KEY', 'MISSING_KEY'),
            'secret': os.getenv('GH_OAUTH_SECRET', 'MISSING_SECRET')
        }
    }

    def get_current_user(self):
        log.info('Current user : %s' % self.get_secure_cookie("user"))
        if self.get_secure_cookie("user", None):
            return json.loads(self.get_secure_cookie("user"))

    @tornado.gen.coroutine
    def get(self):
        if self.get_argument('code', False):
            code = self.get_argument('code')
            user = yield self.get_authenticated_user(
                code=code,
            )

            if not user or not user.get('access_token'):
                log.debug('Auth failed, missing access_token')
                self.redirect(self.reverse_url('login'))
                return

            username = user.get('login')
            if not username:
                log.warn('Auth failed, missing login')
                self.redirect('/login')
                return

            resp = yield self.get_auth_http_client().fetch(
                'https://api.github.com/user/teams', method="GET",
                headers={"Accept": "application/json"},
                auth_mode='basic', auth_username='_',
                auth_password=user['access_token'])

            allowed_teams = self.settings['auth'].get('teams', [])
            allowed_teams_set = set()
            for org, team in allowed_teams:
                allowed_teams_set.add((org.lower(), team.lower()))
            log.debug('Allowed teams: %s' % allowed_teams_set)
            teams = json.loads(resp.body)

            user_teams_set = set()
            for x in teams:
                o = x.get('organization',{}).get('login', '').lower()
                t = x.get('slug', '').lower()
                if not o or not t:
                    continue
                user_teams_set.add((o, t))
            log.debug('user teams: %s' % user_teams_set)

            intersection = allowed_teams_set.intersection(user_teams_set)
            log.debug('intersection: %s' % intersection)
            if len(intersection) > 0:
                    log.debug('Allowed access to github user for team %s' % (intersection))
                    user['username'] = username
                    cookie = json.dumps(user, separators=(',',   ':'))
                    self.set_secure_cookie('user', cookie)
            else:
                log.debug('Access not allowed to user. User teams:  %s' % (
                    ['%s/%s' % (t.get('organization', {}).get('login'), t.get('slug')) for t in teams])
                )


            self.redirect(self.get_query_argument("next", "/"))
        else:
            self.redirect(self.get_auth_url(scopes=['read:org']))

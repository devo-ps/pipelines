import os.path
import unittest
import json
from tornado.testing import AsyncHTTPTestCase
import pipelines.api.server as server

WORKSPACE = os.path.realpath('test/fixtures/workspace')


class TestSlackbotAPI(AsyncHTTPTestCase):

    def get_app(self):
        return server.make_app('1234', WORKSPACE)

    def test_slackbot_success(self):
        '''
        Testing slackbot happy path
        '''
        url = ("/api/slackbot/df9136d0-cec8-4a9b-be79-414a599f54ad")
        response = self.fetch(
            url,
            method='POST',
            body='token=1MwKMNcAByCsmRfFdvjr6Bplj&team_id=T024GQDB5&team_domain=wiredcraft&channel_id=D030N2BN4&channel_name=testchan&user_id=U030N2BNA&user_name=tester&command=%2Fpipelines-test&text=deploy+api+staging+master&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT024GQDB5%2F329076112391%2FsyFUMbZHlfwu0Vt1pGWYPDNj'
        )
        self.assertEqual(response.code, 200)
        content = json.loads(response.body)
        self.assertEquals(
            {
                'text':
                'deploy triggered by tester',
                'response_type':
                'in_channel',
                'attachments': [{
                    'text':
                    'command: deploy\ncomponent: api\nenvironment: staging\nversion: master\n'
                }]
            }, content)

    def test_slackbot_wrong_slug(self):
        '''
        Testing slackbot happy path
        '''
        url = ("/api/slackbot/1234")
        response = self.fetch(
            url,
            method='POST',
            body='token=1MwKMNcAByCsmRfFdvjr6Bplj&team_id=T024GQDB5&team_domain=wiredcraft&channel_id=D030N2BNH&channel_name=directmessage&user_id=U030N2BNF&user_name=juha&command=%2Fpipelines-test&text=deploy+api+staging+master&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT024GQDB5%2F329076112391%2FsyFUMbZHlfwu0Vt1pGWYPDNj'
        )
        self.assertEqual(response.code, 404)


if __name__ == '__main__':
    unittest.main()
    # suite = unittest.TestLoader().loadTestsFromTestCase(TestAPIs)
    # unittest.TextTestRunner(verbosity=2).run(suite)
'''
Dump of real message coming from Slack:

POST /api/slackbot/d9dd879c-2925-46ef-afb1-1ffc680e2170 HTTP/1.1
User-Agent: Slackbot 1.0 (+https://api.slack.com/robots)
Accept-Encoding: gzip,deflate
Accept: application/json,*/*
Content-Length: 317
Content-Type: application/x-www-form-urlencoded
Host: 17dfe64b.ngrok.io
Cache-Control: max-age=259200
X-Forwarded-For: 54.161.187.202

token=1MwKMNcAByCsmRfFdvjr6Bplj&team_id=T024GQDB5&team_domain=wiredcraft&channel_id=D030N2BNH&channel_name=directmessage&user_id=U030N2BNF&user_name=juha&command=%2Fpipelines-test&text=deploy+api+staging+master&response_url=https%3A%2F%2Fhooks.slack.com%2Fcommands%2FT024GQDB5%2F329076112391%2FsyFUMbZHlfwu0Vt1pGWYPDNj

'''

import unittest
import json
from main import app

class TestChatService(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_chat_endpoint(self):
        data = {"prompt": "你好"}
        response = self.app.post('/chat',
                                 data=json.dumps(data),
                                 content_type='application/json')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
import unittest
from email.message import Message
import notify

class TestNotify(unittest.TestCase):
	def test_notify(self):
		msg = Message()
		msg["Subject"] = "test"
		subject: str = notify.getSubjectStr(msg)
		self.assertEqual("test", subject)

		#msg["Subject"] = "テスト"
		#subject: str = notify.getSubjectStr(msg)
		#self.assertEqual("テスト", subject)

if __name__ == "__main__":
    unittest.main()

import unittest
from unittest.mock import MagicMock, patch
import main

class TestSheepBot(unittest.TestCase):

    @patch('bot.bot.send_message')
    def test_start_command(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 12345

        main.start(message)

        mock_send_message.assert_called_once()
        args = mock_send_message.call_args[0]
        self.assertEqual(args[0], 12345)
        self.assertIn("Qo‘ylar nazorati botiga xush kelibsiz", args[1])

    @patch('bot.bot.send_message')
    def test_add_sheep(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 12345

        main.add_sheep(message)

        self.assertEqual(main.user_states[12345], 'awaiting_date')
        self.assertEqual(main.user_inputs[12345], {})
        mock_send_message.assert_called_once()
        self.assertIn("Xarid sanasini kiriting", mock_send_message.call_args[0][1])

    @patch('bot.bot.send_message')
    def test_handle_date(self, mock_send_message):
        message = MagicMock()
        message.chat.id = 12345
        message.text = "01-07-2025"

        # Simulate state before date entry
        main.user_states[12345] = 'awaiting_date'
        main.user_inputs[12345] = {}

        main.handle_date(message)

        self.assertEqual(main.user_states[12345], 'awaiting_price')
        self.assertEqual(main.user_inputs[12345]['date'], "01-07-2025")
        mock_send_message.assert_called_once()
        self.assertIn("Qo‘y narxini kiriting", mock_send_message.call_args[0][1])


if __name__ == '__main__':
    unittest.main()

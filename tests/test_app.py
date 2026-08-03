import unittest

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_guided_interface_renders_without_exceptions(self) -> None:
        app = AppTest.from_file("app.py", default_timeout=60).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [tab.label for tab in app.tabs],
            [
                "Build a procurement plan",
                "How to use it",
                "Toronto public example",
            ],
        )
        self.assertIn(
            "Build my procurement plan",
            [button.label for button in app.button],
        )


if __name__ == "__main__":
    unittest.main()

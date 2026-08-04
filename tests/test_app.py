import unittest

from streamlit.testing.v1 import AppTest


class AppTests(unittest.TestCase):
    def test_guided_interface_renders_without_exceptions(self) -> None:
        app = AppTest.from_file("app.py", default_timeout=60).run()
        self.assertFalse(app.exception)
        self.assertEqual(
            [tab.label for tab in app.tabs],
            [
                "1. Plan & approve",
                "2. Compare offers",
                "3. Review usage",
                "Toronto evidence",
                "Operating guide",
            ],
        )
        self.assertIn(
            "Build approval and procurement plan",
            [button.label for button in app.button],
        )

    def test_default_plan_runs_and_holds_unvalidated_commitment(self) -> None:
        app = AppTest.from_file("app.py", default_timeout=90).run()
        app.button(
            key=("FormSubmitter:procurement_planner_form-Build approval and procurement plan")
        ).click().run(timeout=90)
        self.assertFalse(app.exception)
        self.assertTrue(any("HOLD THE FULL COMMITMENT" in item.value for item in app.error))
        self.assertIn(
            "Download supplier pricing template",
            [button.label for button in app.get("download_button")],
        )


if __name__ == "__main__":
    unittest.main()

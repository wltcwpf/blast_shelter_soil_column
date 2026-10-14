import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest

class AppTests(unittest.TestCase):
    def test_default_and_controls(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'streamlit_app.py'),default_timeout=30).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(len(app.metric),7)
        app.radio[0].set_value('Regulated, constant pressure').run()
        self.assertEqual(len(app.exception),0)
        app.slider[1].set_value(0).run()
        self.assertEqual(len(app.exception),0)
        self.assertEqual(app.metric[0].value,'0.0000 mm')
    def test_invalid_geometry(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1] / 'streamlit_app.py'),default_timeout=30).run()
        app.number_input[2].set_value(60.).run()
        self.assertEqual(len(app.exception),0)
        self.assertGreater(len(app.error),0)

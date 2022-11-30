import json
import unittest

from parliament import Context
from werkzeug.test import EnvironBuilder

func = __import__("func")


class TestFunc(unittest.TestCase):

    def test_func_empty_request(self):
        resp, code = func.main({})
        self.assertEqual(resp, "{}")
        self.assertEqual(code, 200)

    def test_func_gets_request(self):
        builder = EnvironBuilder(method="GET")
        req = builder.get_request()
        resp, code = func.main(Context(req))
        self.assertIn("king penguin", resp)
        self.assertEqual(code, 200)

    def test_func_post_request(self):
        data = {"imgURL": "https://raw.githubusercontent.com/chzhyang/faas-workloads/main/tensorflow/image_recognition/tensorflow_image_classification/data/ILSVRC2012_test_00000181.JPEG"}
        builder = EnvironBuilder(
            method="POST", content_type="application/json", data=json.dumps(data))
        req = builder.get_request()
        resp, code = func.main(Context(req))
        self.assertIn("king penguin", resp)
        self.assertEqual(code, 200)


if __name__ == "__main__":
    unittest.main()

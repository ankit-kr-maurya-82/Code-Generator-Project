import unittest

from fastapi.testclient import TestClient

from main import app


class GenerateRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_requires_both_file_fields_when_one_is_missing(self) -> None:
        response = self.client.post(
            "/generate",
            json={"prompt": "", "file_name": "example.py", "file_content": None},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Both file_name and file_content are required for file analysis.",
        )

    def test_rejects_unsupported_file_types(self) -> None:
        response = self.client.post(
            "/generate",
            json={"prompt": "", "file_name": "image.png", "file_content": "not-a-supported-file"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["detail"],
            "Only PDF and text files are supported for analysis.",
        )


if __name__ == "__main__":
    unittest.main()

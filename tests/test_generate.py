import unittest
from unittest.mock import AsyncMock, patch

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

    @patch("routes.generate.add_conversation")
    @patch("routes.generate.extract_pdf_text", return_value="Extracted PDF text")
    @patch("routes.generate.generate_code", new_callable=AsyncMock)
    def test_extracts_pdf_text_before_generation(
        self,
        generate_code_mock: AsyncMock,
        extract_pdf_text_mock,
        add_conversation_mock,
    ) -> None:
        generate_code_mock.return_value = "Generated answer"

        response = self.client.post(
            "/generate",
            json={
                "prompt": "Summarize this",
                "files": [
                    {
                        "name": "notes.pdf",
                        "content": "data:application/pdf;base64,JVBERi0xLjQ=",
                    }
                ],
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Generated answer")
        extract_pdf_text_mock.assert_called_once_with(
            "notes.pdf",
            "data:application/pdf;base64,JVBERi0xLjQ=",
        )

        generated_prompt = generate_code_mock.call_args.args[0]
        self.assertIn("File name: notes.pdf", generated_prompt)
        self.assertIn("Extracted PDF text", generated_prompt)
        self.assertNotIn("JVBERi0xLjQ", generated_prompt)


if __name__ == "__main__":
    unittest.main()

import unittest

from services.pdf_service import clean_pdf_text


class PdfServiceTests(unittest.TestCase):
    def test_cleans_common_ocr_noise(self) -> None:
        noisy_text = """
        [Page 1 OCR]
        Payment     Details

        Name   :   Rahul   Kumar
        Amount     :    1200
        This is a bro-
        ken English line
        यह एक टूटी हुई
        हिंदी लाइन है।
        _________
        """

        cleaned = clean_pdf_text(noisy_text)

        self.assertIn("[Page 1 OCR]", cleaned)
        self.assertIn("Name: Rahul Kumar", cleaned)
        self.assertIn("Amount: 1200", cleaned)
        self.assertIn("This is a broken English line", cleaned)
        self.assertIn("यह एक टूटी हुई हिंदी लाइन है।", cleaned)
        self.assertNotIn("_________", cleaned)


if __name__ == "__main__":
    unittest.main()

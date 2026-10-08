import os
import sys
import unittest

# Ensure dags directory is in python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dags"))
)

from agentic_pipeline_dag import _heal_review, _parse_ollama_response, Config


class TestSelfHealingPipeline(unittest.TestCase):
    def test_clean_review_not_healed(self):
        review = {
            "review_id": "r1",
            "text": "The food was delicious and staff was super friendly!",
            "stars": 5,
        }
        result = _heal_review(review)
        self.assertFalse(result["was_healed"])
        self.assertIsNone(result["error_type"])
        self.assertEqual(result["action_taken"], "none")
        self.assertEqual(
            result["healed_text"],
            "The food was delicious and staff was super friendly!",
        )

    def test_missing_text_healed(self):
        review = {"review_id": "r2", "text": None, "stars": 3}
        result = _heal_review(review)
        self.assertTrue(result["was_healed"])
        self.assertEqual(result["error_type"], "missing_text")
        self.assertEqual(result["action_taken"], "filled_with_placeholder")
        self.assertEqual(result["healed_text"], "No review text provided.")

    def test_empty_text_healed(self):
        review = {"review_id": "r3", "text": "    ", "stars": 2}
        result = _heal_review(review)
        self.assertTrue(result["was_healed"])
        self.assertEqual(result["error_type"], "empty_text")
        self.assertEqual(result["action_taken"], "filled_with_placeholder")
        self.assertEqual(result["healed_text"], "No review text provided.")

    def test_wrong_type_number_healed(self):
        review = {"review_id": "r4", "text": 123456, "stars": 4}
        result = _heal_review(review)
        self.assertTrue(result["was_healed"])
        self.assertEqual(result["error_type"], "wrong_type")
        self.assertEqual(result["action_taken"], "type_conversion")
        self.assertEqual(result["healed_text"], "123456")

    def test_wrong_type_boolean_healed(self):
        review = {"review_id": "r5", "text": False, "stars": 1}
        result = _heal_review(review)
        self.assertTrue(result["was_healed"])
        self.assertEqual(result["error_type"], "wrong_type")
        self.assertEqual(result["action_taken"], "type_conversion")
        self.assertEqual(result["healed_text"], "False")

    def test_special_characters_only_healed(self):
        review = {"review_id": "r6", "text": "!@#$%^&*()_+=-", "stars": 1}
        result = _heal_review(review)
        self.assertTrue(result["was_healed"])
        self.assertEqual(result["error_type"], "special_characters_only")
        self.assertEqual(
            result["action_taken"], "replaced_special_characters"
        )
        self.assertEqual(result["healed_text"], "[Non-text content]")

    def test_too_long_text_truncated(self):
        long_text = "A" * (Config.MAX_TEXT_LENGTH + 50)
        review = {"review_id": "r7", "text": long_text, "stars": 4}
        result = _heal_review(review)
        self.assertTrue(result["was_healed"])
        self.assertEqual(result["error_type"], "too_long")
        self.assertEqual(result["action_taken"], "truncated_text")
        self.assertEqual(len(result["healed_text"]), Config.MAX_TEXT_LENGTH)
        self.assertTrue(result["healed_text"].endswith("..."))

    def test_parse_ollama_json_response(self):
        raw_response = '{"sentiment": "POSITIVE", "confidence": 0.96}'
        parsed = _parse_ollama_response(raw_response)
        self.assertEqual(parsed["label"], "POSITIVE")
        self.assertEqual(parsed["score"], 0.96)

    def test_parse_ollama_markdown_wrapped_response(self):
        raw_response = (
            '```json\n{"sentiment": "NEGATIVE", "confidence": 0.88}\n```'
        )
        parsed = _parse_ollama_response(raw_response)
        self.assertEqual(parsed["label"], "NEGATIVE")
        self.assertEqual(parsed["score"], 0.88)

    def test_parse_ollama_fallback_text_response(self):
        raw_response = "The sentiment of this review is clearly POSITIVE."
        parsed = _parse_ollama_response(raw_response)
        self.assertEqual(parsed["label"], "POSITIVE")
        self.assertEqual(parsed["score"], 0.75)


if __name__ == "__main__":
    unittest.main()

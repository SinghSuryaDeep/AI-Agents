"""
Author: SURYA DEEP SINGH
File Name: utils/common_utils.py
LinkedIn: https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import re
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts the first valid JSON object from a given text string.
    Handles cases where the JSON might be embedded within other text.
    """
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError as e:
            logger.warning(f"Could not decode JSON from text segment: {json_match.group()} - Error: {e}")
    logger.warning("No valid JSON found in the text.")
    return {}
if __name__ == "__main__":
    test_text_1 = "Some introductory text. {\"name\": \"Alice\", \"age\": 30} and some trailing text."
    test_text_2 = "No JSON here."
    test_text_3 = "Malformed JSON: {'key': 'value'}"
    test_text_4 = "{\"item\": \"laptop\", \"price\": 1200}"

    print(f"Extracted from 1: {extract_json_from_text(test_text_1)}")
    print(f"Extracted from 2: {extract_json_from_text(test_text_2)}")
    print(f"Extracted from 3: {extract_json_from_text(test_text_3)}")
    print(f"Extracted from 4: {extract_json_from_text(test_text_4)}")
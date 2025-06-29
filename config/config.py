"""
Author: SURYA DEEP SINGH
File Name: config/config.py
LinkedIn: https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration"""
    def __init__(self):
        self.project_id = os.getenv("WATSONX_PROJECT_ID")
        self.api_key = os.getenv("WATSONX_API_KEY")
        self.url = os.getenv("WATSONX_URL")
        self.model_id = os.getenv("WATSONX_MODEL_ID")
        print("\n" + "-" * 60)
        print(f"LLM used from IBM watsonx ** '{self.model_id}' **")
        print("-" * 60)
        print("\n")

    def validate(self) -> bool:
        """Validate configuration"""
        is_valid = all([
            self.project_id and self.project_id != "your-project-id",
            self.api_key and self.api_key != "your-api-key",
            self.url,
            self.model_id
        ])
        if not is_valid:
            logger.warning("Configuration not fully set. Please ensure project_id, api_key, url, and model_id are correctly configured.")
        return is_valid
if __name__ == "__main__":
    config = Config()
    print(f"Project ID: {config.project_id}")
    print(f"API Key (first 5 chars): {config.api_key[:5]}...")
    print(f"URL: {config.url}")
    print(f"Model ID: {config.model_id}")
    print(f"Config Valid: {config.validate()}")
"""
@Author: SURYA DEEP SINGH
Agentic Frameworks: AutoGen, BeeAI, LangChain, LangGraph, CrewAI, etc
File Name: main_showcase.py
LinkedIn 🔵 : https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import asyncio
import logging
import json
from typing import Dict, Any
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
from frameworks.autogen_financial_analysis import main as autogen_main
from frameworks.langgraph_ecommerce_workflow import main as langgraph_main
from frameworks.beeai_research_assistant import main as beeai_main
from frameworks.crewai_content_creation import main as crewai_main
from frameworks.langchain_legal_analysis import main as langchain_main

async def run_all_showcases():
    """Runs all the individual framework showcases."""
    print("\n")
    print("#" * 80)
    print("🚀 AGENTIC FRAMEWORKS STARTER KIT - FULL SHOWCASE 🚀")
    print("#" * 80)
    print("\n")

    showcase_results = {}
    try:
        logger.info("\n--- Starting AutoGen Financial Analysis Showcase ---")
        await autogen_main()
        showcase_results["autogen"] = "Success"
    except Exception as e:
        logger.error(f"AutoGen showcase failed: {e}")
        showcase_results["autogen"] = f"Failed: {e}"

    # Run LangGraph showcase
    try:
        logger.info("\n--- Starting LangGraph E-commerce Workflow Showcase ---")
        await langgraph_main()
        showcase_results["langgraph"] = "Success"
    except Exception as e:
        logger.error(f"LangGraph showcase failed: {e}")
        showcase_results["langgraph"] = f"Failed: {e}"

    # Run BeeAI showcase
    try:
        logger.info("\n--- Starting BeeAI Research Assistant Showcase ---")
        await beeai_main()
        showcase_results["beeai"] = "Success"
    except Exception as e:
        logger.error(f"BeeAI showcase failed: {e}")
        showcase_results["beeai"] = f"Failed: {e}"

    # Run CrewAI showcase
    try:
        logger.info("\n--- Starting CrewAI Content Creation Showcase ---")
        await crewai_main()
        showcase_results["crewai"] = "Success"
    except Exception as e:
        logger.error(f"CrewAI showcase failed: {e}")
        showcase_results["crewai"] = f"Failed: {e}"

    # Run LangChain showcase
    try:
        logger.info("\n--- Starting LangChain Legal Analysis Showcase ---")
        await langchain_main()
        showcase_results["langchain"] = "Success"
    except Exception as e:
        logger.error(f"LangChain showcase failed: {e}")
        showcase_results["langchain"] = f"Failed: {e}"

    print("\n" + "=" * 80)
    print("✅ ALL SHOWCASES COMPLETED ✅")
    print("=" * 80)
    print("Overall Summary:")
    print(json.dumps(showcase_results, indent=2))

if __name__ == "__main__":
    asyncio.run(run_all_showcases())
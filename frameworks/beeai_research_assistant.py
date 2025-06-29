"""
@Author: SURYA DEEP SINGH
Agentic Framework: BeeAI
File Name: frameworks/beeai_research_assistant.py
LinkedIn 🔵 : https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import asyncio
import logging
import json
from typing import Dict, Any
from beeai_framework.agents.react import ReActAgent
from beeai_framework.adapters.watsonx import WatsonxChatModel 
from beeai_framework.memory.token_memory import TokenMemory
from beeai_framework.tools.search.wikipedia import WikipediaTool
from config.config import Config


logger = logging.getLogger(__name__)
BEEAI_AVAILABLE = True

class BeeAIResearchAssistant:
    """BeeAI-based research assistant with tool usage."""
    
    def __init__(self, config: Config):
        self.config = config
        self.agent = None
        self.llm = None
        self._setup_agent()

    def _setup_agent(self):
        """Setup BeeAI agent with Watsonx LLM and tools."""
        if not BEEAI_AVAILABLE:
            logger.error("BeeAI framework components not fully available. Skipping agent setup.")
            return

        try:
            self.llm = WatsonxChatModel(
                api_key=self.config.api_key,
                project_id=self.config.project_id,
                model=self.config.model_id,
                url=self.config.url,
            )
            
            memory = TokenMemory(llm=self.llm)
            wikipedia_tool = WikipediaTool()
            self.agent = ReActAgent(
                llm=self.llm, 
                memory=memory, 
                tools=[wikipedia_tool]
            )
            
            logger.info("BeeAI research assistant initialized successfully.")
        except Exception as e:
            logger.error(f"Error setting up BeeAI agent: {e}")
            self.agent = None

    async def get_research_answer(self, query: str) -> Dict[str, Any]:
        """Gets an answer to a research query using BeeAI agent and its tools."""
        if not self.agent:
            return {"error": "BeeAI agent not available", "framework": "beeai"}

        try:
            logger.info(f"BeeAI: Answering research query: '{query}'")
            result = await self.agent.run(prompt=query)
            answer_text = self._extract_result(result)

            return {
                "query": query,
                "answer": answer_text,
                "framework": "beeai",
                "status": "completed" if answer_text else "failed_to_answer"
            }
        except Exception as e:
            logger.error(f"BeeAI research query failed: {e}")
            return {"error": str(e), "framework": "beeai"}

    def _extract_result(self, result) -> str:
        """Extract meaningful result from BeeAI response."""
        try:
            if hasattr(result, 'iterations') and result.iterations:
                last_iteration = result.iterations[-1]
                if hasattr(last_iteration, 'state') and hasattr(last_iteration.state, 'final_answer'):
                    if last_iteration.state.final_answer:
                        return last_iteration.state.final_answer
            if hasattr(result, 'result'):
                if hasattr(result.result, 'content'):
                    return result.result.content
                elif hasattr(result.result, 'text'):
                    return result.result.text
            if hasattr(result, 'answer') and hasattr(result.answer, 'text'):
                return result.answer.text
            elif hasattr(result, 'final_answer'):
                return result.final_answer
            elif isinstance(result, str):
                return result
            else:
                result_str = str(result)
                logger.debug(f"Result structure: {result_str[:500]}...")
                import re
                final_answer_match = re.search(r"final_answer='([^']*)'", result_str)
                if final_answer_match:
                    return final_answer_match.group(1)
                
                return "Unable to extract meaningful response from agent result"
                
        except Exception as e:
            logger.error(f"Error extracting result: {e}")
            return f"Error processing agent response: {str(e)}"


class BeeAIResearchAssistantFallback:
    """Fallback research assistant that works without specialized tools."""
    
    def __init__(self, config: Config):
        self.config = config
        self.agent = None
        self.llm = None
        self._setup_agent()

    def _setup_agent(self):
        """Setup basic BeeAI agent without specialized tools."""
        if not BEEAI_AVAILABLE:
            logger.error("BeeAI framework components not fully available. Skipping agent setup.")
            return

        try:
            # Create WatsonxChatModel directly
            self.llm = WatsonxChatModel(
                api_key=self.config.api_key,
                project_id=self.config.project_id,
                model=self.config.model_id,
                url=self.config.url,
            )
            memory = TokenMemory(llm=self.llm)
            self.agent = ReActAgent(
                llm=self.llm, 
                memory=memory, 
                tools=[]
            )
            
            logger.info("BeeAI research assistant (fallback mode) initialized successfully.")
        except Exception as e:
            logger.error(f"Error setting up BeeAI agent: {e}")
            self.agent = None

    async def get_research_answer(self, query: str) -> Dict[str, Any]:
        """Gets an answer to a research query using BeeAI agent."""
        if not self.agent:
            return {"error": "BeeAI agent not available", "framework": "beeai"}

        try:
            logger.info(f"BeeAI (Fallback): Answering research query: '{query}'")
            result = await self.agent.run(prompt=query)
            answer_text = self._extract_result(result)

            return {
                "query": query,
                "answer": answer_text,
                "framework": "beeai_fallback",
                "status": "completed" if answer_text else "failed_to_answer"
            }
        except Exception as e:
            logger.error(f"BeeAI research query failed: {e}")
            return {"error": str(e), "framework": "beeai_fallback"}

    def _extract_result(self, result) -> str:
        """Extract meaningful result from BeeAI response."""
        if hasattr(result, 'answer') and hasattr(result.answer, 'text'):
            return result.answer.text
        elif hasattr(result, 'final_answer'):
            return result.final_answer
        elif hasattr(result, 'result') and hasattr(result.result, 'final_answer'):
            return result.result.final_answer
        elif isinstance(result, str):
            return result
        else:
            result_str = str(result)
            logger.debug(f"Result structure: {result_str}")
            return result_str


async def main():
    """Main function to demonstrate BeeAI research assistant."""
    print("\n" + "=" * 60)
    print("📚 BEEAI RESEARCH ASSISTANT SHOWCASE")
    print("=" * 60)
    config = Config()
    if not config.validate():
        print("Watsonx configuration is invalid. Please set environment variables or update config.py.")
        return
    assistant = BeeAIResearchAssistant(config)
    if not assistant.agent:
        print("Primary assistant failed, trying fallback mode...")
        assistant = BeeAIResearchAssistantFallback(config)

    # Queries
    queries = [
        "What is the capital of France?",
        "Explain the concept of quantum entanglement in simple terms.",
        "If an item costs $150 and has a 20% discount, what is the final price?"
    ]

    for query in queries:
        print(f"\nQuerying: '{query}'")
        result = await assistant.get_research_answer(query)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
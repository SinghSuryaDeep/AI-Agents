"""
Author: SURYA DEEP SINGH
Framework: AutoGen
File Name: frameworks/autogen_financial_analysis.py
LinkedIn: https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import asyncio
import logging
import json
from typing import Dict, Any

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_watsonx_client.config import WatsonxClientConfiguration
from autogen_watsonx_client.client import WatsonXChatCompletionClient

from config.config import Config
from utils.common_utils import extract_json_from_text

logger = logging.getLogger(__name__)

class AutoGenFinancialAnalyzer:
    """AutoGen-based financial data analyzer"""
    def __init__(self, config: Config):
        self.config = config
        self.watsonx_client = None
        self._setup_client()

    def _setup_client(self):
        """Setup AutoGen Watsonx client"""
        try:
            wx_config = WatsonxClientConfiguration(
                project_id=self.config.project_id,
                url=self.config.url,
                api_key=self.config.api_key,
                model_id=self.config.model_id
            )
            self.watsonx_client = WatsonXChatCompletionClient(**wx_config)
            logger.info("AutoGen Watsonx client initialized successfully for financial analysis.")
        except ImportError as e:
            logger.error(f"AutoGen dependencies not installed: {e}. Please install 'autogen-agentchat' and 'autogen-watsonx-client'.")
        except Exception as e:
            logger.error(f"Error setting up AutoGen client: {e}")

    async def analyze_stock_performance(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stock performance and suggest investment strategy using AutoGen agents"""
        if not self.watsonx_client:
            return {"error": "AutoGen client not available", "framework": "autogen"}

        try:
            company_name = company_data.get("name", "a company")
            financial_data = company_data.get("financials", {})
            news_sentiment = company_data.get("news_sentiment", "neutral")

            # Create agents with more specific instructions
            analyst_agent = AssistantAgent(
                name="FinancialAnalyst",
                model_client=self.watsonx_client,
                system_message=f"""You are a skilled financial analyst. Analyze the provided financial data for {company_name} and provide:
1. Revenue and profitability assessment
2. Financial health indicators
3. Key strengths and weaknesses
4. Market positioning insights

Keep your analysis concise but comprehensive. End your response by saying 'Analysis complete - passing to strategist.'"""
            )

            strategist_agent = AssistantAgent(
                name="InvestmentStrategist",
                model_client=self.watsonx_client,
                system_message=f"""You are an expert investment strategist. Based on the financial analyst's report, provide your investment recommendation.

You MUST format your final response as a valid JSON object with this exact structure:
{{
    "company": "{company_name}",
    "financial_summary": "brief summary of key financial metrics",
    "investment_strategy": "Buy/Hold/Sell",
    "justification": "clear reasoning for your recommendation",
    "potential_returns": "High/Medium/Low",
    "risks": ["list", "of", "key", "risks"]
}}

After providing the JSON, write 'ANALYSIS_COMPLETE' to signal completion."""
            )
            termination_conditions = [
                TextMentionTermination("ANALYSIS_COMPLETE"),
                MaxMessageTermination(10)
            ]
            
            team = RoundRobinGroupChat(
                [analyst_agent, strategist_agent],
                termination_condition=termination_conditions[0] 
            )
            prompt = f"""
Please analyze the following financial data for {company_name}:

Financial Metrics:
{json.dumps(financial_data, indent=2)}

Recent News Sentiment: {news_sentiment}

FinancialAnalyst: Please provide your analysis first.
InvestmentStrategist: Then provide your investment strategy recommendation in the specified JSON format.
"""

            logger.info(f"AutoGen: Starting analysis for {company_name}...")
            task_result = await team.run(task=prompt)
            
            print("##############")
            print(f'Task completed. Message count: {len(task_result.messages)}')
            print(f'Stop reason: {task_result.stop_reason}')
            
            # Print all messages for debugging
            for i, msg in enumerate(task_result.messages):
                print(f"Message {i} from {msg.source}: {msg.content[:200]}...")
            print("##############")
            
            logger.info(f"AutoGen: Task completed for {company_name}.")

            result_json = self._extract_json_from_autogen_result(task_result)
            result_json["framework"] = "autogen"
            return result_json

        except Exception as e:
            logger.error(f"AutoGen financial analysis failed: {e}")
            return {"error": str(e), "framework": "autogen"}

    def _extract_json_from_autogen_result(self, task_result) -> Dict[str, Any]:
        """Extract JSON from AutoGen task result by iterating through messages."""
        if not task_result.messages:
            logger.warning("AutoGen task result contained no messages.")
            return {"error": "No messages in result from AutoGen"}

        # Look for JSON in messages from the InvestmentStrategist
        for message in reversed(task_result.messages):
            if isinstance(message, TextMessage):
                # Skip the initial user message
                if message.source == 'user':
                    continue
                    
                content = message.content
                logger.info(f"Checking message from {message.source}: {content[:100]}...")
                
                json_data = extract_json_from_text(content)
                if json_data:
                    logger.info("Successfully extracted JSON from AutoGen message.")
                    return json_data
                    
        # If no JSON found, try to extract any structured information
        logger.warning("No valid JSON found in any AutoGen message.")
        
        # Look for any agent responses to provide at least some analysis
        agent_responses = []
        for message in task_result.messages:
            if isinstance(message, TextMessage) and message.source != 'user':
                agent_responses.append(message.content)
        
        if agent_responses:
            return {
                "analysis": " ".join(agent_responses),
                "investment_strategy": "Manual review required",
                "note": "Agents responded but JSON extraction failed"
            }
        else:
            return {
                "error": "No agent responses found",
                "debug_info": f"Total messages: {len(task_result.messages)}, Stop reason: {task_result.stop_reason}"
            }

async def main():
    """Main function to demonstrate AutoGen financial analysis."""
    print("\n" + "=" * 60)
    print("📈 AUTOGEN FINANCIAL ANALYSIS SHOWCASE")
    print("=" * 60)

    config = Config()
    if not config.validate():
        print("Watsonx configuration is invalid. Please set environment variables or update watsonx_config.py.")
        return

    analyzer = AutoGenFinancialAnalyzer(config)

    # Case 1: Strong performance
    strong_company_data = {
        "name": "Tech Innovators Inc.",
        "financials": {
            "revenue_growth_qtr": "15%",
            "profit_margin": "20%",
            "debt_to_equity": "0.3",
            "cash_flow": "positive"
        },
        "news_sentiment": "highly positive"
    }
    print(f"\nAnalyzing: {strong_company_data['name']}")
    strong_result = await analyzer.analyze_stock_performance(strong_company_data)
    print(json.dumps(strong_result, indent=2))

    # Case 2: Mixed performance
    mixed_company_data = {
        "name": "Retail Giants Corp.",
        "financials": {
            "revenue_growth_qtr": "2%",
            "profit_margin": "8%",
            "debt_to_equity": "0.8",
            "cash_flow": "stable"
        },
        "news_sentiment": "mixed"
    }
    print(f"\nAnalyzing: {mixed_company_data['name']}")
    mixed_result = await analyzer.analyze_stock_performance(mixed_company_data)
    print(json.dumps(mixed_result, indent=2))

if __name__ == "__main__":
    asyncio.run(main())
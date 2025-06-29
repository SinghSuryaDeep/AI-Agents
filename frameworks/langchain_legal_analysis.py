"""
@Author: SURYA DEEP SINGH
Agentic Framework: LangChain
File Name: frameworks/langchain_legal_analysis.py
LinkedIn 🔵 : https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import logging
import json
from typing import Dict, Any

from langchain_ibm.chat_models import ChatWatsonx
from langchain_ibm import WatsonxToolkit
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

from config.config import Config
from utils.common_utils import extract_json_from_text

logger = logging.getLogger(__name__)

class LangChainLegalWorkflow:
    """LangChain-based workflow for legal document analysis."""
    def __init__(self, config: Config):
        self.config = config
        self.llm = None
        self.full_workflow = None 
        self._setup_chain()

    def _setup_chain(self):
        """Setup LangChain workflow for legal document analysis."""
        try:
            watsonx = WatsonxToolkit(
                url=self.config.url,
                project_id=self.config.project_id,
                apikey=self.config.api_key
            )
            self.llm = ChatWatsonx(
                watsonx_client=watsonx.watsonx_client,
                model_id=self.config.model_id,
                temperature=0.0,
            )

            # 1. Summary Chain
            summary_prompt = PromptTemplate(
                input_variables=["document_text"],
                template="""
                Summarize the following legal document concisely, highlighting its main purpose and key agreements.
                Document: {document_text}
                """
            )

            # 2. Key Clause Extraction Chain
            clause_extraction_prompt = PromptTemplate(
                input_variables=["document_text"],
                template="""
                From the following legal document, identify and extract the most important clauses related to rights, obligations, and termination conditions.
                List them as a JSON array of strings.
                Document: {document_text}
                Return only a JSON array, e.g., ["clause1", "clause2", "clause3"].
                """
            )
            clause_parser = JsonOutputParser()

            # 3. Risk Assessment Chain
            risk_assessment_prompt = PromptTemplate(
                input_variables=["document_text", "summary"],
                template="""
                Given the following legal document and its summary, assess potential legal risks or ambiguous points.
                Provide your assessment in JSON format with a risk level (Low, Medium, High) and bullet points of specific risks.
                Document Summary: {summary}
                Full Document (for context): {document_text}
                Return only valid JSON: {{ "risk_level": "Low/Medium/High", "identified_risks": ["risk1", "risk2"] }}
                """
            )
            risk_parser = JsonOutputParser()
            initial_analysis_parallel = RunnableParallel(
                summary=summary_prompt | self.llm,
                key_clauses=clause_extraction_prompt | self.llm | clause_parser
            )

            
            self.full_workflow = {
                "initial_analysis": initial_analysis_parallel,
                "document_text": RunnablePassthrough() 
            } | RunnableParallel(
                initial_analysis=lambda x: x["initial_analysis"], 
                risk_assessment=(
                    {
                        "document_text": lambda x: x["document_text"],
                        "summary": lambda x: x["initial_analysis"]["summary"].content 
                    }
                    | risk_assessment_prompt
                    | self.llm
                    | risk_parser
                )
            )

            logger.info("LangChain legal workflow initialized successfully.")

        except ImportError as e:
            logger.error(f"LangChain dependencies not installed: {e}. Please install 'langchain-ibm', 'langchain-core'.")
            self.full_workflow = None
        except Exception as e:
            logger.error(f"Error setting up LangChain legal workflow: {e}")
            self.full_workflow = None

    def analyze_legal_document(self, document_content: str) -> Dict[str, Any]:
        """Analyzes a legal document using the LangChain workflow."""
        if not self.full_workflow:
            return {"error": "LangChain not available or not properly initialized", "framework": "langchain"}

        try:
            logger.info("LangChain: Starting legal document analysis...")
            result = self.full_workflow.invoke(document_content)
            summary_content = result["initial_analysis"]["summary"].content if hasattr(result["initial_analysis"]["summary"], 'content') else str(result["initial_analysis"]["summary"])

            key_clauses = result["initial_analysis"]["key_clauses"]
            if not isinstance(key_clauses, list):
                key_clauses = extract_json_from_text(str(key_clauses))
                if not isinstance(key_clauses, list):
                     key_clauses = [str(key_clauses)] if key_clauses else []

            return {
                "document_summary": summary_content,
                "key_clauses_extracted": key_clauses,
                "risk_assessment": result["risk_assessment"],
                "framework": "langchain",
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"LangChain legal document analysis failed: {e}")
            return {"error": str(e), "framework": "langchain"}

def get_test_legal_document(scenario: str) -> Dict[str, str]:
    """Provides sample legal document content for testing."""
    if scenario == "simple_contract":
        return {
            "name": "Simple Service Agreement",
            "content": """
            This Service Agreement ("Agreement") is made effective as of January 1, 2025,
            between Company A (the "Service Provider") and Company B (the "Client").

            1. Services. The Service Provider agrees to provide web development services
               to the Client, as detailed in Exhibit A.
            2. Payment. The Client shall pay the Service Provider a fee of $5,000 upon
               completion of services.
            3. Term. This Agreement shall commence on the Effective Date and continue
               until the services are completed, unless terminated earlier.
            4. Termination. Either party may terminate this Agreement with 30 days'
               written notice.
            5. Governing Law. This Agreement shall be governed by the laws of the State of New York.
            """
        }
    elif scenario == "complex_nda":
        return {
            "name": "Complex Non-Disclosure Agreement",
            "content": """
            NON-DISCLOSURE AGREEMENT

            This Non-Disclosure Agreement (hereinafter "Agreement"), dated this 25th day of June, 2025 (the "Effective Date"),
            is made by and between Global Innovations Inc. (hereinafter "Disclosing Party")
            and Tech Solutions LLC (hereinafter "Receiving Party").

            WHEREAS, the Disclosing Party possesses certain confidential and proprietary information
            (hereinafter "Confidential Information") that it wishes to disclose to the Receiving Party
            for the sole purpose of evaluating a potential business collaboration (the "Permitted Purpose");

            NOW, THEREFORE, in consideration of the mutual covenants and agreements contained herein,
            the parties agree as follows:

            1. Definition of Confidential Information. "Confidential Information" shall mean any and all
               information disclosed by the Disclosing Party to the Receiving Party, whether oral,
               written, electronic, or in any other form, including but not limited to, trade secrets,
               business plans, financial data, customer lists, technical data, product designs, marketing strategies,
               and software code. This does not include information that is publicly available or independently developed.

            2. Obligations of Receiving Party. The Receiving Party agrees:
               a. To use the Confidential Information solely for the Permitted Purpose.
               b. To maintain the Confidential Information in strict confidence and take all reasonable measures
                  to protect its secrecy.
               c. Not to disclose, copy, or reproduce any Confidential Information without the prior
                  written consent of the Disclosing Party.
               d. To limit access to Confidential Information to its employees, agents, or contractors
                  who have a need to know for the Permitted Purpose and who are bound by confidentiality obligations
                  at least as restrictive as those contained herein.

            3. Term and Termination. This Agreement shall remain in effect for a period of five (5) years
               from the Effective Date, or until the Confidential Information becomes public knowledge
               through no fault of the Receiving Party. Either party may terminate this Agreement
               immediately upon written notice if the other party breaches any material term of this Agreement.
               Upon termination, all Confidential Information shall be returned or destroyed.

            4. Return of Confidential Information. Upon request of the Disclosing Party, the Receiving Party
               shall promptly return or destroy all Confidential Information.

            5. Remedies. The Receiving Party acknowledges that a breach of this Agreement would cause
               irreparable harm to the Disclosing Party, for which monetary damages would be an inadequate remedy.
               Therefore, the Disclosing Party shall be entitled to seek injunctive relief in addition to any other
               remedies available at law or in equity.

            6. Governing Law. This Agreement shall be governed by and construed in accordance with the
               laws of the State of Delaware, without regard to its conflict of law principles.
            """
        }
    else:
        return {"name": "Empty Document", "content": ""}

async def main():
    """Main function to demonstrate LangChain legal analysis."""
    print("\n" + "=" * 60)
    print("⚖️ LANGCHAIN LEGAL DOCUMENT ANALYSIS SHOWCASE")
    print("=" * 60)

    config = Config() 
    if not config.validate():
        print("Watsonx configuration is invalid. Please set environment variables or update watsonx_config.py.")
        return

    analyzer = LangChainLegalWorkflow(config)

    # Case 1: Simple Service Agreement
    simple_doc_data = get_test_legal_document("simple_contract")
    print(f"\nAnalyzing: {simple_doc_data['name']}")
    simple_result = analyzer.analyze_legal_document(simple_doc_data["content"])
    print(json.dumps(simple_result, indent=2, default=str)) # Use default=str for any non-JSON serializable objects

    # Case 2: Complex Non-Disclosure Agreement
    complex_doc_data = get_test_legal_document("complex_nda")
    print(f"\nAnalyzing: {complex_doc_data['name']}")
    complex_result = analyzer.analyze_legal_document(complex_doc_data["content"])
    print(json.dumps(complex_result, indent=2, default=str))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
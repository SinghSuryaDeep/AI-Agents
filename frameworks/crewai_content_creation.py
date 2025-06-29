"""
Author: SURYA DEEP SINGH
Framework: CrewAI
File Name: frameworks/crewai_content_creation.py
LinkedIn: https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import logging
import json
from typing import Dict, Any
from crewai import Agent, Task, Crew, Process, LLM
from config.config import Config


logger = logging.getLogger(__name__)

class CrewAIContentCreation:
    """CrewAI-based content creation team."""
    def __init__(self, config: Config):
        self.config = config
        self.llm = None
        self._setup_crew()

    def _setup_crew(self):
        """Setup CrewAI content creation team."""
        if not all([Agent, Task, Crew, Process, LLM]): 
            logger.error("CrewAI framework components not fully available. Skipping crew setup.")
            return

        try:
            
            self.llm = LLM(
                model=f"watsonx/{self.config.model_id}",
                api_base=self.config.url,
                api_key=self.config.api_key,
                project_id=self.config.project_id,
                temperature=0.2,
            )

            self.writer = Agent(
                role='Content Writer',
                goal='Draft engaging and informative blog posts based on given topics',
                backstory='Experienced writer with a knack for transforming complex ideas into clear, readable content.',
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            self.editor = Agent(
                role='Content Editor',
                goal='Review, refine, and optimize drafted content for clarity, grammar, and SEO',
                backstory='Detail-oriented editor with a sharp eye for errors and a strong understanding of content best practices.',
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            logger.info("CrewAI content creation team initialized successfully.")
        except Exception as e:
            logger.error(f"Error setting up CrewAI: {e}")
            self.llm = None

    def generate_blog_post(self, topic: str, word_count_target: int = 500) -> Dict[str, Any]:
        """Generates a blog post using the CrewAI team."""
        if not self.llm:
            return {"error": "CrewAI not available or not properly initialized", "framework": "crewai"}

        try:
            draft_task = Task(
                description=f"""
                Draft a compelling and informative blog post about "{topic}".
                The post should be approximately {word_count_target} words.
                Focus on introducing the topic, explaining key concepts, and providing valuable insights.
                Ensure it's well-structured with an introduction, main body, and conclusion.
                """,
                agent=self.writer,
                expected_output=f"A {word_count_target}-word draft blog post on '{topic}'."
            )

            edit_task = Task(
                description=f"""
                Review and refine the drafted blog post on "{topic}".
                - Check for grammar, spelling, and punctuation errors.
                - Improve clarity, flow, and conciseness.
                - Ensure the tone is appropriate for a professional blog.
                - Optimize for readability and engagement.
                - Provide the final, polished blog post.
                """,
                agent=self.editor,
                context=[draft_task],
                expected_output="A polished, final version of the blog post, ready for publication."
            )

            crew = Crew(
                agents=[self.writer, self.editor],
                tasks=[draft_task, edit_task],
                verbose=True,
                process=Process.sequential
            )

            logger.info(f"CrewAI: Generating blog post for topic '{topic}'...")
            result = crew.kickoff()

            return {
                "topic": topic,
                "generated_content": str(result), 
                "framework": "crewai",
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"CrewAI content creation failed for topic '{topic}': {e}")
            return {"error": str(e), "framework": "crewai"}

def get_test_content_topic(scenario: str) -> Dict[str, Any]:
    """Provides sample content topics for testing."""
    if scenario == "tech":
        return {"topic": "The Future of AI in Healthcare", "word_count": 600}
    elif scenario == "marketing":
        return {"topic": "Effective SEO Strategies for Small Businesses", "word_count": 400}
    else:
        return {"topic": "General Knowledge", "word_count": 300}

async def main():
    """Main function to demonstrate CrewAI content creation."""
    print("\n" + "=" * 60)
    print("📝 CREWAI CONTENT CREATION SHOWCASE")
    print("=" * 60)

    config = Config()
    if not config.validate():
        print("Watsonx configuration is invalid. Please set environment variables or update watsonx_config.py.")
        return

    creator = CrewAIContentCreation(config)

    #  Case 1: Tech topic
    tech_data = get_test_content_topic("tech")
    print(f"\nCreating content for: '{tech_data['topic']}'")
    tech_result = creator.generate_blog_post(tech_data["topic"], tech_data["word_count"])
    print(json.dumps(tech_result, indent=2))

    # Case 2: Marketing topic
    marketing_data = get_test_content_topic("marketing")
    print(f"\nCreating content for: '{marketing_data['topic']}'")
    marketing_result = creator.generate_blog_post(marketing_data["topic"], marketing_data["word_count"])
    print(json.dumps(marketing_result, indent=2))

if __name__ == "__main__":
    main_sync = main()
    import asyncio
    asyncio.run(main_sync)
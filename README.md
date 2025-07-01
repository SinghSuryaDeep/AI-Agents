---

# 🚀 Agentic Frameworks Starter Kit 🚀

This repository provides a comprehensive starter kit demonstrating the power and versatility of various **Agentic AI frameworks like AutoGen, BeeAI, LangChain, LangGraph, CrewAI, etc.**. Each framework is showcased through a practical use case, illustrating its strengths and how it can be leveraged for different applications.

---

| Agentic Framework | Implementation File                                                                                                                               |
| ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| AutoGen           | [frameworks/autogen\_financial\_analysis.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/autogen_financial_analysis.py)     |
| BeeAI             | [frameworks/beeai\_research\_assistant.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/beeai_research_assistant.py)         |
| CrewAI            | [frameworks/crewai\_content\_creation.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/crewai_content_creation.py)           |
| LangChain         | [frameworks/langchain\_legal\_analysis.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/langchain_legal_analysis.py)         |
| LangGraph         | [frameworks/langgraph\_ecommerce\_workflow.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/langgraph_ecommerce_workflow.py) |

## 🌟 Features

* **Centralized Configuration**: A `Config` class to manage Watsonx API credentials and model details, ensuring easy setup and secure access.
* **Modular Design**: Each agentic framework is implemented in its own dedicated file, promoting clarity and reusability.
* **Practical Use Cases**: Real-world scenarios for each framework, showcasing their capabilities in financial analysis, e-commerce workflows, research assistance, content creation, and legal document analysis.
* **Watsonx Integration**: All examples are configured to use IBM Watsonx as the underlying Large Language Model (LLM) provider.
* **Asynchronous Execution**: Leverages `asyncio` for efficient handling of concurrent agent interactions where applicable.

---

## [frameworks/autogen\_financial\_analysis.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/autogen_financial_analysis.py)

### 🧠 Framework: AutoGen by Microsoft

AutoGen is a framework that enables the development of LLM applications by allowing multiple agents to converse with each other to solve tasks. It provides a flexible and conversational AI paradigm.

### 💼 Use Case: Financial Analysis

This AutoGen example demonstrates how to build a multi-agent system for **financial stock performance analysis and investment strategy recommendation**.

#### How it Works:

Two specialized agents, `FinancialAnalyst` and `InvestmentStrategist`.

1. **FinancialAnalyst**: Analyzes provided financial data (revenue, profit, debt, cash flow) and news sentiment for a given company. It assesses financial health, identifies strengths/weaknesses, and provides market positioning insights.
2. **InvestmentStrategist**: Takes the analyst's report and formulates an investment recommendation (Buy/Hold/Sell) with justification, potential returns, and risks. The strategist is instructed to output its final recommendation in a structured JSON format.

The `AutoGenFinancialAnalyzer` orchestrates this conversation, taking company financial data as input and returning a detailed investment recommendation.

---

## [frameworks/beeai\_research\_assistant.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/beeai_research_assistant.py)

### 🧠 Framework: BeeAI by IBM

BeeAI is an agentic framework designed to build intelligent agents that can reason, plan, and use tools to achieve goals. It emphasizes structured agent behavior and memory management.

### 💼 Use Case: Research Assistant

This BeeAI example implements a **research assistant capable of answering queries by leveraging external tools**, specifically Wikipedia. A fallback mechanism is also included for scenarios where specialized tools might not be fully functional.

#### How it Works:

The `BeeAIResearchAssistant` utilizes a `ReActAgent` (Reasoning and Acting) which allows the agent to decide when to use its available tools.

1. **WatsonxChatModel**: The LLM for the agent is provided by `WatsonxChatModel`.
2. **TokenMemory**: A `TokenMemory` is used to manage the agent's conversational context.
3. **WikipediaTool**: The agent is equipped with a `WikipediaTool` to perform information retrieval. When a query requires external knowledge, the agent uses this tool to search Wikipedia and synthesize an answer.
4. **Fallback Mechanism**: `BeeAIResearchAssistantFallback` demonstrates a simpler agent without specialized tools, providing a basic response directly from the LLM.

The assistant takes a natural language query and returns a researched answer, indicating the framework used and its status.

---

## [frameworks/crewai\_content\_creation.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/crewai_content_creation.py)

### 🧠 Framework: CrewAI by CrewAI

CrewAI is a framework for orchestrating role-playing autonomous AI agents. It enables agents to work together in a structured "crew" to achieve a common goal, making it ideal for multi-step, collaborative tasks.

### 💼 Use Case: Content Creation

This CrewAI example showcases a team of agents collaborating to **generate polished blog posts** based on a given topic and word count.

#### How it Works:

The `CrewAIContentCreation` class sets up a sequential workflow with two agents:

1. **Content Writer (`Agent`)**:

   * **Role**: 'Content Writer'
   * **Goal**: 'Draft engaging and informative blog posts based on given topics'
   * **Task**: `draft_task` - responsible for generating the initial blog post draft.
2. **Content Editor (`Agent`)**:

   * **Role**: 'Content Editor'
   * **Goal**: 'Review, refine, and optimize drafted content for clarity, grammar, and SEO'
   * **Task**: `edit_task` - takes the writer's draft, performs editing, and produces the final version.

A `Crew` is established with these agents and their respective tasks, executing them in a `sequential` process. The `generate_blog_post` method kicks off this crew, returning the final generated content.

---

## [frameworks/langchain\_legal\_analysis.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/langchain_legal_analysis.py)

### 🧠 Framework: LangChain by LangChain

LangChain is a widely used framework for developing applications powered by language models. It provides modular components and chains to build complex LLM workflows, enabling integration with various tools and data sources.

### 💼 Use Case: Legal Document Analysis

This LangChain example demonstrates a comprehensive workflow for **analyzing legal documents**, extracting key information, and assessing potential risks.

#### How it Works:

The `LangChainLegalWorkflow` constructs a pipeline using `Runnable` components:

1. **Summary Chain**: Uses a `PromptTemplate` and `ChatWatsonx` to generate a concise summary of the legal document.
2. **Key Clause Extraction Chain**: Employs another `PromptTemplate` and `ChatWatsonx` with `JsonOutputParser` to identify and extract important clauses as a JSON array.
3. **Risk Assessment Chain**: Takes both the full document and its summary to assess legal risks, outputting a risk level and identified risks in JSON format.

These chains are combined using `RunnableParallel` and `RunnablePassthrough` to create a `full_workflow`. The `analyze_legal_document` method invokes this workflow, returning a structured analysis including summary, key clauses, and risk assessment.

---

## [frameworks/langgraph\_ecommerce\_workflow.py](https://github.com/SinghSuryaDeep/Agentic-AI/blob/main/frameworks/langgraph_ecommerce_workflow.py)

### 🧠 Framework: LangGraph by LangChain

LangGraph is an extension of LangChain, designed for building stateful, multi-actor applications with LLMs. It allows defining flows as graphs, where nodes represent computational steps (agents, tools, LLMs) and edges define transitions based on state.

### 💼 Use Case: E-commerce Order Processing

This LangGraph example builds a **stateful workflow for processing e-commerce orders**, including validation, inventory checks, and shipping confirmation.

#### How it Works:

The `LangGraphEcommerceWorkflow` defines an `OrderState` and a `StateGraph` with the following nodes:

1. **`validate_order_node`**: Uses the LLM to analyze order details for fraud or inconsistencies, returning a "valid" or "suspicious" status.
2. **`check_inventory_node`**: Simulates checking inventory availability for items in the order.
3. **`confirm_shipping_node`**: Generates a customer-friendly shipping confirmation report using the LLM.

The graph defines conditional edges: after inventory check, if items are in stock, it proceeds to shipping; otherwise, the workflow ends. The `process_order` method initializes the state and invokes the compiled graph, providing a detailed status and final report.

---

## 🛠️ Setup and Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/SinghSuryaDeep/AI-Agents.git
   cd AI-Agents
   ```

2. **Install dependencies**:
   It's recommended to use a virtual environment.

   ```bash
   python -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Configure Watsonx API Credentials**:
   Create a `.env` file in the root directory or set the following environment variables:

   * `WATSONX_PROJECT_ID`: Your IBM Watsonx project ID.
   * `WATSONX_API_KEY`: Your IBM Watsonx API Key.
   * `WATSONX_URL`: The Watsonx API endpoint URL.
   * `WATSONX_MODEL_ID`: The ID of the LLM model to use (e.g., `ibm/granite-3-3-8b-instruct`).

   Example `.env` file:

   ```
   WATSONX_PROJECT_ID="your-project-id"
   WATSONX_API_KEY="your-api-key"
   WATSONX_URL="https://us-south.ml.cloud.ibm.com"
   WATSONX_MODEL_ID="model-name"
   ```

---

## 🚀 Running the Showcases

To run all the framework showcases sequentially, execute the `main_showcase.py` file:

```bash
python main_showcase.py
```

This script will run each framework's demonstration and print its output to the console, along with an overall summary of results.

---

## 🔗 Connect

**SURYA DEEP SINGH**
LinkedIn 🔵 : [https://www.linkedin.com/in/surya-deep-singh-b9b94813a/](https://www.linkedin.com/in/surya-deep-singh-b9b94813a/)

---

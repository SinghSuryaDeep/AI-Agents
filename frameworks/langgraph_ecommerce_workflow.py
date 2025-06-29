"""
Author: SURYA DEEP SINGH
Framework: LangGraph
File Name: frameworks/langgraph_ecommerce_workflow.py
LinkedIn: https://www.linkedin.com/in/surya-deep-singh-b9b94813a/
"""

import logging
import json
from typing import Dict, Any, TypedDict
from datetime import datetime

from langchain_core.tools import tool
from langgraph.graph import StateGraph, END, START
from langchain_ibm import WatsonxToolkit
from langchain_ibm.chat_models import ChatWatsonx

from config.config import Config
from utils.common_utils import extract_json_from_text

logger = logging.getLogger(__name__)

class OrderState(TypedDict):
    """Represents the state of an e-commerce order."""
    order_id: str
    items: list
    customer_info: dict
    validation_status: str
    inventory_status: str
    shipping_status: str
    processed_report: str
    metadata: dict

class LangGraphEcommerceWorkflow:
    """LangGraph-based e-commerce order processing workflow."""
    def __init__(self, config: Config):
        self.config = config
        self.chat = None
        self.compiled_graph = None
        self._setup_graph()

    def _setup_graph(self):
        """Setup LangGraph workflow for order processing."""
        try:
            watsonx = WatsonxToolkit(
                url=self.config.url,
                project_id=self.config.project_id,
                apikey=self.config.api_key
            )
            self.chat = ChatWatsonx(
                watsonx_client=watsonx.watsonx_client,
                model_id=self.config.model_id,
                temperature=0.1,
            )

            def validate_order_node(state: OrderState) -> Dict[str, Any]:
                """Validates the order details."""
                order_id = state.get("order_id")
                items = state.get("items", [])
                customer_info = state.get("customer_info", {})

                if not order_id or not items or not customer_info:
                    logger.warning(f"Order {order_id}: Missing crucial information for validation.")
                    return {"validation_status": "failed", "metadata": {"error": "Missing order details"}}

                validation_prompt = f"""
                Analyze the following order for potential fraud or inconsistencies:
                Order ID: {order_id}
                Items: {json.dumps(items)}
                Customer Info: {json.dumps(customer_info)}

                Based on typical e-commerce fraud patterns, is this order "valid" or "suspicious"?
                Return a JSON object: {{"status": "valid/suspicious", "reason": "short explanation"}}
                """
                try:
                    response = self.chat.invoke(validation_prompt).content
                    validation_result = extract_json_from_text(response)
                    status = validation_result.get("status", "suspicious")
                    reason = validation_result.get("reason", "No specific reason provided.")
                    logger.info(f"Order {order_id}: Validation status - {status} ({reason})")
                    return {"validation_status": status, "metadata": {"validation_reason": reason}}
                except Exception as e:
                    logger.error(f"LLM validation failed for order {order_id}: {e}")
                    return {"validation_status": "failed", "metadata": {"error": f"LLM validation error: {e}"}}

            def check_inventory_node(state: OrderState) -> Dict[str, Any]:
                """Checks inventory for order items."""
                order_id = state.get("order_id")
                items = state.get("items", [])
                all_items_available = True
                unavailable_items = []
                for item in items:
                    if "unavailable" in item.get("name", "").lower(): # Example for simulation
                        all_items_available = False
                        unavailable_items.append(item.get("name"))

                if not all_items_available:
                    logger.warning(f"Order {order_id}: Some items are out of stock: {', '.join(unavailable_items)}")
                    return {"inventory_status": "out_of_stock", "metadata": {"unavailable_items": unavailable_items}}
                else:
                    logger.info(f"Order {order_id}: All items in stock.")
                    return {"inventory_status": "in_stock"}

            def confirm_shipping_node(state: OrderState) -> Dict[str, Any]:
                """Confirms shipping details and generates a report."""
                order_id = state.get("order_id")
                items = state.get("items", [])
                customer_info = state.get("customer_info", {})

                shipping_status = "shipped"
                shipping_notes = f"Order {order_id} containing {len(items)} items for {customer_info.get('name')} at {customer_info.get('address')} has been processed and shipped."

                report_prompt = f"""
                Generate a concise, customer-friendly shipping confirmation message for the following order:
                Order ID: {order_id}
                Items: {json.dumps(items)}
                Customer Name: {customer_info.get('name')}
                Shipping Address: {customer_info.get('address')}
                Shipping Status: {shipping_status}
                Notes: {shipping_notes}

                Focus on clarity and confirmation.
                """
                try:
                    report_message = self.chat.invoke(report_prompt).content
                    logger.info(f"Order {order_id}: Shipping confirmed.")
                    return {"shipping_status": shipping_status, "processed_report": report_message}
                except Exception as e:
                    logger.error(f"LLM report generation failed for order {order_id}: {e}")
                    return {"shipping_status": "confirmed_with_error", "processed_report": f"Shipping confirmed for {order_id}, but report generation failed: {e}"}

            self.graph = StateGraph(OrderState)
            self.graph.add_node("validate_order", validate_order_node)
            self.graph.add_node("check_inventory", check_inventory_node)
            self.graph.add_node("confirm_shipping", confirm_shipping_node)

            self.graph.add_edge(START, "validate_order")
            self.graph.add_edge("validate_order", "check_inventory")

            self.graph.add_conditional_edges(
                "check_inventory",
                lambda state: "confirm_shipping" if state["inventory_status"] == "in_stock" else END,
                {
                    "confirm_shipping": "confirm_shipping",
                    END: END 
                }
            )
            self.graph.add_edge("confirm_shipping", END)

            self.compiled_graph = self.graph.compile()
            logger.info("LangGraph e-commerce workflow initialized successfully.")

        except ImportError as e:
            logger.error(f"LangGraph dependencies not installed: {e}. Please install 'langchain-ibm', 'langgraph', 'langchain-core', 'typing-extensions'.")
            self.graph = None
            self.compiled_graph = None
        except Exception as e:
            logger.error(f"Error setting up LangGraph: {e}")
            self.graph = None
            self.compiled_graph = None

    def process_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processes an e-commerce order using the LangGraph workflow."""
        if not self.compiled_graph:
            return {"error": "LangGraph not available", "framework": "langgraph"}

        try:
            initial_state = {
                "order_id": order_data.get("order_id"),
                "items": order_data.get("items"),
                "customer_info": order_data.get("customer_info"),
                "validation_status": "",
                "inventory_status": "",
                "shipping_status": "",
                "processed_report": "",
                "metadata": {}
            }
            logger.info(f"LangGraph: Processing order {order_data.get('order_id')}...")
            result = self.compiled_graph.invoke(initial_state)

            final_report = result.get("processed_report", "Order processing completed. No specific report generated or an error occurred.")
            status = "completed" if "error" not in result.get("metadata", {}) else "failed"
            if result.get("validation_status") == "suspicious":
                status = "flagged_suspicious"
            elif result.get("inventory_status") == "out_of_stock":
                status = "items_unavailable"

            return {
                "order_processing_status": status,
                "final_report": final_report,
                "detailed_state": result,
                "framework": "langgraph",
                "status": "completed"
            }
        except Exception as e:
            logger.error(f"LangGraph order processing failed for order {order_data.get('order_id')}: {e}")
            return {"error": str(e), "framework": "langgraph"}

def get_test_order_data(scenario: str) -> Dict[str, Any]:
    """Provides sample order data for different scenarios."""
    if scenario == "valid":
        return {
            "order_id": "ORD_001",
            "items": [
                {"item_id": "P001", "name": "Laptop Pro", "quantity": 1, "price": 1200},
                {"item_id": "P002", "name": "Wireless Mouse", "quantity": 2, "price": 25}
            ],
            "customer_info": {
                "name": "Alice Smith",
                "email": "alice.smith@example.com",
                "address": "123 Main St, Anytown, USA",
                "payment_method": "credit_card"
            }
        }
    elif scenario == "suspicious":
        return {
            "order_id": "ORD_002",
            "items": [
                {"item_id": "P003", "name": "High-End Graphics Card", "quantity": 5, "price": 800} # Suspiciously high quantity for expensive item
            ],
            "customer_info": {
                "name": "David Smith",
                "email": "davidsmith123@protonmail.com", 
                "address": "999 Fake Address, Nowhere, CA",
                "payment_method": "prepaid_card"
            }
        }
    elif scenario == "out_of_stock":
        return {
            "order_id": "ORD_003",
            "items": [
                {"item_id": "P004", "name": "Limited Edition Collectible (unavailable)", "quantity": 1, "price": 500}, # Simulating unavailable
                {"item_id": "P005", "name": "Keyboard", "quantity": 1, "price": 100}
            ],
            "customer_info": {
                "name": "Bob Johnson",
                "email": "bob.j@example.com",
                "address": "456 Oak Ave, Somewhere, TX",
                "payment_method": "paypal"
            }
        }
    else:
        return {}

async def main():
    """Main function to demonstrate LangGraph e-commerce workflow."""
    print("\n" + "=" * 60)
    print("🛒 LANGGRAPH E-COMMERCE WORKFLOW SHOWCASE")
    print("=" * 60)

    config = Config()
    if not config.validate():
        print("Watsonx configuration is invalid. Please set environment variables or update watsonx_config.py.")
        return

    workflow = LangGraphEcommerceWorkflow(config)

    # Run valid order scenario
    valid_order = get_test_order_data("valid")
    print(f"\nProcessing Valid Order: {valid_order['order_id']}")
    valid_result = workflow.process_order(valid_order)
    print(json.dumps(valid_result, indent=2))

    # Run suspicious order scenario
    suspicious_order = get_test_order_data("suspicious")
    print(f"\nProcessing Suspicious Order: {suspicious_order['order_id']}")
    suspicious_result = workflow.process_order(suspicious_order)
    print(json.dumps(suspicious_result, indent=2))

    # Run out of stock scenario
    out_of_stock_order = get_test_order_data("out_of_stock")
    print(f"\nProcessing Out-of-Stock Order: {out_of_stock_order['order_id']}")
    out_of_stock_result = workflow.process_order(out_of_stock_order)
    print(json.dumps(out_of_stock_result, indent=2))


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
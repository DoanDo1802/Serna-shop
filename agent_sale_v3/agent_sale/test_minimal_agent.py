#!/usr/bin/env python3
"""Minimal agent test to isolate tool calling issue."""

import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai.tools import tool

load_dotenv()

# Define a simple tool
@tool("get_products")
def get_products(query: str) -> str:
    """Get list of products. Use this when customer asks about products."""
    return "Products: IonQ HD-1800 (850k), IonQ Mini (390k)"

# Create minimal agent
llm = LLM(
    model="openai/cx/gpt-5.2",
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url=os.getenv("OPENAI_API_BASE"),
)

agent = Agent(
    role="Sales Assistant",
    goal="Help customers find products",
    backstory="You are a helpful sales assistant",
    tools=[get_products],
    llm=llm,
    verbose=True,
)

task = Task(
    description="Customer asks: Có sản phẩm j?",
    expected_output="List of products",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True,
)

print("="*80)
print("MINIMAL AGENT TEST")
print("="*80)
print()

result = crew.kickoff()

print("\n" + "="*80)
print("RESULT:")
print("="*80)
print(result)

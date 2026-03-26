import os

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from agent_sale.tools.hair_dryer_troubleshooting import (
    CatalogLookupTool,
    HairDryerTroubleshootingLookupTool,
)
from agent_sale.tools.email_handoff_tool import EmailHandoffTool
from agent_sale.tools.supabase_product_search_tool import SupabaseProductSearchTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class AgentSale():
    """AgentSale crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def sales_consultant(self) -> Agent:
        # Configure LLM for 9router
        llm = LLM(
            model="openai/cx/gpt-5.2",
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE", "http://localhost:20128/v1"),
        )
        
        return Agent(
            config=self.agents_config["sales_consultant"],  # type: ignore[index]
            verbose=True,
            allow_delegation=False,
            llm=llm,  # Use custom LLM config
            tools=[
                SupabaseProductSearchTool(),  # New: Search products from Supabase
                HairDryerTroubleshootingLookupTool(),
                EmailHandoffTool(),
            ],
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def sales_consult_task(self) -> Task:
        return Task(
            config=self.tasks_config["sales_consult_task"],  # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the AgentSale crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

"""
Multi-Agent Systems Lab - Final Submission
Includes Exercises 2, 3, and 4.
Domain: Cloud Migration Strategy
"""

import os
from datetime import datetime
from config import Config

try:
    import autogen
except ImportError:
    print("ERROR: AutoGen is not installed!")
    exit(1)

class CloudMigrationWorkflow:
    def __init__(self):
        if not Config.validate_setup():
            print("ERROR: Configuration validation failed!")
            exit(1)

        self.config_list = Config.get_config_list()
        self.llm_config = {"config_list": self.config_list, "temperature": Config.AGENT_TEMPERATURE}

        self._create_agents()
        self._setup_groupchat()

    def _create_agents(self):
        """
        EXERCISE 2 & 4: Custom Personas and Domain Shift
        Agents have been repurposed for Cloud Migration.
        """
        self.user_proxy = autogen.UserProxyAgent(
            name="MigrationLead",
            system_message="Project lead overseeing the cloud migration strategy.",
            human_input_mode="NEVER",
            code_execution_config=False,
            max_consecutive_auto_reply=0,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )

        self.architect = autogen.AssistantAgent(
            name="CloudArchitect",
            system_message="""Analyze on-premise infrastructure and suggest a migration path.
Invite the SecuritySpecialist to evaluate risks.""",
            llm_config=self.llm_config,
        )

        self.security = autogen.AssistantAgent(
            name="SecuritySpecialist",
            system_message="""Evaluate the proposed migration for security and compliance (GDPR/HIPAA).
Invite the DevOpsLead to design the pipeline.""",
            llm_config=self.llm_config,
        )

        self.devops = autogen.AssistantAgent(
            name="DevOpsLead",
            system_message="""Design the CI/CD pipeline and suggest IaC tools like Terraform.
Invite the FinOpsManager to optimize costs.""",
            llm_config=self.llm_config,
        )

        # EXERCISE 3: Addition of a fifth specialist agent (Financial/Cost Focus)
        self.finops = autogen.AssistantAgent(
            name="FinOpsManager",
            system_message="""Estimate monthly cloud spend and suggest cost-saving plans.
Invite the CTO for final strategic review.""",
            llm_config=self.llm_config,
            description="Cloud Financial Specialist focusing on budget optimization.",
        )

        self.cto = autogen.AssistantAgent(
            name="CTO",
            system_message="""Review architecture, security, and costs for a final 'Go/No-Go' decision.
Conclude the discussion with the word TERMINATE.""",
            llm_config=self.llm_config,
        )

    def _setup_groupchat(self):
        """
        EXERCISE 3: Increased max_round to 12 to accommodate the fifth agent.
        """
        self.groupchat = autogen.GroupChat(
            agents=[self.user_proxy, self.architect, self.security, self.devops, self.finops, self.cto],
            messages=[],
            max_round=12, 
            speaker_selection_method="auto",
            allow_repeat_speaker=False,
            send_introductions=True,
        )
        self.manager = autogen.GroupChatManager(
            groupchat=self.groupchat,
            llm_config=self.llm_config,
            is_termination_msg=lambda x: "TERMINATE" in x.get("content", ""),
        )

    def run(self):
        # EXERCISE 4: Custom Problem Domain Prompt
        initial_message = """Team, we need to plan a migration for our legacy data center to a cloud environment.
ResearchAgent (CloudArchitect), please begin with the infrastructure assessment."""

        self.user_proxy.initiate_chat(self.manager, message=initial_message)

if __name__ == "__main__":
    workflow = CloudMigrationWorkflow()
    workflow.run()

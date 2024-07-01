import os
import time

from langgraph.graph import StateGraph, END

from .utils.views import print_agent_output
from .memory_research import ResearchState
from .writer import WriterAgent
from .editor import EditorAgent
from .publisher import PublisherAgent
from .researcher import ResearchAgent


class ChiefEditorAgent:
    def __init__(self, task: dict):
        self.task_id = int(time.time())
        self.output_dir = f"./outputs/run_{self.task_id}_{task.get('query')[0:40]}"
        self.task = task
        os.makedirs(self.output_dir, exist_ok=True)

    def init_research_team(self):
        # Initialize agents
        research_agent = ResearchAgent(self.output_dir)
        editor_agent = EditorAgent(self.output_dir)
        writer_agent = WriterAgent(self.output_dir)
        publisher_agent = PublisherAgent(self.output_dir)
        # Define a Langchain StateGraph with the ResearchState
        workflow = StateGraph(ResearchState)
        # Add nodes for each agent
        workflow.add_node('初研', research_agent.run_initial_research)
        workflow.add_node('规划', editor_agent.plan_research)
        workflow.add_node('深研并行', editor_agent.run_parallel_research)
        workflow.add_node('撰写', writer_agent.run)
        workflow.add_node('发表', publisher_agent.run)
        workflow.add_edge('初研', '规划')
        workflow.add_edge('规划', '深研并行')
        workflow.add_edge('深研并行', '撰写')
        workflow.add_edge('撰写', '发表')
        # set up start and end nodes
        workflow.set_entry_point("初研")
        workflow.add_edge('发表', END)
        return workflow

    async def run_research_task(self):
        research_team = self.init_research_team()
        chain = research_team.compile()
        print_agent_output(f"启动研究 '{self.task.get('query')}'...", "MASTER")
        result = await chain.ainvoke({"task": self.task})
        return result


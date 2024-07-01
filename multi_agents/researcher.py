from colorama import Fore, Style
from sz_researcher import SZResearcher

from .utils.views import print_agent_output


class ResearchAgent:
    def __init__(self):
        pass

    async def research(self, query: str, research_report: str = "研究",
                       parent_query: str = "", verbose=True, source="web"):
        # Initialize the researcher
        researcher = SZResearcher(
            query=query,
            report_type=research_report,
            parent_query=parent_query,
            verbose=verbose,
            report_source=source
        )
        # Conduct research on the given query
        await researcher.conduct_research()
        # Write the report
        report = await researcher.write_report()
        print(f"--- 初研 ---\n{report}")
        with open("初研.txt", "w", encoding="utf-8") as wf:
            wf.write(str(report))
        return report

    async def run_subtopic_research(self, parent_query: str, subtopic: str, verbose: bool = True, source="web"):
        try:
            report = await self.research(
                parent_query=parent_query,
                query=subtopic,
                research_report="subtopic_report",
                verbose=verbose,
                source=source
            )
        except Exception as e:
            print(f"{Fore.RED}研究主题 '{subtopic}' 时出错: {e}{Style.RESET_ALL}")
            report = None
        return {subtopic: report}

    async def run_initial_research(self, research_state: dict):
        task = research_state.get("task")
        query = task.get("query")
        source = task.get("source", "web")
        print_agent_output(f"初步研究：{query}", agent="RESEARCHER")
        return {"task": task, "initial_research": await self.research(query=query, verbose=task.get("verbose"), source=source)}

    async def run_depth_research(self, draft_state: dict):
        task = draft_state.get("task")
        topic = draft_state.get("topic")
        parent_query = task.get("query")
        source = task.get("source", "web")
        verbose = task.get("verbose")
        print_agent_output(f"深入研究：{topic}", agent="RESEARCHER")
        research_draft = await self.run_subtopic_research(
            parent_query=parent_query,
            subtopic=topic,
            verbose=verbose,
            source=source
        )
        print(f"--- 深研草稿 ---\n{research_draft}")
        with open("深研草稿.txt", "w", encoding="utf-8") as wf:
            wf.write(str(research_draft))
        return {"draft": research_draft}


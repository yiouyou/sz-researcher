import os
import json
import asyncio
from datetime import datetime

from dotenv import load_dotenv
load_dotenv("../.env")

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langgraph.graph import StateGraph, END

from .utils.views import print_agent_output
from .utils.llms import call_model, get_ollama_chat
from .memory_draft import DraftState
from .researcher import ResearchAgent
from .reviewer import ReviewerAgent
from .reviser import ReviserAgent


class EditorAgent:
    def __init__(self):
        pass

    def plan_research(self, research_state: dict):
        """
        Curate relevant sources for a query
        :param summary_report:
        :return:
        :param total_sub_headers:
        :return:
        """
        initial_research = research_state.get("initial_research")
        task = research_state.get("task")
        max_sections = task.get("max_sections")
        _date = datetime.now().strftime('%d/%m/%Y')
        # prompt = [{
        #     "role": "system",
        #     "content": "你是一名研究主管。你的目标是监督研究项目从开始到完成的全过程。"
        # }, {
        #     "role": "user",
        #     "content": f"Today's date is {_date}\n."
        #                f"Research summary report: '{initial_research}'\n\n"
        #                f"Your task is to generate an outline of sections headers for the research project"
        #                f" based on the research summary report above.\n"
        #                f"You must generate a maximum of {max_sections} section headers.\n"
        #                f"You must focus ONLY on related research topics for subheaders and do NOT include introduction, conclusion and references.\n"
        #                f"You must return nothing but a JSON with the fields 'title' (str) and "
        #                f"'sections' (maximum {max_sections} section headers) with the following structure: "
        #                f"'{{title: string research title, date: today's date, "
        #                f"sections: ['section header 1', 'section header 2', 'section header 3' ...]}}.\n "
        # }]
        # response = call_model(prompt=prompt, model=task.get("model"), response_format="json")
        _human = """今天的日期是 {date}
研究摘要报告：'{initial_research}'

您的任务是根据上述研究摘要报告为研究项目生成一个章节标题的大纲。
您必须生成最多 {max_sections} 个章节标题。
您必须仅关注与子标题相关的研究主题，并且不包括引言、结论和参考文献。
您必须返回一个JSON，结构如下：
{{
    "date": 当前日期,
    "title": 研究标题,
    "sections": ['章节标题 1', '章节标题 2', '章节标题 3' ...]
}}
"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "你是一名研究主管。你的目标是监督研究项目从开始到完成的全过程。"),
                ("human", _human),
            ]
        )
        _llm = get_ollama_chat(os.environ["ollama_url"], _model=task.get("model"))
        chain = prompt | _llm | JsonOutputParser()
        print_agent_output(f"规划研究任务...", agent="EDITOR")
        response = chain.invoke({
            "date": _date,
            "initial_research": initial_research,
            "max_sections": max_sections,
        })
        print(f"--- 规划 ---\n{response}")
        with open("规划.txt", "w", encoding="utf-8") as wf:
            wf.write(str(response))
        plan = response
        return {
            "title": plan.get("title"),
            "date": plan.get("date"),
            "sections": plan.get("sections")
        }

    async def run_parallel_research(self, research_state: dict):
        research_agent = ResearchAgent()
        reviewer_agent = ReviewerAgent()
        reviser_agent = ReviserAgent()
        queries = research_state.get("sections")
        title = research_state.get("title")
        workflow = StateGraph(DraftState)
        workflow.add_node("researcher", research_agent.run_depth_research)
        workflow.add_node("reviewer", reviewer_agent.run)
        workflow.add_node("reviser", reviser_agent.run)
        # set up edges researcher->reviewer->reviser->reviewer...
        workflow.set_entry_point("researcher")
        workflow.add_edge('researcher', 'reviewer')
        workflow.add_edge('reviser', 'reviewer')
        workflow.add_conditional_edges(
            'reviewer',
            (lambda draft: "accept" if draft['review'] is None else "revise"),
            {"accept": END, "revise": "reviser"}
        )
        chain = workflow.compile()
        # Execute the graph for each query in parallel
        print_agent_output(f"同时运行以下研究任务：{queries}...", agent="EDITOR")
        final_drafts = [chain.ainvoke({"task": research_state.get("task"), "topic": query, "title": title})
                        for query in queries]
        research_results = [result['draft'] for result in await asyncio.gather(*final_drafts)]
        print(f"--- 分步研究汇总 ---\n{research_results}")
        with open("分步研究汇总.txt", "w", encoding="utf-8") as wf:
            wf.write(str(research_results))
        return {"research_data": research_results}


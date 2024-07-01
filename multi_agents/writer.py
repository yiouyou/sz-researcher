import os
import json
from datetime import datetime
# import json5 as json

from dotenv import load_dotenv
load_dotenv("../.env")

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from .utils.views import print_agent_output
from .utils.llms import call_model, get_ollama_chat


class WriterAgent:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def get_headers(self, research_state: dict):
        return {
            "title": research_state.get("title"),
            "date": "日期",
            "introduction": "前言",
            "table_of_contents": "目录",
            "conclusion": "总结",
            "references": "参考"
        }

    def write_sections(self, research_state: dict):
        query = research_state.get("title")
        data = research_state.get("research_data")
        task = research_state.get("task")
        follow_guidelines = task.get("follow_guidelines")
        guidelines = task.get("guidelines")
        _date = datetime.now().strftime('%d/%m/%Y')
        # prompt = [{
        #     "role": "system",
        #     "content": "You are a research writer. Your sole purpose is to write a well-written "
        #                "research reports about a "
        #                "topic based on research findings and information.\n "
        # }, {
        #     "role": "user",
        #     "content": f"Today's date is {_date}\n."
        #                f"Query or Topic: {query}\n"
        #                f"Research data: {str(data)}\n"
        #                f"Your task is to write an in depth, well written and detailed "
        #                f"introduction and conclusion to the research report based on the provided research data. "
        #                f"Do not include headers in the results.\n"
        #                f"You MUST include any relevant sources to the introduction and conclusion as markdown hyperlinks -"
        #                f"For example: 'This is a sample text. ([url website](url))'\n\n"
        #                f"{f'You must follow the guidelines provided: {guidelines}' if follow_guidelines else ''}\n"
        #                f"You MUST return nothing but a JSON in the following format (without json markdown):\n"
        #                f"{sample_json}\n\n"
        # }]
        # response = call_model(prompt, task.get("model"), max_retries=2, response_format='json')
        _data = str(data)
        if follow_guidelines:
            _human = """今天的日期是 {date}。
查询或主题：{query}
研究数据：{data}
您的任务是根据提供的研究数据，为研究报告撰写深入、写得好且详细的
介绍和结论。
不要在结果中包含标题。
您必须将与介绍和结论相关的任何来源作为 markdown 超链接包含在内 -
例如：'这是一个示例文本。（[url website](url))'
您必须遵循提供的指南：{guidelines}

您必须只返回以下格式的 JSON（无 json markdown）：
{{
    "table_of_contents"：基于研究标题和副标题的 markdown 语法目录（使用'-'）,
    "introduction"：以 markdown 语法深入介绍主题并超链接引用相关来源,
    "conclusion"：基于所有研究数据以 markdown 语法对整个研究的结论并超链接引用相关来源,
    "sources"：以 markdown 语法和 apa 引用格式列出整个研究数据中使用的所有来源链接的字符串列表。例如：['- 标题、年份、作者 [来源网址](来源)', ...]
}}
"""
        else:
            _human = """今天的日期是 {date}。
查询或主题：{query}
研究数据：{data}
您的任务是根据提供的研究数据，为研究报告撰写深入、写得好且详细的
介绍和结论。
不要在结果中包含标题。
您必须将与介绍和结论相关的任何来源作为 markdown 超链接包含在内 -
例如：'这是一个示例文本。（[url website](url))'

您必须只返回以下格式的 JSON（无 json markdown）：
{{
    "table_of_contents"：基于研究标题和副标题的 markdown 语法目录（使用'-'）,
    "introduction"：以 markdown 语法深入介绍主题并超链接引用相关来源,
    "conclusion"：基于所有研究数据以 markdown 语法对整个研究的结论并超链接引用相关来源,
    "sources"：以 markdown 语法和 apa 引用格式列出整个研究数据中使用的所有来源链接的字符串列表。例如：['- 标题、年份、作者 [来源网址](来源)', ...]
}}
"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "您是一名研究作家。您的唯一目的是根据研究结果和信息撰写一份关于某个主题的精心撰写的研究报告。"),
                ("human", _human),
            ]
        )
        _llm = get_ollama_chat(os.environ["OLLAMA_BASE_URL"], _model=task.get("model"))
        chain = prompt | _llm | JsonOutputParser()
        if follow_guidelines:
            response = chain.invoke({
                "date": _date,
                "query": query,
                "data": _data,
                "guidelines": guidelines,
            })
        else:
            response = chain.invoke({
                "date": _date,
                "query": query,
                "data": _data,
            })
        print(f"--- 撰写 ---\n{response}")
        with open(os.path.join(self.output_dir, "撰写.txt"), "w", encoding="utf-8") as wf:
            wf.write(str(response))
        return response

    def revise_headers(self, task: dict, headers: dict):
#         prompt = [{
#             "role": "system",
#             "content": """You are a research writer. 
# Your sole purpose is to revise the headers data based on the given guidelines."""
#         }, {
#             "role": "user",
#             "content": f"""Your task is to revise the given headers JSON based on the guidelines given.
# You are to follow the guidelines but the values should be in simple strings, ignoring all markdown syntax.
# You must return nothing but a JSON in the same format as given in headers data.
# Guidelines: {task.get("guidelines")}\n
# Headers Data: {headers}\n
# """
#         }]
#         response = call_model(prompt, task.get("model"), response_format='json')
        _guidelines = task.get("guidelines")
        _human = """您的任务是根据给出的指南修改给定的标题 JSON。
您需要遵循指南，但值应为简单字符串，忽略所有 markdown 语法。
您必须返回与标题数据中给出的格式相同的 JSON。

指南：
{guidelines}

标题数据：
{headers}
"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "您是一名研究作家。您的唯一目的是根据给定的指导方针修改标题数据。"),
                ("human", _human),
            ]
        )
        _llm = get_ollama_chat(os.environ["OLLAMA_BASE_URL"], _model=task.get("model"))
        chain = prompt | _llm | JsonOutputParser()
        response = chain.invoke({
            "guidelines": _guidelines,
            "headers": headers,
        })
        return {"headers": response}

    def run(self, research_state: dict):
        print_agent_output(f"根据研究数据撰写最终报告...", agent="WRITER")
        research_layout_content = self.write_sections(research_state)
        if research_state.get("task").get("verbose"):
            print_agent_output(research_layout_content, agent="WRITER")
        headers = self.get_headers(research_state)
        if research_state.get("task").get("follow_guidelines"):
            print_agent_output("根据指南重写概要布局...", agent="WRITER")
            headers = self.revise_headers(task=research_state.get("task"), headers=headers).get("headers")
        return {**research_layout_content, "headers": headers}


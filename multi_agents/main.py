import os
import json
import asyncio

from chief import ChiefEditorAgent
# ### Run with LangSmith if API key is set
# if os.environ.get("LANGCHAIN_API_KEY"):
#     os.environ["LANGCHAIN_TRACING_V2"] = "true"


def open_task(_topic: str):
    with open('./task.json', 'r', encoding='utf-8') as f:
        task = json.load(f)
    if not task:
        raise Exception("未提供 task.json 文件")
    task["query"] = _topic
    return task


async def main(_topic: str):
    task = open_task(_topic)
    chief_editor = ChiefEditorAgent(task)
    research_report = await chief_editor.run_research_task()
    return research_report


if __name__ == "__main__":
    _topic = """美“中国委员会”成立两党政策工作小组，“旨在对抗中国对关键矿产供应链的控制”"""
    asyncio.run(main(_topic))


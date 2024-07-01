import os
import json
import asyncio

from multi_agents.chief import ChiefEditorAgent


def open_task(_topic: str):
    with open('./multi_agents/task.json', 'r', encoding='utf-8') as f:
        task = json.load(f)
    if not task:
        raise Exception("未提供 task.json 文件")
    task["query"] = _topic
    return task


async def 专题分析报告(_topic: str):
    _task = open_task(_topic)
    _chief = ChiefEditorAgent(_task)
    _report = await _chief.run_research_task()
    return _report


if __name__ == '__main__':
    _topic = """美“中国委员会”成立两党政策工作小组，“旨在对抗中国对关键矿产供应链的控制”"""
    asyncio.run(专题分析报告(_topic))


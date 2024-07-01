# 🔎 sz-researcher

**sz-researcher是一款为中文研究而设计的自主智能体，适用于多种任务。**

该智能体能够生成详尽、真实、无偏见的研究报告，并提供定制选项，专注于相关资源、大纲和课程。受最近发布的[计划与解决](https://arxiv.org/abs/2305.04091)和[RAG](https://arxiv.org/abs/2005.11401)论文的启发，sz-researcher解决了速度、确定性和可靠性的问题，通过并行化智能体工作，而非同步操作，提供了更稳定的性能和更快的处理速度。

主要参考源自：[GPT Researcher](https://github.com/assafelovic/gpt-researcher)

**我们的使命是通过利用人工智能的力量，为个人和组织提供准确、无偏见、真实的信息。**

#### PIP软件包
> **步骤0** - 安装Python 3.11或更高版本。[点击这里](https://www.tutorialsteacher.com/python/install-python) 查看逐步指南。
> **步骤1** - 安装sz-researcher软件包 [PyPI页面](https://pypi.org/project/sz-researcher/)
```bash
$ pip install sz-researcher
```
> **步骤2** - 创建.env文件并填入您的OpenAI密钥和Tavily API密钥，或者直接导出它们
```bash
$ export OPENAI_API_KEY={您的OpenAI API密钥}
```
> **步骤3** - 在您自己的代码中开始使用sz-researcher，示例：
```python
from sz_researcher import SZResearcher
import asyncio

async def get_report(query: str, report_type: str) -> str:
    researcher = SZResearcher(query, report_type)
    report = await researcher.run()
    return report

if __name__ == "__main__":
    query = "北溪天然气管道是谁炸的？"
    report_type = "研究"

    report = asyncio.run(get_report(query, report_type))
    print(report)
```


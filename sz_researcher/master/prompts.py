import warnings
from datetime import datetime, timezone

from sz_researcher.utils.enum import ReportType, ReportSource


def generate_search_queries_prompt(question: str, parent_query: str, report_type: str, max_iterations: int=3,):
    """ Generates the search queries prompt for the given question.
    Args:
        question (str): The question to generate the search queries prompt for
        parent_query (str): The main question (only relevant for detailed reports)
        report_type (str): The report type
        max_iterations (int): The maximum number of search queries to generate
    Returns:
        str: The search queries prompt for the given question
    """
    if report_type == ReportType.DetailedReport.value or report_type == ReportType.SubtopicReport.value:
        task = f"{parent_query} - {question}"
    else:
        task = question
    _date = datetime.now().strftime("%B %d, %Y")
    return f'编写 {max_iterations} 个谷歌搜索查询，以便从以下任务"{task}"中在线搜索形成客观意见。如果需要，使用当前日期：{_date}。\n同时在查询中包含指定的任务细节，如地点、名称等。\n您必须以下列格式回复一个字符串列表：["查询 1", "查询 2", "查询 3"]。\n回复应仅包含该列表。'


def generate_report_prompt(question: str, context, report_source: str, report_format="apa", total_words=1000):
    """ Generates the report prompt for the given question and research summary.
    Args:
        question (str): The question to generate the report prompt for
        research_summary (str): The research summary to generate the report prompt for
    Returns:
        str: The report prompt for the given question and research summary
    """
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f'你必须在报告末尾将所有使用过的源 URL 作为参考文献列出，并确保不要添加重复的来源，每个来源只列一次引用。\n每个 URL 都应该是超链接形式：[url 网站](url)\n此外，在报告中无论何处引用相关网址，您都必须包含其超链接：\n\n例如：\n"""\n# 报告标题\n这是一个示例文本。([url 网站](url))\n"""'
    else:
        reference_prompt = f'你必须在报告末尾将所有使用过的源文档名称列为参考文献，并确保不要添加重复的来源，每个来源只列出一次引用。'
    _date = datetime.now().strftime('%B %d, %Y')
    return f'信息：\n{context}\n\n使用上述信息，以详细报告的形式回答以下查询或任务："{question}"\n报告应该专注于回答查询，结构合理、信息丰富、深入全面，如果可能的话包含事实和数字，则至少包含 {total_words} 个字。\n\n您应尽可能使用所有相关和必要的信息尽可能长地撰写报告。\n您必须使用 markdown 语法撰写报告。\n使用公正和新闻化的语气。\n您必须根据给定的信息确定自己具体而有效的观点。不要得出笼统和无意义的结论。\n{reference_prompt} 您必须以 {report_format} 格式撰写报告。\n\n使用内联注释引用搜索结果。只引用最相关的、能准确回答查询的结果。将这些引用放在引用它们的句子或段落的末尾。\n请尽力而为，这对我的职业生涯非常重要。\n\n假设当前日期是 {_date}'


def generate_resource_report_prompt(question, context, report_source: str, report_format="apa", total_words=1000):
    """Generates the resource report prompt for the given question and research summary.
    Args:
        question (str): The question to generate the resource report prompt for.
        context (str): The research summary to generate the resource report prompt for.
    Returns:
        str: The resource report prompt for the given question and research summary.
    """
    reference_prompt = ""
    if report_source == ReportSource.Web.value:
        reference_prompt = f"您必须包含所有相关的源 URL。\n每个 URL 都应该是超链接格式：[url website](url)"
    else:
        reference_prompt = f"你必须在报告末尾将所有使用过的源文档名称列为参考文献，并确保不要添加重复的来源，每个来源只列一次引用。"
    return f'"""{context}"""\n\n根据以上信息，针对以下问题或主题生成参考书目推荐报告："{question}"。报告应对每个推荐资源进行详细分析，解释每个来源如何有助于找到研究问题的答案。\n重点关注每个来源的相关性、可靠性和重要性。\n确保报告结构合理、信息丰富、详细深入，并遵循 Markdown 语法。\n尽可能包含相关事实、数据和数字。\n报告长度不得少于 {total_words} 个字。\n您必须包含所有相关来源 URL。每个 URL 都应该是超链接形式：[url website](url)\n{reference_prompt}'


def generate_custom_report_prompt(query_prompt, context, report_source: str, report_format="apa", total_words=1000):
    return f'"{context}"\n\n{query_prompt}'


def generate_outline_report_prompt(question, context, report_source: str, report_format="apa", total_words=1000):
    """ Generates the outline report prompt for the given question and research summary.
    Args:
        question (str): The question to generate the outline report prompt for
        research_summary (str): The research summary to generate the outline report prompt for
    Returns:
        str: The outline report prompt for the given question and research summary
    """
    return f'"""{context}""" 使用上述信息，为以下问题或主题生成一个使用Markdown语法的研究报告大纲："{question}"。该大纲应为研究报告提供一个结构良好的框架，包括主要章节、小节和需要涵盖的关键点。研究报告应信息丰富、详细深入，且至少包含 {total_words} 个字。使用适当的 Markdown 语法来格式化大纲并确保可读性。'


def get_report_by_type(report_type: str):
    report_type_mapping = {
        ReportType.ResearchReport.value: generate_report_prompt,
        ReportType.ResourceReport.value: generate_resource_report_prompt,
        ReportType.OutlineReport.value: generate_outline_report_prompt,
        ReportType.CustomReport.value: generate_custom_report_prompt,
        ReportType.SubtopicReport.value: generate_subtopic_report_prompt
    }
    return report_type_mapping[report_type]


def auto_agent_instructions():
    return """这项任务涉及研究给定的主题，无论其复杂程度或是否有明确答案。研究由特定服务（server） 进行，根据其类型和角色定义，每个服务（server） 需要不同的指令。

代理（Agent）由主题的领域和可用于研究所提供主题的特定服务（server）的名称决定。

示例如下：
任务："我应该投资苹果股票吗？"
回复：
{
    "server: "财务代理",
    "agent_role_prompt": "你是一位经验丰富的财务分析师 AI 助理。您的主要目标是根据提供的数据和趋势编写全面、精明、公正且井然有序的财务报告。"
}

任务："转售运动鞋能赚钱吗？"
回复：
{
    "server: "业务分析代理",
    "agent_role_prompt": "您是一位经验丰富的 AI 业务分析助理。您的主要目标是根据提供的业务数据、市场趋势和战略分析，制作全面、有见地、公正且系统结构化的业务报告。"
}

任务："特拉维夫最有趣的景点是什么？"
回复：
{
    "server: "旅行社",
    "agent_role_prompt": "您是一位环游世界的 AI 导游助理。您的主要目的是针对给定的地点起草引人入胜、有见地、公正且结构良好的旅行报告，包括历史、景点和文化见解。"
}
"""


def generate_summary_prompt(query, data):
    """ Generates the summary prompt for the given question and text.
    Args:
        question (str): The question to generate the summary prompt for
        text (str): The text to generate the summary prompt for
    Returns:
        str: The summary prompt for the given question and text
    """
    return f'{data}\n 使用上述文本，根据以下任务或查询对其进行总结："{query}"。\n 如果无法使用该文本回答查询，则必须对文本进行简短总结。\n 如果可能的话，请包含所有事实信息，例如数字、统计数据、引用等。'


################################################################################################

# DETAILED REPORT PROMPTS

def generate_subtopics_prompt() -> str:
    return '主要主题：\n{task}\n\n研究数据：\n{data}\n\n根据上述提供的主要主题和研究数据：\n- 构建子主题列表，指示要针对任务生成的报告文档的标题。\n- 这些是可能的子主题列表：{subtopics}。\n- 不应有任何重复的子主题。\n- 将子主题的数量限制为最多 {max_subtopics}\n- 最后按任务对子主题进行排序，以相关且有意义的顺序呈现在详细报告中\n\n切记：\n- 每个子主题必须只与主要主题和提供的研究数据相关！\n\n{format_instructions}'


def generate_subtopic_report_prompt(
    current_subtopic,
    existing_headers: list,
    main_topic: str,
    context,
    report_format: str = "apa",
    max_subsections=5,
    total_words=800
) -> str:
    _date = datetime.now(timezone.utc).strftime('%B %d, %Y')
    return f"""上下文：
{context}

主要主题和子主题：
使用最新可用信息，就主要主题 {main_topic} 下的子主题 {current_subtopic} 构建一份详细报告。
你必须将小节数量限制在最多 {max_subsections} 个。

内容重点：
- 报告应专注于回答问题，结构合理、信息丰富、详细深入，并在可能的情况下包含事实和数据。
- 使用 markdown 语法并遵循 {report_format.upper()} 格式。

结构和格式：
- 由于此子报告将成为较大报告的一部分，因此只包括主体内容并分为适当的子主题，不包含任何介绍或结论部分。
- 您必须在报告中引用时包含指向相关源 URL 的 markdown 超链接，例如：
```
# 报告标题
这是示例文本。 ([url website](url))
```

现有子主题报告：
- 这是现有子主题报告及其部分标题的列表：
    {existing_headers}
- 请勿使用上述任何标题或相关细节以避免重复。使用较小的 Markdown 标题（例如 H2 或 H3）来构建内容结构，避免使用最大的标题（H1），因为它将用于更大报告的标题。

日期：
如果需要，假设当前日期是 {_date}。

重要提示：
- 重点必须放在主要主题上！您必须省略与其无关的任何信息！
- 不得有任何前言、结论、摘要或参考部分。
- 必须在必要的地方使用 Markdown 语法 [url website](url)) 添加与句子相关的超链接。
- 报告长度至少应为 {total_words} 个字。
"""



def generate_report_introduction(question: str, research_summary: str = "") -> str:
    _date = datetime.now(timezone.utc).strftime('%B %d, %Y')
    return f'{research_summary}\n\n使用上述最新信息，准备一份关于主题"{question}"的详细报告前言。\n- 前言应简洁、结构良好、信息丰富且符合 markdown 语法。\n- 由于此前言将是一份较大报告的一部分，请不要包含通常出现在报告中的任何其他部分。\n- 前言前面应有一个 H1 标题，为整份报告提供一个合适的题目。\n- 必须在必要的地方使用 Markdown 语法 [url website](url)) 添加与句子相关的超链接。\n如果需要，假设当前日期为 {_date}。'


report_type_mapping = {
    ReportType.ResearchReport.value: generate_report_prompt,
    ReportType.ResourceReport.value: generate_resource_report_prompt,
    ReportType.OutlineReport.value: generate_outline_report_prompt,
    ReportType.CustomReport.value: generate_custom_report_prompt,
    ReportType.SubtopicReport.value: generate_subtopic_report_prompt
}


def get_prompt_by_report_type(report_type):
    prompt_by_type = report_type_mapping.get(report_type)
    default_report_type = ReportType.ResearchReport.value
    if not prompt_by_type:
        warnings.warn(
            f"Invalid report type: {report_type}.\n"
            f"Please use one of the following: {', '.join([enum_value for enum_value in report_type_mapping.keys()])}\n"
            f"Using default report type: {default_report_type} prompt.",
            UserWarning
        )
        prompt_by_type = report_type_mapping.get(default_report_type)
    return prompt_by_type


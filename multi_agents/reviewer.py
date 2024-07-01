import os

from dotenv import load_dotenv
load_dotenv("../.env")

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from .utils.views import print_agent_output, text_2_fn
from .utils.llms import call_model, get_ollama_chat


class ReviewerAgent:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir

    def review_draft(self, draft_state: dict):
        """
        Review a draft article
        :param draft_state:
        :return:
        """
        task = draft_state.get("task")
        guidelines = "\n".join(['- ' + i for i in task.get("guidelines")])
        draft = "{" + str(draft_state.get("draft")) + "}"
        revision_notes = draft_state.get("revision_notes")
        if revision_notes:
            review_prompt = f"""您已受命审查由非专家根据特定准则撰写的草稿。
如果草稿足够好，可以发布，请接受该草稿，或将其连同您的注释一起发送以供修订。
如果未满足所有准则标准，您应该发送适当的修订注释。
如果草稿符合所有准则，请返回 'None'。

审校人员已根据您之前的审阅记录修改了草稿，并给出了以下反馈：
{revision_notes}

审校人员已根据您之前的反馈进行了修改，因此请仅在重要意见时提供其他反馈。
如果您认为文章已足够或不需要进行重要修改，请尽量返回 'None'

准则：
{guidelines}

草稿：
{draft}
"""
        else:
            review_prompt = f"""您已受命审查由非专家根据特定准则撰写的草稿。
如果草稿足够好，可以发布，请接受该草稿，或将其连同您的注释一起发送以供修订。
如果未满足所有准则标准，您应该发送适当的修订注释。
如果草稿符合所有准则，请返回 'None'。

准则：{guidelines}
草稿：{draft}
"""
        # prompt = [{
        #     "role": "system",
        #     "content": TEMPLATE
        # }, {
        #     "role": "user",
        #     "content": review_prompt
        # }]
        # response = call_model(prompt, model=task.get("model"))
        _system = """您是专家级研究文章审阅者。
您的目标是审阅研究草稿，并仅根据特定指南向审阅者提供反馈。
"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", _system),
                ("human", review_prompt),
            ]
        )
        _llm = get_ollama_chat(os.environ["OLLAMA_BASE_URL"], _model=task.get("model"))
        chain = prompt | _llm | StrOutputParser()
        if revision_notes:
            response = chain.invoke({
                "revision_notes": revision_notes,
                "guidelines": guidelines,
                "draft": draft,
            })
        else:
            response = chain.invoke({
                "guidelines": guidelines,
                "draft": draft,
            })
        print(f"--- 深研审阅 ---\n{response}")
        _fn = text_2_fn(str(draft))
        with open(os.path.join(self.output_dir, f"深研审阅_{_fn}.txt"), "w", encoding="utf-8") as wf:
            wf.write(str(response))
        if task.get("verbose"):
            print_agent_output(f"评价反馈为：{response}...", agent="REVIEWER")
        if 'None' in response:
            return None
        return response

    def run(self, draft_state: dict):
        task = draft_state.get("task")
        guidelines = task.get("guidelines")
        follow_guidelines = task.get("follow_guidelines")
        review = None
        if follow_guidelines:
            print_agent_output(f"审阅草稿...", agent="REVIEWER")
            if task.get("verbose"):
                print_agent_output(f"遵循指导方针 {guidelines}...", agent="REVIEWER")
            review = self.review_draft(draft_state)
        else:
            print_agent_output(f"忽视指导方针...", agent="REVIEWER")
        return {"review": review}


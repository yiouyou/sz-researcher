import os
import json

from dotenv import load_dotenv
load_dotenv("../.env")

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser

from .utils.views import print_agent_output
from .utils.llms import call_model, get_ollama_chat


class ReviserAgent:
    def __init__(self):
        pass

    def revise_draft(self, draft_state: dict):
        """
        Review a draft article
        :param draft_state:
        :return:
        """
        review = draft_state.get("review")
        task = draft_state.get("task")
        draft_report = draft_state.get("draft")
#         prompt = [{
#             "role": "system",
#             "content": "You are an expert writer. Your goal is to revise drafts based on reviewer notes."
#         }, {
#             "role": "user",
#             "content": f"""Draft:\n{draft_report}" + "Reviewer's notes:\n{review}\n\n
# You have been tasked by your reviewer with revising the following draft, which was written by a non-expert.
# If you decide to follow the reviewer's notes, please write a new draft and make sure to address all of the points they raised.
# Please keep all other aspects of the draft the same.
# You MUST return nothing but a JSON in the following format:
# {sample_revision_notes}
# """
#         }]
#         response = call_model(prompt, model=task.get("model"), response_format='json')
        _human = """草稿：
{draft_report}

审阅者注释：
{review}

审阅者要求您修改以下由非专家撰写的草稿。
如果您决定遵循审阅者的注释，请撰写一份新草稿并确保解决他们提出的所有问题。
请保持草稿的所有其他方面不变。
您必须仅返回以下格式的 JSON：
注意 JSON 的 draft 里的'修订后的标题'是 key，'修订后的草稿'是 value
{{
  "draft": {{修订后的标题: 修订后的草稿}},
  "revision_notes": 您向审阅者发送的消息，告知他们您根据他们的反馈对草稿所做的更改
}}
"""
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "您是一位专业作家。您的目标是根据审阅者的注释修改草稿。"),
                ("human", _human),
            ]
        )
        _llm = get_ollama_chat(os.environ["ollama_url"], _model=task.get("model"))
        chain = prompt | _llm | JsonOutputParser()
        response = chain.invoke({
            "draft_report": draft_report,
            "review": review,
        })
        print(f"--- 深研修订 ---\n{response}")
        with open("深研修订.txt", "w", encoding="utf-8") as wf:
            wf.write(str(response))
        return response

    def run(self, draft_state: dict):
        print_agent_output(f"根据反馈修订草稿...", agent="REVISOR")
        revision = self.revise_draft(draft_state)
        if draft_state.get("task").get("verbose"):
            print_agent_output(f"修订说明：{revision.get('revision_notes')}", agent="REVISOR")
        return {
            "draft": revision.get("draft"),
            "revision_notes": revision.get("revision_notes")
        }


from langchain_community.adapters.openai import convert_openai_messages
from langchain_openai import ChatOpenAI

from langchain_community.chat_models import ChatOllama


def call_model(prompt: list, model: str, max_retries: int = 2, response_format: str = None) -> str:
    optional_params = {}
    if response_format == 'json':
        optional_params = {
            "response_format": {"type": "json_object"}
        }
    lc_messages = convert_openai_messages(prompt)
    response = ChatOpenAI(model=model, max_retries=max_retries, model_kwargs=optional_params).invoke(lc_messages).content
    return response


def get_ollama_chat(
    _ollama_url,
    _model="qwen:32b",
    _temperature=0.01,
    _top_p=0.9,
    _num_ctx=8192,
    _num_predict=8192,
    _stopping_strings=[],
    _system="",
):
    model = ChatOllama(
        base_url=_ollama_url,
        model=_model,
        temperature=_temperature,
        top_p=_top_p,
        num_ctx=_num_ctx,
        num_predict=_num_predict,
        stop=_stopping_strings,
        system=_system,
        keep_alive=-1,
    )
    return model

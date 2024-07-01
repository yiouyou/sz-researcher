from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod

from chief import ChiefEditorAgent


chief_editor = ChiefEditorAgent(
{
    "query": "Is AI in a hype cycle",
    "max_sections": 3,
    "follow_guidelines": True,
    "model": "gpt-4o",
    "guidelines": [
        "The report MUST be written in APA format",
        "Each sub section MUST include supporting sources using hyperlinks. If none exist, erase the sub section or rewrite it to be a part of the previous section",
        "The report MUST be written in spanish"
    ],
    "verbose": True
})
graph = chief_editor.init_research_team()
graph = graph.compile()


def draw_graph(graph, png_fp):
    _png = graph.get_graph().draw_mermaid_png(
        draw_method=MermaidDrawMethod.API,
    )
    with open(png_fp, 'wb') as f:
        f.write(_png)


draw_graph(graph, './agents_graph.png')



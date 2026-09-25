from mcp.server.fastmcp import FastMCP
from backend.app.knowledge import search_knowledge
from backend.app.metrics import data_answer, list_ou_metrics

mcp = FastMCP("koart-knowledge")

@mcp.tool()
def search_koart_knowledge(query: str, top_k: int = 5) -> str:
    """Search the attached KOART PDFs and Team text for grounded support information."""
    return search_knowledge(query, top_k)

@mcp.tool()
def query_koart_data(question: str) -> str:
    """Answer data questions using the attached OU_Tasks_SKUs workbook and dashboard snapshots."""
    return data_answer(question)

@mcp.tool()
def get_ou_metrics(operating_unit: str) -> str:
    """Return the row of workbook metrics for one operating unit."""
    return list_ou_metrics(operating_unit)

if __name__ == "__main__":
    mcp.run()

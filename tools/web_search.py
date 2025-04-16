from pydantic import  Extra
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from datetime import datetime
from utils.functions import is_current_event_query
search_tool = DuckDuckGoSearchRun()

# This defines the actual tool
class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "Use this tool when user asks about current news. This tool only expect query as input. Answer the user's query in a clear, well-structured way in a sentence or two."

    return_direct: bool = True
    class Config:
        extra = Extra.allow  

    def _run(self, query: str) -> str:
        print('Tool triggered web search')
        
        if not query:
            return "Error: Empty query"
        try:
            updated_query = query
            if is_current_event_query(query):
                today = datetime.now().strftime("%B %d, %Y")
                updated_query = f"{query} (as of {today})"
                print(f"[Timestamped Query for Web] {updated_query}")
            else:
                print(f"[Updated Query for Web] {updated_query}")
            
            return search_tool.run(query)
        except Exception as e:
            return f"Search failed: {str(e)}"

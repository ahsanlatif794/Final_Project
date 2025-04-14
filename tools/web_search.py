from pydantic import  Extra
from langchain.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from datetime import datetime

search_tool = DuckDuckGoSearchRun()

# This defines the actual tool
class WebSearchTool(BaseTool):
    name: str = "Web Search Tool"
    description: str = "Use this tool when user asks about current news."

    class Config:
        extra = Extra.allow  # Optional, allows extra fields in the input

    def _run(self, query: str) -> str:
        # Extract query from the Pydantic model instance
        print('tool triggered web search')
        
        
        if not query:
            return "Error: Empty query"
        
        today = datetime.now().strftime("%B %d, %Y")
        print(f'date:{today}')
        query = f"{query} (as of {today})"
    
        try:
            return search_tool.run(query)
        except Exception as e:
            return f"Search failed: {str(e)}"

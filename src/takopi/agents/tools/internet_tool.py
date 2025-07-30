from typing import Any
from google.adk.tools import ToolContext, google_search

class InternetTools():
    def __init__(self):
        pass

    async def google_search(self,args: dict[str,Any],tool_context: ToolContext):
        return await google_search.run_async(args=args,tool_context=tool_context)

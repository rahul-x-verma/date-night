from date_night_api.settings import get_settings
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph import START, MessagesState, StateGraph
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from date_night_api.restaurant_finder.restaurant_finder import find_restaurant


class Chatbot:
    _SYSTEM_MESSAGE = """   
    You are an expert in understanding human cuisine preferences. 
    Make sure you understand the user and their partner's preferences,
    and then find a restaurant that serves a cuisine that both of them will enjoy.
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        settings = get_settings()
        self.model = ChatOpenAI(model='gpt-4o-mini', api_key=settings.openai_api_key)
        self.model = self.model.bind_tools([find_restaurant])
        self.graph = StateGraph(state_schema=MessagesState)
        self.graph.add_node('model',self._call_model)
        self.graph.add_edge(START, 'model')
        self.memory = None
        self.compiled_graph = None
        self._initialized = True

    
    # TODO: This is pretty weird. We should instead use a context manager for the FastAPI app.
    async def __aenter__(self):
        if self.compiled_graph is None:
            self.memory_context = AsyncSqliteSaver.from_conn_string('checkpoints.db')
            self.memory = await self.memory_context.__aenter__()
            self.compiled_graph = self.graph.compile(checkpointer=self.memory)
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        if self.memory_context is not None:
            await self.memory_context.__aexit__(exc_type, exc_value, traceback)
    
    async def _call_model(self, state: MessagesState):
        messages = state['messages']
        messages = [SystemMessage(content=self._SYSTEM_MESSAGE)] + messages
        response = await self.model.ainvoke(messages)
        if response.tool_calls:
            response = await self._execute_tools(messages, response)
        return {'messages': response}

    async def _execute_tools(self, messages, response):
        tool_messages = []
        for call in response.tool_calls:
            tool_input = call['args']['cuisine']
            tool_response = find_restaurant(tool_input)
            tool_messages.append(ToolMessage(tool_response, tool_call_id=call['id']))
        
        messages = messages + [response] + tool_messages
        return await self.model.ainvoke(messages)

    async def ainvoke(self, message: str, thread_id: str):
        config = {'configurable': {'thread_id': thread_id}}
        resp = await self.compiled_graph.ainvoke({'messages': [HumanMessage(content=message)]}, config)
        return resp['messages'][-1].content
        

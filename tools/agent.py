from tools.retrieval_chain import retrievalChainTool,llm
from tools.web_search import WebSearchTool
from tools.sensitiveInfo import SendSensitiveEmail
from utils.final_prompt import final_prompt 
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor


prompt = PromptTemplate(
    input_variables=["input", "agent_scratchpad", "tool_names", "tools"],
    template=final_prompt
)

def ask_agent(query,chat_history):
    tools = [
        retrievalChainTool(),
        WebSearchTool(),
        SendSensitiveEmail()
    ]

    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)

    print("Initializing agent... to trigger the tool")
    agent_executor = AgentExecutor(
        agent = agent,
        tools = tools,
        llm = llm,
        memory=chat_history,
        verbose=True,
        handle_parsing_errors = True,
        max_iterations = 3
    ) 

    print(f"Agent initialized. Running query: {query}")
    response = agent_executor.invoke({"input": query})
    output_text = response.get("output", "")
    print(f'The agent output is:{output_text}')  # Extract the output field
    return output_text
  
 
    # return "Hello"
    # response = agent_executor.invoke({"input": query})
    # print(f'response of agent:{response}')
    # return jsonify({"response": response["output"]})  # Only return the string
    # return jsonify({"response": response.get("output", "")})

    # print("Prompt ")
    # print(agent_executor.agent.llm_chain.prompt.template)

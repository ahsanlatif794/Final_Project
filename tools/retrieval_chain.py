from utils.functions import response_with_sources
from langchain.chains import RetrievalQA
from langchain.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
import os

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
faiss_index = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
retriever = faiss_index.as_retriever(
    # search_type="similarity", 
    search_kwargs={"k": 3}     # Number of relevant chunks to retrieve
)

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=os.getenv('openai_api_key'),
    temperature=0  # Less creative, more factual answers
)

class retrievalChainTool(BaseTool):
    name: str = "RetrievalChain"
    description: str = "Use this tool when user asked something about Pakistan's History. If no relevant documents are found, don't produce final answer just trigger the web search tool. "

    def _run(self, query: str) -> str:
        print('Tool triggered retrieval chain')

        if not query:
            return "Error: Missing 'query' parameter"
    
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents = True
            # memory=memory
        )    

        response = qa_chain.invoke(query)
        final_response = response_with_sources(response)
        print(f'final response:{final_response}')
        return final_response

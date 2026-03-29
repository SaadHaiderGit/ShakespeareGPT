from langchain_ollama import ChatOllama
from agent_core import AgentCore
from orchestrator import Orchestrator
from tools import doc_search

def facts(topic: str) -> str:
    return f"Here's a fun fact about {topic}!"

def setup_model() -> Orchestrator:
    #Tools
    info_tools = {
    "facts": facts,
    "doc_search": doc_search
    }

    info_description = """
        You are an agent that is knowledgeable about Shakespeare and his plays and sonnets.

        You have the following documents as knowledge sources:
        -ShakespearePlays.txt
        -ShakespeareSonnets.txt

        You have access to these tools:
        - facts[topic] → Use this for general or public knowledge about Shakespeare.
        - doc_search[query] → Use this to look up information about Shakespeare's plays and sonnets, such as quotes and characters.

        Only use one tool per question.

        Follow this exact ReAct format:
        Thought: ...
        Action: tool_name[parameter]
        Observation: ...
        Final Answer: ...

        ALWAYS use the facts tool for general information about Shakespeare. Do NOT use the knowledge sources.
        ALWAYS use the doc_search tool for information about Shakespeare's plays and sonnets.
        NEVER invent tools.
        ONLY use quotes when specifically asked by the user.
        Do NOT skip the Action step.
        Do NOT use parentheses for tools — use square brackets like tool_name[param].
        Do NOT put brackets around the entire action.
        The format is: Action: tool[param] — NOT Action: [tool param]

        FORMAT EXAMPLES (copy this pattern exactly):

        Action: doc_search[Romeo]
        Action: facts[birthday]

        If you fail to follow this format, your answer will not be accepted.
    """

    # Create models and agents
    llm = ChatOllama(model="llama3", temperature=0)
    info_agent = AgentCore(llm, info_tools, info_description)

    # Orchestrator
    router = Orchestrator({
        "info": info_agent
    })

    return router

if __name__ == "__main__":
    router = setup_model()

    # Interactive loop
    print("\nWelcome to ShakespeareGPT. Ask a question, and our LLM chatbot will answer (type 'exit' to quit):")
    while True:
        user_input = input("User: ")
        if user_input.lower() == "exit":
            break
        router.run(user_input)
import re

# Max conversation turns kept in context before compaction is needed
MAX_HISTORY = 10

class AgentCore:
    def __init__(self, model, tools: dict[str, callable], description: str):
        self.llm = model
        self.tools = tools
        self.description = description
        self.history = []  # list of {"user": ..., "assistant": ...}

    def _build_history_block(self) -> str:
        # Serialise history turns into a plain-text block for the prompt
        if not self.history:
            return ""
        lines = [f"User: {t['user']}\nAssistant: {t['assistant']}" for t in self.history]
        return "\n\n".join(lines) + "\n\n"

    def compact(self):
        # Summarise full history into a single entry to free up context space
        if not self.history:
            return
        history_text = self._build_history_block()
        summary_prompt = (
            "Summarise the following Shakespeare Q&A conversation in 3-5 sentences, "
            "preserving key facts mentioned:\n\n" + history_text
        )
        summary = self.llm.invoke(summary_prompt).content.strip()
        self.history = [{"user": "[Compacted history]", "assistant": summary}]

    def _extract_action(self, text: str):
        # Match Action: tool[param] or fallback Action: [tool param]
        match = re.search(r"Action:\s*(?:([\w_]+)\[(.*?)\]|\[([\w_]+)\s+(.*?)\])", text, re.DOTALL)
        if match:
            tool = match.group(1) or match.group(3)
            raw_param = match.group(2) or match.group(4)
            param = raw_param.strip().strip('"').strip("'")
            return tool, param
        return None, None

    def _execute_tool(self, tool_name: str, param: str):
        if tool_name not in self.tools:
            return (
                f"The tool '{tool_name}' is not available.\n"
                f"Available tools: {', '.join(self.tools.keys())}"
            )
        try:
            return self.tools[tool_name](param)
        except Exception as e:
            return f"Tool '{tool_name}' failed to execute. Error: {e}"

    def run(self, user_input: str):
        # Prepend conversation history so the LLM can resolve follow-up references
        history_block = self._build_history_block()
        prompt = f"{self.description}\n\n{history_block}Question: {user_input}"
        response = self.llm.invoke(prompt).content
        answer = response[response.find("Final Answer:") + 13:].strip()
        print("LLM:", answer, "\n")
        tool_name, param = self._extract_action(response)
        if tool_name:
            self._execute_tool(tool_name, param)
        else:
            print("\nNo valid Action step found.")
        # Append turn and enforce MAX_HISTORY cap
        self.history.append({"user": user_input, "assistant": answer})
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
        return answer

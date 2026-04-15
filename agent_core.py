import re

# Max conversation turns kept in context before compaction is needed
MAX_HISTORY = 10

# Prompt suffixes injected based on the active response style
STYLE_INSTRUCTIONS = {
    "concise":     "Answer in 1-3 sentences. Be direct, no elaboration.",
    "explanatory": "Answer thoroughly with context, examples, and relevant details.",
}

class AgentCore:
    def __init__(self, model, tools: dict[str, callable], description: str, response_style: str = "concise"):
        self.llm = model
        self.tools = tools
        self.description = description
        self.response_style = response_style  # "concise" | "explanatory"
        self.history = []  # list of {"user": ..., "assistant": ...}

    def _build_history_block(self) -> str:
        # Serialise history turns into a plain-text block prepended to the prompt
        if not self.history:
            return ""
        lines = [f"User: {t['user']}\nAssistant: {t['assistant']}" for t in self.history]
        return "\n\n".join(lines) + "\n\n"

    def compact(self):
        # Summarise full history into one entry to free context space
        if not self.history:
            return
        summary_prompt = (
            "Summarise the following Shakespeare Q&A conversation in 3-5 sentences, "
            "preserving key facts mentioned:\n\n" + self._build_history_block()
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
        style_note = STYLE_INSTRUCTIONS.get(self.response_style, STYLE_INSTRUCTIONS["concise"])
        base_prompt = (
            f"{self.description}\n\n"
            f"Response style: {style_note}\n\n"
            f"{self._build_history_block()}"
            f"Question: {user_input}\n\n"
            f"Provide only your Thought and Action steps. Stop after the Action line."
        )

        # Step 1 — get Thought + Action from LLM
        step1 = self.llm.invoke(base_prompt).content

        # Step 2 — run the real tool and get actual observation
        tool_name, param = self._extract_action(step1)
        observation = self._execute_tool(tool_name, param) if tool_name else "No tool matched. Answer from general knowledge."

        # Step 3 — feed real observation back; LLM generates grounded Final Answer
        step2_prompt = (
            f"{base_prompt}\n\n{step1}\n"
            f"Observation: {observation}\n\n"
            f"Now provide your Final Answer based solely on the Observation above."
        )
        step2 = self.llm.invoke(step2_prompt).content
        answer = (step2[step2.find("Final Answer:") + 13:] if "Final Answer:" in step2 else step2).strip()

        print("LLM:", answer, "\n")
        # Append turn; cap at MAX_HISTORY (oldest turns dropped)
        self.history.append({"user": user_input, "assistant": answer})
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
        return answer

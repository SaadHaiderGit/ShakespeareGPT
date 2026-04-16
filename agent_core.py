import re

# Max conversation turns kept in context before compaction is needed
MAX_HISTORY = 10

# Max tool-use iterations per question before forcing a Final Answer
MAX_STEPS = 3

# Prompt suffixes injected based on the active response style
STYLE_INSTRUCTIONS = {
    "concise":     "Answer in at least 40 words but stay brief and direct. No lengthy elaboration.",
    "explanatory": "Answer in at least 100 words. Be thorough — include context, examples, and relevant details.",
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

    def _prepare_answer_prompt(self, user_input: str) -> str:
        # Multi-step ReAct loop: repeat Thought→Action→Observation up to MAX_STEPS times,
        # then return a prompt that asks for the Final Answer over the full transcript
        style_note = STYLE_INSTRUCTIONS.get(self.response_style, STYLE_INSTRUCTIONS["concise"])
        transcript = (
            f"{self.description}\n\n"
            f"Response style: {style_note}\n\n"
            f"{self._build_history_block()}"
            f"Question: {user_input}\n"
        )
        for step in range(MAX_STEPS):
            step_prompt = transcript + "\nProvide your next Thought and Action. Stop after the Action line."
            response = self.llm.invoke(step_prompt).content
            tool_name, param = self._extract_action(response)
            if not tool_name:
                # LLM produced no action — enough context to answer
                transcript += f"\n{response}\n"
                break
            observation = self._execute_tool(tool_name, param)
            print(f"[Step {step + 1}] {tool_name}[{param}]")
            transcript += f"\n{response}\nObservation: {observation}\n"

        return transcript + "\nNow provide your Final Answer based on the Observations above."

    def _extract_answer(self, text: str) -> str:
        # Pull the Final Answer section out of a full LLM response
        return (text[text.find("Final Answer:") + 13:] if "Final Answer:" in text else text).strip()

    def _record_turn(self, user_input: str, answer: str):
        # Append turn to history and enforce MAX_HISTORY cap
        self.history.append({"user": user_input, "assistant": answer})
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]

    def _stream_answer(self, step2_prompt: str):
        # Yield Final Answer tokens from a streaming LLM call; skips preamble before "Final Answer:"
        in_answer = False
        buf = ""
        for chunk in self.llm.stream(step2_prompt):
            text = chunk.content
            if not in_answer:
                buf += text
                if "Final Answer:" in buf:
                    in_answer = True
                    after = buf[buf.find("Final Answer:") + 13:]
                    if after:
                        yield after
            else:
                yield text

    def run(self, user_input: str) -> str:
        # Non-streaming path used by CLI
        step2_prompt = self._prepare_answer_prompt(user_input)
        response = self.llm.invoke(step2_prompt).content
        answer = self._extract_answer(response)
        print("LLM:", answer, "\n")
        self._record_turn(user_input, answer)
        return answer

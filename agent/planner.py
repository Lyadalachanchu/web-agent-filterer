from typing import Dict, Any
from .llm import LLM
from .schemas import Plan


SYSTEM_PROMPT = (
"You are a precise web task planner. Always output STRICT JSON only, valid to the schema:\n"
"{\n 'thought': str,\n 'action': { 'type': 'CLICK'|'TYPE'|'FIND'|'EXTRACT'|'STOP', 'args': object },\n 'expected_observation': str,\n 'success_checklist': [str, ...]\n}\n"
"Action types:\n"
"- CLICK: click an element/link (args: {text: str} or {selector: str}) - Use this to navigate by clicking links\n"
"- TYPE: fill input field (args: {selector: str, text: str})\n"
"- FIND: search the page (args: {query: str})\n"
"- EXTRACT: take a snapshot (rarely needed - page content is already visible)\n"
"- STOP: when you have the answer OR cannot find it (args: {answer: str})\n"
"IMPORTANT:\n"
"- If the Page Content contains the answer, use STOP immediately with the answer.\n"
"- If the Page Content does NOT contain the answer and there's no clear way to find it, use STOP to report that.\n"
"- To navigate to other pages, CLICK on links visible in the Page Content.\n"
"- You can only visit pages by clicking links - no direct URL navigation.\n"
"No extra text, no markdown, no comments."
)


PLAN_FORMAT_HINT = (
"Return ONLY a JSON object. Examples:\n"
"{\n \"thought\": \"The page content shows the answer\",\n"
" \"action\": {\"type\": \"STOP\", \"args\": {\"answer\": \"The answer is...\"}},\n"
" \"expected_observation\": \"Task completed\",\n"
" \"success_checklist\": [\"answer found\", \"goal achieved\"]\n}\n"
"OR to navigate:\n"
"{\n \"thought\": \"Need to check the About page\",\n"
" \"action\": {\"type\": \"CLICK\", \"args\": {\"text\": \"About\"}},\n"
" \"expected_observation\": \"About page loaded\",\n"
" \"success_checklist\": [\"about page visible\"]\n}"
)


class Planner:
    def __init__(self, llm: LLM):
        self.llm = llm


    def decide(self, goal: str, plan_summary: str, latest_observation: str, constraints: Dict[str, Any]) -> Plan:
        user = (
        f"GOAL:\n{goal}\n\n"
        f"PLAN_SUMMARY:\n{plan_summary}\n\n"
        f"LATEST_OBSERVATION (filtered Markdown):\n{latest_observation[:6000]}\n\n"
        f"CONSTRAINTS: {constraints}\n\n"
        + PLAN_FORMAT_HINT
        )
        raw = self.llm.complete(SYSTEM_PROMPT, user)
        data = self.llm.parse_json_block(raw)
        return Plan(**data)
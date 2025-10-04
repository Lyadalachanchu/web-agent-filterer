from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ActionType(str, Enum):
    NAVIGATE = "NAVIGATE"
    CLICK = "CLICK"
    TYPE = "TYPE"
    FIND = "FIND"
    EXTRACT = "EXTRACT"
    STOP = "STOP"


class Action(BaseModel):
    type: ActionType
    args: Dict[str, Any] = Field(default_factory=dict)


class Plan(BaseModel):
    thought: str = Field(description="Brief reasoning for next step")
    action: Action
    expected_observation: str
    success_checklist: List[str] = Field(default_factory=list)


class Step(BaseModel):
    number: int
    action: Action
    observation_md: str
    extracted_facts: Dict[str, Any] = Field(default_factory=dict)


class AgentState(BaseModel):
    goal: str
    steps: List[Step] = Field(default_factory=list)
    plan_summary: str = "Start: clarify goal and outline a high-level plan."
    found_answer: bool = False
    budget_tokens: int = 6000
    max_steps: int = 8
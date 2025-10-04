import os
import typer
from dotenv import load_dotenv
from .schemas import AgentState, Step
from .llm import LLM
from .planner import Planner
from .navigator import Browser
from .filterer import ContextFilterer
from .controller import Controller
from .utils import trunc

# Load environment variables from .env file
load_dotenv()

app = typer.Typer(add_completion=False)

@app.command()
def main(goal: str, url: str = typer.Option(None, help="Starting URL (file:// or https://)"), model: str = typer.Option(None, help="OpenAI model (default from env)"), max_steps: int = typer.Option(None), token_budget: int = typer.Option(None), headless: bool = typer.Option(True, help="Run headless browser")):
    # Env + defaults
    model = model or os.getenv("OPENAI_MODEL", "gpt-4")
    max_steps = max_steps or int(os.getenv("MAX_STEPS", "8"))
    token_budget = token_budget or int(os.getenv("TOKEN_BUDGET", "6000"))

    llm = LLM(model=model)
    planner = Planner(llm)

    state = AgentState(goal=goal, max_steps=max_steps, budget_tokens=token_budget)

    with Browser(headless=headless, nav_timeout_ms=int(os.getenv("NAV_TIMEOUT_MS", "20000"))) as browser:
        filterer = ContextFilterer(token_budget=token_budget)
        controller = Controller(browser, filterer, goal=goal)

        # Navigate to starting URL if provided
        latest_observation = ""
        if url:
            print(f"Navigating to: {url}")
            exec_out = browser.goto(url)
            latest_observation = filterer.to_markdown(exec_out, goal=goal)
            state.plan_summary = f"Started at {url}. Current page loaded."
        
        while not state.found_answer and len(state.steps) < state.max_steps:
            constraints = {
                "max_steps": state.max_steps,
                "remaining_steps": state.max_steps - len(state.steps),
                "token_budget": state.budget_tokens,
            }
            plan = planner.decide(goal=state.goal, plan_summary=state.plan_summary, latest_observation=latest_observation, constraints=constraints)

            exec_out = controller.run(plan.action.model_dump())
            latest_observation = exec_out["observation_md"]

            step = Step(number=len(state.steps) + 1, action=plan.action, observation_md=latest_observation, extracted_facts={})
            state.steps.append(step)

            # Update summary (very light)
            state.plan_summary = f"Last action: {plan.action.type.value}. Expectation: {trunc(plan.expected_observation, 180)}."

            # Stop conditions
            if plan.action.type.value == "STOP":
                state.found_answer = True
                break

        # Final output
        print("\n=== FINAL SCRATCHPAD ===")
        for s in state.steps:
            print(f"\nStep {s.number}: {s.action.type.value}")
            print(trunc(s.observation_md, 1000))
        print("\nDone.")

if __name__ == "__main__":
    app()
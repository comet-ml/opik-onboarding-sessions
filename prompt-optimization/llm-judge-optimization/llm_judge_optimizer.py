"""
LLM Judge Prompt Optimizer using GEPA

Optimizes the 'Usefulness Metric' prompt from the Opik Prompt Library
against the 'Opik-Agent' dataset using the GEPA algorithm and an Equals metric.

Usage:
    python scripts/llm_judge_optimizer.py
    python scripts/llm_judge_optimizer.py --trials 15
    python scripts/llm_judge_optimizer.py --model gpt-4o
    python scripts/llm_judge_optimizer.py --save
"""

import argparse
import os
from typing import Any, Dict

import opik
from dotenv import load_dotenv
from opik.evaluation.metrics import Equals
from opik.evaluation.metrics.score_result import ScoreResult
from opik_optimizer import ChatPrompt, GepaOptimizer

load_dotenv()


DATASET_NAME = "Opik-Agent-Dataset"  # "Opik-Agent"
PROMPT_NAME = "Usefulness Metric Prompt"
PROJECT_NAME = "LLM Judge Optimization"

equals = Equals(case_sensitive=False)


def equals_metric(dataset_item: Dict[str, Any], llm_output: str) -> ScoreResult:
    """Score the LLM output against the 'Useful' feedback score value."""
    feedback_scores = dataset_item.get("feedback_scores", [])
    reference = ""
    for score in feedback_scores:
        if score.get("name") == "Useful":
            reference = str(score["value"])
            break
    print(f"Reference: {reference}")
    print(f"LLM Output: {llm_output}")
    score = equals.score(output=llm_output, reference=reference)
    print(f"Score: {score}")
    return score


def run(model: str, n_trials: int, save_prompt: bool):
    client = opik.Opik()

    print(f"\n{'=' * 60}")
    print("LLM Judge Optimizer (GEPA)")
    print(f"{'=' * 60}")
    print(f"  Dataset:   {DATASET_NAME}")
    print(f"  Prompt:    {PROMPT_NAME}")
    print("  Algorithm: GEPA")
    print("  Metric:    Equals")
    print(f"  Model:     {model}")
    print(f"  Trials:    {n_trials}")
    print(f"  Workspace: {os.environ.get('OPIK_WORKSPACE', '')}")
    print(f"{'=' * 60}\n")

    dataset = client.get_dataset(name=DATASET_NAME)
    #prompt_obj = client.get_prompt(name=PROMPT_NAME)
    prompt = """You are an impartial judge tasked with evaluating the quality and usefulness of AI-generated responses.

Your evaluation should consider the following key factors:
- Helpfulness: How well does it solve the user's problem?
- Relevance: How well does it address the specific question?
- Accuracy: Is the information correct and reliable?
- Depth: Does it provide sufficient detail and explanation?
- Creativity: Does it offer innovative or insightful perspectives when appropriate?
- Level of detail: Is the amount of detail appropriate for the question?

Analyze the text thoroughly and assign a score of 0 and 1, where:

   - 1: Exceptional response that excels in all criteria
   - 0: Unhelpful response


Provide a brief reason for your decision.

Now, please evaluate the following:

User Question: {{input}}
AI Response: {{expected_output}}

Provide ONLY the raw score of 0 or 1. 
"""

    #Version prompt in the prompt library
    opik.Prompt(
        name="Usefulness Metric Prompt",
        prompt=prompt
    )

    #Optimize this prompt using GEPA
    chat_prompt = ChatPrompt(
        system=prompt, user="{input}", model="gpt-5-nano"
    )

    optimizer = GepaOptimizer(
        model="gpt-5",
        n_threads=6,
    )

    print("\nStarting GEPA optimization...\n")

    result = optimizer.optimize_prompt(
        prompt=chat_prompt,
        dataset=dataset,
        metric=equals_metric,
        max_trials=15,
        n_samples="all",
        reflection_minibatch_size=25,
        project_name=PROJECT_NAME,
    )

    print(f"\n{'=' * 60}")
    print("OPTIMIZATION RESULTS")
    print(f"{'=' * 60}")

    result.display()

    if result.prompt is None:
        print("\nNo optimized prompt returned. Check the Opik UI for details.")
        return result

    optimized_system = getattr(result.prompt, "system", None)
    if optimized_system:
        print(f"\nBest Score: {result.score:.2%}")
        print(f"\nOptimized Prompt:\n{optimized_system[:500]}")

    if save_prompt and optimized_system:
        saved_name = f"{PROMPT_NAME} - Optimized"
        opik.Prompt(
            name=saved_name,
            prompt=optimized_system,
            metadata={
                "source": "llm_judge_optimizer.py",
                "algorithm": "GEPA",
                "base_prompt": PROMPT_NAME,
            },
            description=f"GEPA-optimized version of '{PROMPT_NAME}'",
            change_description="Saved from GEPA optimizer result",
            tags=["optimized", "llm-judge", "gepa"],
        )
        print(f"\nSaved optimized prompt to library: {saved_name}")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Optimize an LLM judge prompt with GEPA"
    )
    parser.add_argument(
        "--model", type=str, default="gpt-4o-mini", help="LiteLLM model name"
    )
    parser.add_argument(
        "--trials", type=int, default=12, help="Number of optimization trials"
    )
    parser.add_argument(
        "--save", action="store_true", help="Save optimized prompt to library"
    )

    args = parser.parse_args()
    run(model=args.model, n_trials=args.trials, save_prompt=args.save)
    opik.flush_tracker()

    print(f"\n{'=' * 60}")
    print("OPTIMIZATION COMPLETE")
    print(f"{'=' * 60}")

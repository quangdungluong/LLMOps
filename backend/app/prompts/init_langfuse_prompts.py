import os
import sys
from typing import Dict, List, Optional

from app.core.config import settings
from app.prompts.manager import DEFAULT_PROMPTS, prompt_manager


def main():
    lf = prompt_manager._lf_client
    prompt_specs: Dict[str, Dict[str, Optional[List[str]]]] = {
        "qa_system": {"name": "llmops/qa_system"},
        "contextualize_q_system": {"name": "llmops/contextualize_q_system"},
        "document_prompt": {"name": "llmops/document_prompt"},
    }

    for key, spec in prompt_specs.items():
        name = spec["name"]
        template = DEFAULT_PROMPTS[key]

        try:
            try:
                print(f"Checking for prompt {name}")
                prompt = lf.get_prompt(name)
                print(f"Found prompt {name}")
            except Exception:
                lf.create_prompt(
                    name=name,
                    prompt=template,
                    labels=["production"],
                )
                print(f"Created prompt {name}")
        except Exception as e:
            print(f"Failed to upsert prompt {name}: {e}")


if __name__ == "__main__":
    main()

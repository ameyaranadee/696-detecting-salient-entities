# utils/llm_utils.py
import re
import json

def parse_llm_decision(text):
    """
    Parses the LLM response and returns True for "yes", False for "no".
    Defaults to True (yes) if parsing fails to ensure high recall.
    """
    try:
        if not text:
            raise ValueError("Empty response")

        text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()

        if text.startswith("{") and text.endswith("}"):
            data = json.loads(re.sub(r",\s*([}\]])", r"\\1", re.sub(r"(')", '"', text)))
            return data.get("final_decision", "yes").strip().lower() == "yes"

        match = re.search(r"final[_\s]?decision\s*['\"]?\s*:\s*['\"]?(yes|no)", text, re.IGNORECASE)
        return match.group(1).lower() == "yes" if match else True

    except Exception as e:
        print(f"[Decision Warning] Fallback to YES: {e}")
        return True

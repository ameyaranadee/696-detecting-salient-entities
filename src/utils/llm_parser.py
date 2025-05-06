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

def parse_contextual_el_output(text):
    try:
        match = re.search(r'\{.*?\}', text, re.DOTALL)
        if not match:
            return -1
        data = json.loads(match.group())
        m = re.match(r'(-?\d+)\s*\.\s*(.+)', data.get("final_decision", ""))
        return int(m.group(1)) if m else -1
    except Exception as e:
        print(f"[parse_contextual_el_output] Error: {e}")
        return -1

def clean_incomplete_json(response):
    # Extract JSON-like content from the response
    match = re.search(r'\{.*\}', response, re.DOTALL)
    if not match:
        print("Error: No valid JSON-like content found in the response.")
        with open("weird.txt", "a", encoding="utf-8") as f:
            f.write(f"Weird Response: {response}\n")
        return {"entities": []}  # Return an empty entity list
    
    json_like_str = match.group(0)
    
    # Preserve valid apostrophes inside words while ensuring JSON formatting
    json_like_str = re.sub(r'(\w)\'(\w)', r'\1’\2', json_like_str)  # Convert ' to ’ in words
    json_like_str = json_like_str.replace("'", '"')  # Replace improper single quotes with double quotes
    json_like_str = re.sub(r',\s*}', '}', json_like_str)  # Remove trailing commas before }
    json_like_str = re.sub(r',\s*\]', ']', json_like_str)  # Remove trailing commas before ]

    # Attempt to extract "entities" list
    entities_match = re.search(r'"entities"\s*:\s*\[', json_like_str)
    if not entities_match:
        print("Error: No 'entities' key found in the response.")
        with open("weird.txt", "a", encoding="utf-8") as f:
            f.write(f"Weird JSON Content: {json_like_str}\n")
        return {"entities": []}  # Return an empty entity list

    # Extract individual entity objects safely
    entity_blocks = re.findall(r'\{[^{}]*\}', json_like_str, re.DOTALL)

    valid_entities = []
    for block in entity_blocks:
        try:
            entity = json.loads(block)  # Attempt to parse each entity block
            valid_entities.append(entity)
        except json.JSONDecodeError:
            print(f"Skipping invalid entity: {block}")
            with open("weird.txt", "a", encoding="utf-8") as f:
                f.write(f"Invalid Entity Block: {block}\n")

    # Remove duplicate entities based on "entity title"
    try:
        cleaned_response = {
                "entities": list({e.get("entity title", f"Unknown-{i}"): e for i, e in enumerate(valid_entities)}.values())
            }
    except Exception as e:
            print("Error processing entities:", e)
            cleaned_response = {"entities": []}  # Fallback to empty list

    return cleaned_response
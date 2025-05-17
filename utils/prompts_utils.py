# utils/prompts.py
import re
import json
from datetime import datetime

def construct_pointwise_prompt(entity, candidate, model: str):
    if model == "llama":
        return [
        {
            "role": "user", 
            "content": (f"""You are an entity disambiguator. I'll provide you with a detailed description of entity disambiguation along with several tips on what to look out for:\n 1. Context: Look at the surrounding text to understand the topic. 2. Categories: Consider the type of the entity (person, organization, location, etc.). 3. Modifiers: Pay attention to words or phrases that add details to the mention. 4. Co-references: Check other mentions of the same entity in the text. 5. Temporal and Geographical Factors: Consider when and where the text was written. 6. External Knowledge: Use knowledge from outside the text. Remember, effective entity disambiguation requires understanding the text thoroughly, having world knowledge, and exercising good judgment. Your job is to decide whether a candidate should stay on the shortlist for an entity in context. Output **"yes"** if the candidate is a **plausible match** for the entity mention based on the context. Output **"no"** if the candidate is **clearly irrelevant or incompatible** with the context, even if the entity names look similar. Do **not** default to "yes" if you're unsure — use clues from the context, entity type, and modifiers to guide your decision. Example 1: entity: Australian. context: "Earlier today, the ###Australian### Gliders beat the Chinese women's national wheelchair basketball team 57–45 at the Rollers & Gliders World Challenge." candidate: Australia — A country in the Southern Hemisphere that includes the mainland of the Australian continent, Tasmania, and numerous smaller islands. {{"final_decision":"yes","reasoning":"The mention 'Australian' modifies 'Gliders', a known Australian team. While the candidate is a country, it is plausible and commonly used in such adjectival form."}} Example 2: entity: Gliders. context: "Earlier today, the Australian ###Gliders### beat the Chinese women's national wheelchair basketball team."  candidate: Glider (aircraft) — A heavier-than-air aircraft that is supported in flight by the dynamic reaction of the air against its lifting surfaces.  {{"final_decision":"no","reasoning":"The candidate refers to an aircraft, which is not relevant here. In the context of a sports match, 'Gliders' refers to a sports team, not a flying machine."}} Now, I will provide you with an entity, its context, and a candidate with its description. The entity in the context is highlighted with '###'. entity: {entity['entity_title']} context: {entity['surrounding_context']}" candidate: {candidate['title']}. {candidate['text'][:300]}. Please analyze the information and determine if the entity and the candidate are related. Keep the answer to exactly one compact JSON object on a single line, no extra spaces: {{"final_decision":"yes|no","reasoning":""}}""")
        }
    ]
    
    elif model == "zephyr":
        system_prompt = ("You are an entity disambiguator. I'll provide you with a detailed description of entity disambiguation.")
        
        user_input = (f"""I'll provide you with a detailed description of entity disambiguation along with several tips on what to look out for:\n 1. Context: Look at the surrounding text to understand the topic. 2. Categories: Consider the type of the entity (person, organization, location, etc.). 3. Modifiers: Pay attention to words or phrases that add details to the mention. 4. Co-references: Check other mentions of the same entity in the text. 5. Temporal and Geographical Factors: Consider when and where the text was written. 6. External Knowledge: Use knowledge from outside the text. Remember, effective entity disambiguation requires understanding the text thoroughly, having world knowledge, and exercising good judgment. Your job is to decide whether a candidate should stay on the shortlist for an entity in context. Output **"yes"** if the candidate is a **plausible match** for the entity mention based on the context. Output **"no"** if the candidate is **clearly irrelevant or incompatible** with the context, even if the entity names look similar. Do **not** default to "yes" if you're unsure — use clues from the context, entity type, and modifiers to guide your decision. Example 1: entity: Australian. context: "Earlier today, the ###Australian### Gliders beat the Chinese women's national wheelchair basketball team 57–45 at the Rollers & Gliders World Challenge." candidate: Australia — A country in the Southern Hemisphere that includes the mainland of the Australian continent, Tasmania, and numerous smaller islands. {{"final_decision":"yes","reasoning":"The mention 'Australian' modifies 'Gliders', a known Australian team. While the candidate is a country, it is plausible and commonly used in such adjectival form."}} Example 2: entity: Gliders. context: "Earlier today, the Australian ###Gliders### beat the Chinese women's national wheelchair basketball team."  candidate: Glider (aircraft) — A heavier-than-air aircraft that is supported in flight by the dynamic reaction of the air against its lifting surfaces.  {{"final_decision":"no","reasoning":"The candidate refers to an aircraft, which is not relevant here. In the context of a sports match, 'Gliders' refers to a sports team, not a flying machine."}} Now, I will provide you with an entity, its context, and a candidate with its description. The entity in the context is highlighted with '###'. entity: {entity['entity_title']} context: {entity['surrounding_context']}" candidate: {candidate['title']}. {candidate['text'][:300]}. Please analyze the information and determine if the entity and the candidate are related. Keep the answer to exactly one compact JSON object on a single line, no extra spaces: {{"final_decision":"yes|no","reasoning":""}})""")
        
        return f"<|system|>\n{system_prompt}</s>\n<|user|>\n{user_input}</s>\n<|assistant|>"
    
    else:
        raise ValueError(f"Unknown model: {model}")
        
        
def parse_llm_decision(text: str, model: str, log_path="bad_llm_outputs.log") -> bool:
    """
    Extract decision ('yes' or 'no') from LLM output. Fallback to 'yes' on failure.
    """
    try:
        if not text:
            raise ValueError("Empty text")

        if model == "zephyr":
            text = re.sub(r"^Example\s*\d+\s*:\s*", "", text.strip())
            match = re.findall(r"\{.*?\}", text, re.DOTALL)
            if not match:
                raise ValueError("No JSON-like object found")
            raw = match[-1]
        else:
            raw = text.strip().strip("`")

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            cleaned = raw.replace("'", '"')
            cleaned = re.sub(r",\s*([}\]])", r"\\1", cleaned)
            parsed = json.loads(cleaned)

        for k in ("final_decision", "finalDecision", "decision"):
            if k in parsed:
                return str(parsed[k]).strip().lower() == "yes"

        raise ValueError("final_decision not found")

    except Exception as e:
        print(f"[decision warning] Falling back to YES — could not parse: {text[:120]} — {e}")
        with open(log_path, "a") as f:
            f.write(f"\n---\n[{datetime.now()}]\n{text.strip()}\nError: {e}\n")
        return True

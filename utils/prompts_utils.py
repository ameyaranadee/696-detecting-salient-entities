# utils/prompts.py
import re
import random
import json
from datetime import datetime

COT_POOL = [
    {
        "mention": "Washington, D.C.",
        "surrounding_context": "The United States capital of ###Washington, D.C.### legalized same-sex marriage on Wednesday.",
        "candidates": [
            {"id": 1, "name": "Washington, D.C.", "summary": "The capital city of the United States."},
            {"id": 2, "name": "Washington (state)", "summary": "A state in the Pacific Northwest region of the United States."}
        ],
        "answer": "1.Washington, D.C."
    },
    {
        "mention": "Eric Massa",
        "surrounding_context": "New York Representative ###Eric Massa### announced Wednesday that he would be stepping down as Congressman from New York's 29th congressional district.",
        "candidates": [
            {"id": 1, "name": "Eric Massa", "summary": "A former U.S. Congressman from New York."},
            {"id": 2, "name": "Eric Massan", "summary": "A fictional character in a novel."}
        ],
        "answer": "1.Eric Massa"
    },
    {
        "mention": "Air Canada",
        "surrounding_context": "Canadian airline ###Air Canada### has said that it will be laying off 1,010 machinists seconded to work at the Aveos Fleet Performance aircraft maintenance company.",
        "candidates": [
            {"id": 1, "name": "Air Canada", "summary": "The flag carrier and largest airline of Canada."},
            {"id": 2, "name": "Canada Air", "summary": "A fictional airline in a movie."}
        ],
        "answer": "1.Air Canada"
    },
    {
        "mention": "Bosnian president",
        "surrounding_context": "Former ###Bosnian president### Dr. Ejup Ganić was arrested by the Metropolitan Police at Heathrow Airport, London on Monday.",
        "candidates": [
            {"id": 1, "name": "Ejup Ganić", "summary": "A former president of the Federation of Bosnia and Herzegovina."},
            {"id": 2, "name": "Alija Izetbegović", "summary": "The first president of Bosnia and Herzegovina."}
        ],
        "answer": "1.Ejup Ganić"
    },
    {
        "mention": "Greek bailout",
        "surrounding_context": "The spike lower this morning indicates market nervousness about the prospects of a ###Greek bailout### - the message coming out of Europe is still confused.",
        "candidates": [
            {"id": 1, "name": "Greek bailout", "summary": "A financial assistance program for Greece during its debt crisis."},
            {"id": 2, "name": "Greek mythology", "summary": "A body of myths originally told by the ancient Greeks."}
        ],
        "answer": "1.Greek bailout"
    }
]

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

def construct_contextual_prompt(entity_row, model: str):
    ex = random.choice(COT_POOL)
    ex_candidates = "; ".join([f"{c['id']}.{c['name']} – {c['summary']}" for c in ex['candidates']])

    if model == "llama":
        return [
        {
            "role": "user",
            "content": (f"""You are an entity disambiguator. I'll provide you with a detailed description of entity disambiguation along with several tips on what to look out for:\n 1. Context: Look at the surrounding text to understand the topic. 2. Categories: Consider the type of the entity (person, organization, location, etc.). 3. Modifiers: Pay attention to words or phrases that add details to the mention. 4. Co-references: Check other mentions of the same entity in the text.  5. Temporal and Geographical Factors: Consider when and where the text was written. 6. External Knowledge: Use knowledge from outside the text.  Remember, effective entity disambiguation requires understanding the text thoroughly, having world knowledge, and exercising good judgment. Now, I will first provide you with an example to illustrate the task: Mention: {ex['mention']} Context: {ex['surrounding_context']} Candidates: {ex_candidates} Answer: {ex['answer']}. Now, I will give you a new mention, its context, and a list of candidate entities. The mention is highlighted with '###'. Mention: {entity_row['entity_title']} Context: {entity_row['surrounding_context']} Candidates: """ + "; ".join([f"{idx + 1}.{cand['title']} – {cand['text'][:300]}"  for idx, cand in enumerate(entity_row['candidates_after_pointwise'])]) + """ Think step by step. At the end output exactly one line with the ID and name of the chosen entity, e.g., '3.Barack Obama'. If none of the candidates are correct, output '-1.None'. Only output a single JSON object in the following format, without line breaks, indentation, or extra text: {"final_decision": "<id>.<entity name>", "reasoning": "your explanation here"} """)
        }
    ]

    elif model == "zephyr":
        system_prompt = ("You are an entity disambiguator.")
        user_input = (f"""I'll provide you with a detailed description of entity disambiguation along with several tips on what to look out for:\n 1. Context: Look at the surrounding text to understand the topic. 2. Categories: Consider the type of the entity (person, organization, location, etc.). 3. Modifiers: Pay attention to words or phrases that add details to the mention. 4. Co-references: Check other mentions of the same entity in the text.  5. Temporal and Geographical Factors: Consider when and where the text was written. 6. External Knowledge: Use knowledge from outside the text.  Remember, effective entity disambiguation requires understanding the text thoroughly, having world knowledge, and exercising good judgment. Now, I will first provide you with an example to illustrate the task: Mention: {ex['mention']} Context: {ex['surrounding_context']} Candidates: {ex_candidates} Answer: {ex['answer']}. Now, I will give you a new mention, its context, and a list of candidate entities. The mention is highlighted with '###'. Mention: {entity_row['entity_title']} Context: {entity_row['surrounding_context']} Candidates: """ + "; ".join([f"{idx + 1}.{cand['title']} – {cand['text'][:100]}"  for idx, cand in enumerate(entity_row['candidates_after_pointwise'])]) + """ Think step by step. At the end output exactly one line with the ID and name of the chosen entity, e.g., '3.Barack Obama'. If none of the candidates are correct, output '-1.None'. Only output a single JSON object in the following format, without line breaks, indentation, or extra text: {"final_decision": "<id>.<entity name>", "reasoning": "your explanation here"} """)

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

def parse_contextual_el_output(text: str, log_path="bad_contextual_outputs.log") -> int:
    """
    Extract the final candidate index from Zephyr-style natural language output.
    Falls back to -1 on error and logs malformed outputs.
    """
    try:
        if not text:
            raise ValueError("Empty text")

        # Normalize the text
        text = text.strip()

        # Strategy 1: Match "Final decision: 3." (with or without candidate name)
        m = re.search(r'final decision\s*[:\-]?\s*(\d+)', text, flags=re.IGNORECASE)
        if m:
            return int(m.group(1))

        # Strategy 2: Look for pattern like: {"final_decision": "3. Something"}
        match = re.findall(r"\{.*?\}", text, re.DOTALL)
        if match:
            raw = match[-1]
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                # Fix bad formatting and retry
                raw = raw.replace("'", '"')
                raw = re.sub(r",\s*([}\]])", r"\1", raw)
                data = json.loads(raw)

            val = data.get("final_decision", "")
            m = re.match(r'(\d+)', val)
            if m:
                return int(m.group(1))

        raise ValueError("No parseable candidate index found")

    except Exception as e:
        print(f"[contextual warning] Could not parse: {text[:120]} — {e}")
        try:
            with open(log_path, "a") as f:
                f.write(f"\n---\n[{datetime.now()}]\n{text.strip()}\nError: {e}\n")
        except Exception as log_err:
            print(f"[log warning] Could not write to log: {log_err}")
        return -1
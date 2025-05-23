import ast
import pandas as pd
from utils.prompts_utils import construct_contextual_prompt, parse_contextual_el_output, COT_POOL
from utils.llm_configs import setup_llm, get_sampling_params
from utils.io import save_intermediate_outputs
from utils.EL_eval import evaluate_contextual_linking

def build_contextual_prompts(df: pd.DataFrame, model: str = "llama"):
    prompt_records = []
    for idx, row in df.iterrows():
        if not row['candidates_after_pointwise']:
            continue
        prompt = construct_contextual_prompt(row, model=model)
        label_map = {i+1: cand for i, cand in enumerate(row['candidates_after_pointwise'])}
        prompt_records.append((idx, label_map, prompt, len(prompt) // 4))
    return prompt_records


def run_contextual_inference(prompt_records, llm, sampling_params, batch_size=250):
    all_outputs = []
    for chunk_start in range(0, len(prompt_records), batch_size):
        batch = prompt_records[chunk_start:chunk_start + batch_size]
        prompts = [rec[2] for rec in batch]
        responses = llm.chat(messages=prompts, sampling_params=sampling_params)

        for (record, response) in zip(batch, responses):
            idx, label_map, _ = record
            text = response.outputs[0].text.strip()
            selected_label = parse_contextual_el_output(text)

            selected_candidate = label_map.get(selected_label, 0)
            all_outputs.append((idx, selected_candidate))
    return all_outputs


def write_linked_entities(df, all_outputs):
    top_linked_entities = [0] * len(df)
    for idx, selected_candidate in all_outputs:
        if selected_candidate:
            top_linked_entities[idx] = int(selected_candidate['wiki_id'])
    df['top_linked_entity'] = pd.Series(top_linked_entities, dtype="Int64")
    return df


def main():
    model = "llama"  # or "zephyr"
    sampling_params = get_sampling_params(max_tokens=350, temperature=0.6, top_p=0.9, stops=["</s>", "\n}"])
    llm, sampling_params = setup_llm(model=model)

    df = pd.read_csv(f"outputs/pointwise/final/intermediate_results_ner_llama.csv")
    df['candidates_after_pointwise'] = df['candidates_after_pointwise'].apply(
        lambda x: ast.literal_eval(x) if pd.notna(x) else []
    )

    prompt_records = build_contextual_prompts(df, model=model)

    all_outputs = run_contextual_inference(prompt_records, llm, sampling_params)
    df = write_linked_entities(df, all_outputs)

    save_intermediate_outputs(df, "outputs/contextual/ner_SEL_WikiNews_contextual_linked_results.csv")
    print("Contextual linking completed.")
    # metrics = evaluate_contextual_linking(df)
    # print(metrics)


if __name__ == "__main__":
    main()

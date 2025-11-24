import argparse
import csv
import os
import pickle
import random
import re
import signal
import time
from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
from tqdm import tqdm
import openai
from typing import Union


"""
Usage example:
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_DIR=$(pwd)/outputs/try1/v${TIMESTAMP}
mkdir -p ${OUTPUT_DIR}
echo ${OUTPUT_DIR}
python code/100_run_benchmark.py \
    --problem-name "quantumbench8" \
    --model-name "gpt-5-2025-08-07" \
    --model-type "openaireasoning" \
    --client-type "openai" \
    --effort "high" \
    --prompt-type "zeroshot" \
    --llm-server-url "None" \
    --out-dir "${OUTPUT_DIR}" \
    --num-workers 8
"""



## --- SETUP ---
SEED=0
OPENROUTER_API_KEY=None
# OPENROUTER_API_KEY=os.environ["OPENROUTER_API_KEY"]
OPENAI_API_KEY=os.environ["OPENAI_API_KEY"]

QB_PATH = './quantumbench/quantumbench.csv'
CATEGORY_PATH = './quantumbench/category.csv'
CACHE_PATH = './cache'


Example = namedtuple('Example', [
    'numchoices',
    'question', 
    'choice1', 
    'choice2', 
    'choice3', 
    'choice4', 
    'choice5',
    'choice6',
    'choice7',
    'choice8',
    'correct_index', 
    'subdomain'
])
LETTER_TO_INDEX = {'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4, 'F': 5, 'G': 6, 'H': 7}
INDEX_TO_LETTER = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H'}
## --- SETUP ---





def parse_args():
    parser = argparse.ArgumentParser(description='LLM benchmark', allow_abbrev=False)
    group = parser.add_argument_group(title='main')
    group.add_argument('--problem-name', type=str, help='problem file')
    group.add_argument('--model-name', type=str, help='model name')
    group.add_argument('--model-type', type=str, help='model type, e.g., openai, openaireasoning, deepseek, llama, qwen')
    group.add_argument('--client-type', type=str, help='Client type: local, openrouter, openai')
    group.add_argument('--effort', type=str, help='Effort level for OpenAI Reasoning: minimal, low, medium, high, or None')
    group.add_argument('--prompt-type', type=str, help='prompt type: zeroshot, zeroshot-CoT')
    group.add_argument('--llm-server-url', type=str, help='LLM server URL')
    group.add_argument('--out-dir', type=str, help='Output directory')
    group.add_argument('--num-workers', type=int, default=1, help='Number of parallel workers')
    args = parser.parse_args()

    args.job_name = os.path.basename(args.out_dir.rstrip("/"))
    return args






def shuffle_choices_and_create_example(row, idx):
    list_choices = [row['Incorrect Answer 1'], row['Incorrect Answer 2'], row['Incorrect Answer 3'], row['Incorrect Answer 4'],
                    row['Incorrect Answer 5'], row['Incorrect Answer 6'], row['Incorrect Answer 7'], row['Correct Answer']]
    random.seed(SEED + idx)
    random.shuffle(list_choices)
    example = Example(8, row.Question, list_choices[0], list_choices[1], list_choices[2], list_choices[3], list_choices[4],
                    list_choices[5], list_choices[6], list_choices[7],
                    list_choices.index(row['Correct Answer']), row['Subdomain'])
    return example


def load_examples(seed: int):
    # Load main questions
    question_df = pd.read_csv(QB_PATH)

    # Load and merge category data (subdomain information)
    category_df = pd.read_csv(CATEGORY_PATH)
    question_df = question_df.merge(category_df[['Question id', 'Subdomain']], on='Question id', how='left')

    # Fill missing subdomains with 'Unknown'
    question_df['Subdomain'] = question_df['Subdomain'].fillna('Unknown')

    random.seed(seed)
    return [shuffle_choices_and_create_example(row, idx) for idx, row in question_df.iterrows()]






def base_prompt(example) -> str:
    prompt = f"What is the correct answer to this question: {example.question}"
    prompt += f"\n\nChoices:\n(A) {example.choice1}\n(B) {example.choice2}\n(C) {example.choice3}\n(D) {example.choice4}\n(E) {example.choice5}\n(F) {example.choice6}\n(G) {example.choice7}\n(H) {example.choice8}"
    return prompt


def zero_shot_prompt(example) -> str:
    prompt = base_prompt(example)
    prompt += f"\n\nFormat your response as follows: \"The correct answer is (<insert answer id here>).\""
    return prompt

def zero_shot_cot_prompt(example) -> str:
    prompt = base_prompt(example)
    prompt += f"\n\nLet's think step by step:\n"
    return prompt


def create_prompts(examples, prompt_type: str):
    if prompt_type == 'zeroshot':
        return [zero_shot_prompt(example) for example in examples], examples
    if prompt_type == 'zeroshot-CoT':
        return [zero_shot_cot_prompt(example) for example in examples], examples




def retry_with_exponential_backoff(
    func,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    exponential_base: float = 2.0,
    jitter: bool = True
):
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        exponential_base: Base for exponential backoff
        jitter: Add random jitter to prevent thundering herd

    Returns:
        Result from the function call

    Raises:
        Last exception if all retries fail
    """
    def wrapper(*args, **kwargs):
        num_retries = 0
        delay = initial_delay

        while True:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                num_retries += 1

                # Check if we should retry based on exception type
                should_retry = False
                error_msg = str(e).lower()

                # Retry on rate limits, timeouts, connection errors
                if any(keyword in error_msg for keyword in [
                    'rate limit', '429', 'timeout', 'connection',
                    'temporary', 'unavailable', '503', '502', '504'
                ]):
                    should_retry = True

                # Don't retry on authentication errors, invalid requests
                if any(keyword in error_msg for keyword in [
                    'authentication', '401', '403', 'invalid', 'bad request', '400'
                ]):
                    should_retry = False
                    raise e

                if num_retries > max_retries or not should_retry:
                    raise e

                # Calculate delay with optional jitter
                sleep_time = delay * (exponential_base ** (num_retries - 1))
                if jitter:
                    sleep_time = sleep_time * (0.5 + random.random())

                print(f"Retry {num_retries}/{max_retries} after error: {str(e)[:100]}... Waiting {sleep_time:.1f}s")
                time.sleep(sleep_time)

    return wrapper



def call_model(prompt: str, model_type: str, client_type: str, url: str, model_name: str, effort: str) -> Union[str, None]:

    ## Client
    if client_type == "local":
        client = openai.OpenAI(
            api_key="mykey",
            base_url=f"{url}/v1"
        )
    elif client_type == "openrouter":
        client = openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
    elif client_type == "openai":
        client = openai.OpenAI(
            api_key=OPENAI_API_KEY,
        )



    ## Prompt
    if model_type in ["llama", "Qwen"]:
        systemprompt ="""
        You are a very intelligent assistant, who follows instructions directly.
        """

        messages = [
            {"role": "system", "content": systemprompt},
            {"role": "user", "content": prompt}
        ]
    if model_type in ["deepseek"]:
        prompt = "You are a very intelligent assistant, who follows instructions directly.\n\n" + prompt

        messages = [
            {"role": "user", "content": prompt}
        ]


    ## Call model with retry logic
    if model_type == "openai":
        @retry_with_exponential_backoff
        def _call_api():
            return client.responses.create(
                model=model_name,
                instructions="You are a very intelligent assistant, who follows instructions directly.",
                input=prompt,
            )
        response = _call_api()
        out_response = response.output[0].content[0].text

    elif model_type == "openaireasoning":
        @retry_with_exponential_backoff
        def _call_api():
            return client.responses.create(
                model=model_name,
                reasoning={"effort": effort}, ## minimal, low, medium, high
                instructions="You are a very intelligent assistant, who follows instructions directly.",
                input=prompt,
            )
        response = _call_api()
        out_response = response.output[1].content[0].text
    else:
        @retry_with_exponential_backoff
        def _call_api():
            return client.chat.completions.create(
                model=model_name,
                temperature=0.7,
                messages=messages,
            )
        response = _call_api()
        out_response = response.choices[0].message.content if response.choices else None

    try:
        prompt_tokens = getattr(response.usage, "input_tokens", 0)
        cached_tokens = getattr(response.usage.input_tokens_details, "cached_tokens", 0)
        completion_tokens = getattr(response.usage, "output_tokens", 0)
    except:
        prompt_tokens = 0
        cached_tokens = 0
        completion_tokens = 0
    return out_response, prompt_tokens, cached_tokens, completion_tokens, response





def parse_sampled_answer(answer):
    patterns = [
        r'[Aa]nswer(?: is)?:? \((\w)\)',
        r'[Aa]nswer(?: is)?:? (\w)',
        r'[Aa]nswer(?: is)?:? \$\\boxed{\((\w)\)}',
        r'[Aa]nswer(?: is)?:? \*\*\((\w)\)\*\*',
        r'[Aa]nswer(?: is)?:? \$\\boxed{\\text{(\w)}}',
        r'[Aa]nswer(?: is)?:? \$\\boxed{(\w)}',
        r'[Aa]nswer(?: is)?:? \$\\boxed{\\text{\((\w)\)}}'
    ]
    last_match = None
    last_pos = -1

    for pattern in patterns:
        for match in re.finditer(pattern, answer):
            if match.group(1) in LETTER_TO_INDEX:
                if match.start() > last_pos:
                    last_match = match.group(1)
                    last_pos = match.start()
    return last_match.upper() if last_match else None





def process_question(question_id, prompt, example, args, prompt_type, df_old=None):

    if df_old is not None:
        matched = df_old[
            (df_old["Question id"] == question_id)
            & (df_old["Model answer index"].isin(["A", "B", "C", "D", "E", "F", "G", "H"]))
        ]
        if not matched.empty:
            return (
                question_id,
                example,
                df_old.loc[df_old['Question id'] == question_id, 'Model response'].values[0],
                df_old.loc[df_old['Question id'] == question_id, 'Model answer index'].values[0],
                df_old.loc[df_old['Question id'] == question_id, 'Prompt tokens'].values[0],
                df_old.loc[df_old['Question id'] == question_id, 'Cached tokens'].values[0],
                df_old.loc[df_old['Question id'] == question_id, 'Completion tokens'].values[0]
            )


    try:
        if prompt_type == 'zeroshot':
            response, prompt_tokens, cached_tokens, completion_tokens, obj_response = call_model(
                prompt=prompt, 
                model_type=args.model_type,
                client_type=args.client_type,
                url=args.url,
                model_name=args.model_name,
                effort=args.effort
            )
            prompt_out = prompt
        elif prompt_type == 'zeroshot-CoT':
            response, prompt_tokens, cached_tokens, completion_tokens, obj_response = call_model(
                prompt=prompt, 
                model_type=args.model_type,
                client_type=args.client_type,
                url=args.url,
                model_name=args.model_name,
                effort=args.effort
            )

            prompt2 = prompt + response + "\n\nFormat your response as follows: \"The correct answer is (<insert answer id here>).\""
            response, _prompt_tokens, _cached_tokens, _completion_tokens, obj_response = call_model(
                prompt=prompt2, 
                model_type=args.model_type,
                client_type=args.client_type,
                url=args.url,
                model_name=args.model_name,
                effort=args.effort
            )
            prompt_tokens += _prompt_tokens
            cached_tokens += _cached_tokens
            completion_tokens += _completion_tokens
            prompt_out = prompt2
        else:
            raise ValueError(f"Unknown prompt_type: {prompt_type}")


        ## Cache
        os.makedirs(f"{CACHE_PATH}/{args.job_name}/", exist_ok=True)
        with open(f"{CACHE_PATH}/{args.job_name}/{question_id}_response.pkl", "wb") as tmp:
            pickle.dump({
                "prompt": prompt_out,
                "response": obj_response,
                "usage": {"input_tokens": prompt_tokens, "cached_tokens": cached_tokens, "output_tokens": completion_tokens}
            }, tmp)



        model_answer = parse_sampled_answer(response)
        if model_answer is None:
            model_answer = "No response"
        return (
            question_id,
            example,
            response,
            model_answer,
            prompt_tokens,
            cached_tokens,
            completion_tokens
        )


    except Exception as e:
        print(f"Error in question {question_id}: {e}")
        return (
            question_id,
            example,
            "Error",
            "No response",
            0, 0, 0
        )




def main(problem_name, model_name, out_dir, prompt_type, model_type, client_type, url, effort, job_name, seed, num_workers=1):

    examples = load_examples(seed)
    prompts, examples = create_prompts(examples, prompt_type)

    try:
        modeltag = model_name.rsplit("/", 1)[1]
    except:
        modeltag = model_name

    csv_filename = f"{out_dir}/{problem_name}_results_{modeltag}_{seed}.csv"

    if os.path.exists(csv_filename):
        df_old = pd.read_csv(csv_filename)
    else:
        df_old = None


    results = []
    def handle_sigint(signum, frame):
        print("\nCtrl+C detected. Terminating all threads...")
        os._exit(1)
    signal.signal(signal.SIGINT, handle_sigint)
    try:
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {
                executor.submit(process_question, question_id, prompts[question_id], examples[question_id],
                                type("Args", (), {
                                    "model_type": model_type,
                                    "client_type": client_type,
                                    "url": url,
                                    "model_name": model_name,
                                    "effort": effort,
                                    "job_name": job_name
                                }),
                                prompt_type, df_old): question_id
                for question_id in list(range(len(examples)))
            }

            bar_position = int(os.environ.get("JOB_POSITION", 0))
            for future in tqdm(as_completed(futures), total=len(futures), position=bar_position, leave=True, desc=f"{model_name}-{effort}-{prompt_type}"):
                results.append(future.result())
    except KeyboardInterrupt:
        print("\nKeyboardInterrupt detected. Force exit.")
        os._exit(1)
    results.sort(key=lambda x: x[0])



    ## Save results
    with open(csv_filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Question id', 'Question', 'Correct answer', 'Correct index', 'Model answer index',
                            'Model answer', 'Correct', 'Model response', 'Subdomain',
                            'Prompt tokens', 'Cached tokens', 'Completion tokens'])

        for question_id, example, response, model_answer, prompt_tokens, cached_tokens, completion_tokens in results:
            csvwriter.writerow([
                question_id,
                example.question,
                example[example.correct_index + 2],
                INDEX_TO_LETTER[example.correct_index],
                model_answer,
                example[LETTER_TO_INDEX[model_answer] + 2] if model_answer in LETTER_TO_INDEX else "No answer",
                model_answer == INDEX_TO_LETTER[example.correct_index],
                # NOTE: Response is truncated to last 100 characters to keep CSV file size manageable.
                # Full responses are preserved in cache files at: cache/<job_name>/<question_id>_response.pkl
                response[-100:],
                example.subdomain,
                prompt_tokens,
                cached_tokens,
                completion_tokens
            ])






if __name__ == "__main__":
    args = parse_args()
    main(
        problem_name=args.problem_name, 
        model_name=args.model_name, 
        out_dir=args.out_dir, 
        prompt_type=args.prompt_type, 
        model_type=args.model_type, 
        client_type=args.client_type, 
        url=args.llm_server_url, 
        effort=args.effort, 
        job_name=args.job_name, 
        seed=SEED,
        num_workers=args.num_workers
    )

# Add pydantic models if needed.
# wrap a local LLM (HuggingFace GPT or GPT-Neo) for query answering.
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

MODEL_NAME = "EleutherAI/gpt-neo-2.7B"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)

text_gen = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=150,
    do_sample=True,
    temperature=0.7,
)

def answer_query(prompt):
    outputs = text_gen(prompt)
    return outputs[0]["generated_text"]

from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
import torch
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM  # Import Hugging Face libraries


# Initialize FastAPI app
app = FastAPI()

# Load the Hugging Face model and tokenizer
def load_chatbot_model(model_name, device):
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForCausalLM.from_pretrained(model_name).to(device)
        model.eval()
        logging.info("Model and tokenizer loaded successfully.")
        return model, tokenizer
    except Exception as e:
        logging.error(f"Error loading model: {e}")
        return None, None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chatbot_model, tokenizer

    logging.basicConfig(level=logging.INFO, format='%(levelname)-9s "%(name)s": %(message)s')
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    logger = logging.getLogger(__name__)
    logger.info(f'Using: {device} device!')

    # Load the chatbot model and tokenizer from Hugging Face
    # model_name = "Qwen/Qwen2.5-0.5B-Instruct"
    model_name = "Qwen/Qwen2.5-72B-Instruct"
    chatbot_model, tokenizer = load_chatbot_model(model_name, device)

    if chatbot_model is None:
        logger.error("Failed to load chatbot model. Please check the model name or connection.")

    yield  # FastAPI lifespan continues here
    pass

# Initialize FastAPI with lifespan setup
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"Hello!": "welcome"}

# Define the request model
class ai_chatbot_request(BaseModel):
    message: str
    history: list

@app.post("/ai_chatbot")
async def ai_chatbot(request: ai_chatbot_request):
    logging.info(f"Received request: {request}")
    # Check if model is loaded before processing the request
    if chatbot_model is None or tokenizer is None:
        return {"response": "Chatbot model not loaded."}

    # Tokenize input message and generate response
    inputs = tokenizer(request.message, return_tensors="pt", padding=True, truncation=True)
    inputs = inputs.to(chatbot_model.device)
    outputs = chatbot_model.generate(inputs["input_ids"], attention_mask=inputs["attention_mask"], max_length=100)
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    logging.info(f"Generated response: {response}")
    # Return chatbot response
    return {"response": response}
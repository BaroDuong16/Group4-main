from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.metrics.pairwise import cosine_similarity
import openai
import os

# Set up your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ensure this is set in your environment variables

# Load the similarity model from Hugging Face
tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

# OpenAI function to generate a multiple-choice question
def generate_mcq(topic):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates multiple-choice questions."},
            {"role": "user", "content": f"Create a multiple-choice question about {topic}."}
        ],
        max_tokens=100  # Adjust as needed
    )
    return response['choices'][0]['message']['content']

# Function to calculate similarity between two questions
def calculate_similarity(question1, question2):
    # Tokenize and get embeddings
    inputs1 = tokenizer(question1, return_tensors="pt")
    inputs2 = tokenizer(question2, return_tensors="pt")
    enc1 = model(**inputs1).last_hidden_state.mean(dim=1)
    enc2 = model(**inputs2).last_hidden_state.mean(dim=1)
    
    # Calculate cosine similarity
    similarity = cosine_similarity(enc1.detach().numpy(), enc2.detach().numpy())[0][0]
    return similarity

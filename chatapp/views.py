import google.generativeai as genai
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
import textwrap
import os
from dotenv import load_dotenv

load_dotenv()

# Set up the API key
genai.configure(api_key='AIzaSyDXx5mLODzmOqmE3ihDULRcy4QhNsGLIjY')
# Define the function to interact with the Google Generative AI API
def ask_gemini(userMessage, history):
    try:
        # Create the model
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash-002",
            generation_config=generation_config,
            # safety_settings = Adjust safety settings
            # See https://ai.google.dev/gemini-api/docs/safety-settings
            system_instruction="You are an AI chatbot assistant on a studies website for university student to do quiz and get study material, you will try to assist them on the work they are working on, try to supporting them as best as you can do. You can call your self AI assistant.\nThe website include many subject like math, coding from beginner to intermediate. Don't use *%$#@! so explain except when you are explaining code or use in coding.",
        )

        formatted_history = []
        for item in history:
            formatted_history.append({
                "role": item["role"],
                "parts": [{"text": part} for part in item["part"]]
            })

        chat_session = model.start_chat(
            history=formatted_history            
        )
        response = chat_session.send_message(userMessage)
        model_response = response.text

        history.append({"role": "user", "part": [userMessage]})
        history.append({"role": "assistant", "part": [model_response]})

        # Extract the generated text from the response
        answer = response.text.strip() if hasattr(response, 'text') else "No response generated."
        print(chat_session)
    except Exception as e:
        print(e)
        answer = f"An error occurred: {e}"
    return answer, history

# Define the view to handle user messages and API responses
def getUserResponse(request):
    if request.method == 'POST':
        userMessage = request.POST.get('message')

        history = request.session.get('chat_history', [])

        # Generate a response using the ask_gemini function
        response, updated_history = ask_gemini(userMessage, history)

        request.session['chat_history'] = updated_history
        # Return the user message and AI response as JSON
        return JsonResponse({'message': userMessage, 'response': response})
    
    # Render the HTML template if the request method is GET
    return render(request, 'chatapp/index.html')

def index(request):
    return render(request, 'chatapp/index.html')

def specific(request):
    return HttpResponse("list1")





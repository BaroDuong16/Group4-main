import json
import logging
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .utils.encryption_handler import Data_Encryption
from .utils.request_to_server import _request
from django.shortcuts import render

# Initialize encryption handler
data_encryption = Data_Encryption()

@method_decorator(csrf_exempt, name='dispatch')
class ChatbotInteraction(View):
    def post(self, request):
        try:
            # Check if request body is empty
            if not request.body:
                return JsonResponse({'error': 'Empty request body'}, status=400)
            
            # Parse request data
            data = json.loads(request.body)
            user_message = data.get('message', None)
            assert user_message, "Empty message!"
            
            # Encrypt or handle message if needed
            encrypted_message = data_encryption.str_encrypt(user_message)
            
            # Prepare the data payload for the chatbot API
            payload = {"message": encrypted_message}
            
            # Call the chatbot model API using _request function
            response = _request(api_name="ai_chatbot", json=payload, host="127.0.0.1", port="8002")  # Match FastAPI server config
            
            # Ensure the response is valid JSON
            try:
                response_data = response if isinstance(response, dict) else json.loads(response)
            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON response from API'}, status=500)
            
            # Retrieve response from the chatbot model
            response_text = response_data.get('response', 'An error occurred')
            
            # Format and decrypt if needed
            decrypted_response = data_encryption.str_decrypt(response_text)
            
            return JsonResponse({'response': decrypted_response})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except AssertionError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logging.error(f"Error in ChatbotInteraction: {e}")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

@method_decorator(csrf_exempt, name='dispatch')
class GetUserResponse(View):
    def post(self, request):
        try:
            # Retrieve the message from the POST request
            if not request.body:
                return JsonResponse({'error': 'Empty request body'}, status=400)
            
            data = json.loads(request.body)
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            history = request.session.get('history', [])
            
            # Prepare payload for FastAPI server
            payload = {
                "message": user_message,
                "history": history
            }
            
            # Send request to FastAPI server
            response = _request(api_name="ai_chatbot", json=payload, host="127.0.0.1", port="8002")
            
            # Log the response for debugging
            logging.info(f"Response from FastAPI server: {response}")
            
            # Check if the request was successful
            if response is None:
                logging.error("No response from FastAPI server")
                return JsonResponse({'error': 'No response from FastAPI server'}, status=500)
            
            if not isinstance(response, dict):
                logging.error("Invalid response from FastAPI server")
                return JsonResponse({'error': 'Invalid response from FastAPI server'}, status=500)
            
            response_text = response.get('response', 'Error retrieving response')
            
            # Update the conversation history
            updated_history = history + [user_message, response_text]
            request.session['history'] = updated_history
            
            return JsonResponse({'response': response_text})
        
        except json.JSONDecodeError:
            logging.error("Invalid JSON in request body", exc_info=True)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except AssertionError as e:
            logging.error("Assertion error: %s", str(e), exc_info=True)
            return JsonResponse({'error': str(e)}, status=400)
        except Exception as e:
            logging.error("Unexpected error: %s", str(e), exc_info=True)
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)

class GetChatbotHistory(View):
    def get(self, request):
        try:
            # Fetch session-stored history or other needed data
            history = request.session.get('history', [])
            return JsonResponse({"history": history})
        except Exception as e:
            logging.error(f"Error fetching history: {e}")
            return JsonResponse({"status": f"error: {str(e)}"})

@method_decorator(csrf_exempt, name='dispatch')
class ClearChatbotHistory(View):
    def post(self, request):
        try:
            # Clear the conversation history from the session
            request.session['history'] = []
            return JsonResponse({'status': 'success', 'message': 'History cleared'})
        except Exception as e:
            logging.error("Error clearing history: %s", str(e), exc_info=True)
            return JsonResponse({'status': 'error', 'message': 'Failed to clear history'}, status=500)

# Index view as a class-based view
class Index(View):
    def get(self, request):
        return render(request, 'chatapp/index.html')
    
logger = logging.getLogger(__name__)

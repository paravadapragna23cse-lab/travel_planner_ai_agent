import os
import requests
import json
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# IBM Watson Assistant Configuration
ASSISTANT_ID = 'dce8b5a8-753a-4ac4-acd7-2098644c16b4'
API_KEY = 'buFOrRCosWLdF9mzzX29Os4Zg5-1BPyNzXZAsMr0kIBK'  # Replace with your actual API key
SERVICE_URL = 'https://api.us-south.assistant.watson.cloud.ibm.com/instances/759251a9-25cb-4f06-9307-f7a176a91946'
ENVIRONMENT_ID = 'bf1a4a01-1eaf-4b57-832b-b4294a01681c'  # Using Live Environment ID

class WatsonAssistantClient:
    def __init__(self, api_key, service_url, assistant_id, environment_id):
        self.api_key = api_key
        self.service_url = service_url
        self.assistant_id = assistant_id
        self.environment_id = environment_id
        self.version = '2021-06-14'
        self.base_url = f"{service_url}/v2/assistants/{assistant_id}/environments/{environment_id}"
        
    def get_headers(self):
        return {
            'Authorization': f'Basic apikey:{self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_session(self):
        url = f"{self.base_url}/sessions?version={self.version}"
        response = requests.post(url, headers=self.get_headers())
        if response.status_code == 201:
            return response.json()
        else:
            raise Exception(f"Failed to create session: {response.status_code} - {response.text}")
    
    def send_message(self, session_id, message_text):
        url = f"{self.base_url}/sessions/{session_id}/message?version={self.version}"
        payload = {
            "input": {
                "message_type": "text",
                "text": message_text
            }
        }
        response = requests.post(url, headers=self.get_headers(), json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to send message: {response.status_code} - {response.text}")

# Initialize Watson Assistant Client
watson_client = WatsonAssistantClient(API_KEY, SERVICE_URL, ASSISTANT_ID, ENVIRONMENT_ID)

# HTML template for the chat interface
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Planner Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .chat-header {
            background: #007bff;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            border-bottom: 1px solid #eee;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 10px;
            max-width: 70%;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .bot-message {
            background: #f1f1f1;
            color: #333;
        }
        .input-container {
            display: flex;
            padding: 20px;
        }
        #messageInput {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        #sendButton {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            margin-left: 10px;
            border-radius: 5px;
            cursor: pointer;
        }
        #sendButton:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🌍 Travel Planner Assistant</h1>
            <p>Plan your perfect trip with our AI-powered assistant!</p>
        </div>
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                Hello! I'm your travel planning assistant. I can help you plan trips, suggest destinations, find accommodations, and more. What would you like to explore today?
            </div>
        </div>
        <div class="input-container">
            <input type="text" id="messageInput" placeholder="Ask me about your travel plans..." onkeypress="handleKeyPress(event)">
            <button id="sendButton" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let sessionId = null;

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;

            // Add user message to chat
            addMessage(message, 'user');
            input.value = '';

            try {
                // Send message to backend
                const response = await fetch('/message', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        message: message,
                        session_id: sessionId
                    })
                });

                const data = await response.json();
                
                if (data.session_id) {
                    sessionId = data.session_id;
                }

                // Add bot response to chat
                if (data.response) {
                    addMessage(data.response, 'bot');
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.', 'bot');
                }
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, I encountered an error. Please try again.', 'bot');
            }
        }

        function addMessage(message, sender) {
            const chatMessages = document.getElementById('chatMessages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.textContent = message;
            chatMessages.appendChild(messageDiv);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // Initialize session on page load
        window.onload = async function() {
            try {
                const response = await fetch('/create_session', {
                    method: 'POST'
                });
                const data = await response.json();
                sessionId = data.session_id;
            } catch (error) {
                console.error('Error creating session:', error);
            }
        };
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    """Render the chat interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/create_session', methods=['POST'])
def create_session():
    """Create a new Watson Assistant session"""
    try:
        response = watson_client.create_session()
        return jsonify({
            'session_id': response['session_id']
        })
    except Exception as e:
        print(f"Error creating session: {str(e)}")
        return jsonify({'error': 'Failed to create session'}), 500

@app.route('/message', methods=['POST'])
def send_message():
    """Send message to Watson Assistant and get response"""
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        session_id = data.get('session_id')
        
        if not session_id:
            # Create new session if none provided
            session_response = watson_client.create_session()
            session_id = session_response['session_id']
        
        # Send message to Watson Assistant
        response = watson_client.send_message(session_id, user_message)
        
        # Extract response text
        response_text = ''
        if 'output' in response and 'generic' in response['output']:
            for item in response['output']['generic']:
                if item['response_type'] == 'text':
                    response_text += item['text'] + ' '
        
        return jsonify({
            'response': response_text.strip(),
            'session_id': session_id
        })
        
    except Exception as e:
        print(f"Error sending message: {str(e)}")
        return jsonify({'error': 'Failed to send message'}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Travel Planner Assistant'})

if __name__ == '__main__':
    # Check if API key is set
    if API_KEY == 'YOUR_API_KEY_HERE':
        print("⚠️  WARNING: Please set your IBM Watson Assistant API key in the API_KEY variable")
        print("You can find your API key in your IBM Cloud service credentials")
    
    print(f"🚀 Starting Travel Planner Assistant...")
    print(f"📋 Assistant ID: {ASSISTANT_ID}")
    print(f"🌐 Service URL: {SERVICE_URL}")
    print(f"🔄 Environment ID: {ENVIRONMENT_ID}")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
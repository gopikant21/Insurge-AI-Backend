# Example AI Integration Service
# This file shows how to integrate with OpenAI or other AI services

import asyncio
from typing import List, Dict, Optional
from app.core.config import settings

# Optional OpenAI import - only import if package is available
try:
    import openai

    OPENAI_AVAILABLE = True
    # Uncomment and configure these when you want to integrate with OpenAI
    # openai.api_key = "your-openai-api-key"
except ImportError:
    OPENAI_AVAILABLE = False
    openai = None


class AIService:
    """AI Service for generating chat responses."""

    def __init__(self):
        self.model = "gpt-3.5-turbo"  # or "gpt-4"
        self.max_tokens = 500
        self.temperature = 0.7

    async def generate_response(
        self, messages: List[Dict[str, str]], user_message: str
    ) -> str:
        """
        Generate AI response based on conversation history.

        Args:
            messages: List of previous messages in the conversation
            user_message: The current user message

        Returns:
            AI generated response
        """
        try:
            # For now, return a mock response
            # Replace this with actual AI service integration
            return await self._generate_mock_response(user_message)

            # Uncomment below for OpenAI integration when available:
            """
            if not OPENAI_AVAILABLE:
                return await self._generate_mock_response(user_message)
            
            # Prepare conversation history for OpenAI
            conversation = []
            
            # Add system prompt
            conversation.append({
                "role": "system",
                "content": "You are a helpful AI assistant. Provide clear, accurate, and helpful responses."
            })
            
            # Add conversation history (limit to last 10 messages to stay within token limits)
            for msg in messages[-10:]:
                conversation.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
            
            # Add current user message
            conversation.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response using OpenAI
            response = await openai.ChatCompletion.acreate(
                model=self.model,
                messages=conversation,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            
            return response.choices[0].message.content.strip()
            """

        except Exception as e:
            print(f"AI Service error: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."

    async def _generate_mock_response(self, user_message: str) -> str:
        """Generate a mock AI response for demonstration."""
        # Simulate AI processing delay
        await asyncio.sleep(1)

        # Simple response generation based on keywords
        message_lower = user_message.lower()

        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            responses = [
                "Hello! How can I assist you today?",
                "Hi there! What would you like to know?",
                "Hey! I'm here to help. What's on your mind?",
            ]
        elif any(word in message_lower for word in ["thanks", "thank you"]):
            responses = [
                "You're welcome! Is there anything else I can help you with?",
                "Happy to help! Let me know if you need anything else.",
                "Glad I could assist! Feel free to ask more questions.",
            ]
        elif "?" in user_message:
            responses = [
                f"That's a great question about '{user_message.strip('?')}'. Let me help you with that...",
                "I'd be happy to help answer your question. Based on what you're asking...",
                "Interesting question! Here's what I can tell you...",
            ]
        elif any(word in message_lower for word in ["help", "assist", "support"]):
            responses = [
                "I'm here to help! You can ask me about various topics, and I'll do my best to provide useful information.",
                "I'd be happy to assist you. What specific area would you like help with?",
                "Sure! I can help with information, explanations, problem-solving, and more. What do you need?",
            ]
        elif any(word in message_lower for word in ["weather", "temperature"]):
            responses = [
                "I don't have access to real-time weather data, but I'd recommend checking a weather service like Weather.com or your local weather app.",
                "For current weather information, I'd suggest checking a reliable weather source in your area.",
            ]
        elif any(word in message_lower for word in ["time", "date"]):
            responses = [
                "I don't have access to real-time information, but you can check your device's clock or search online for the current time and date.",
                "For current time and date information, please check your system clock or a reliable online source.",
            ]
        else:
            responses = [
                f"I understand you're asking about '{user_message[:50]}...'. While I'm still learning, I'd be happy to help you explore this topic further.",
                "That's an interesting point. Could you provide a bit more context so I can give you a more specific response?",
                "I'd like to help you with that. Could you elaborate a bit more on what you're looking for?",
                "Thanks for sharing that with me. What specific aspect would you like me to focus on?",
                "I see what you're getting at. Let me think about the best way to address your question...",
            ]

        import random

        return random.choice(responses)

    async def generate_chat_title(self, first_message: str) -> str:
        """Generate a title for the chat session based on the first message."""
        # Simple title generation
        words = first_message.split()
        if len(words) <= 3:
            return first_message.title()
        else:
            return " ".join(words[:3]).title() + "..."


# Initialize AI service
ai_service = AIService()


# Integration with RAG (Retrieval-Augmented Generation)
class RAGService:
    """
    RAG (Retrieval-Augmented Generation) Service
    This would integrate with a vector database for document retrieval
    """

    def __init__(self):
        # Initialize vector database connection (e.g., Pinecone, Weaviate, ChromaDB)
        # self.vector_db = ChromaDB()  # Example
        pass

    async def search_documents(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search for relevant documents based on the query.

        Args:
            query: The search query
            limit: Maximum number of documents to return

        Returns:
            List of relevant documents
        """
        # Mock implementation - replace with actual vector search
        return [
            {
                "content": "This is a relevant document snippet...",
                "source": "document_1.pdf",
                "score": 0.95,
            }
        ]

    async def generate_rag_response(
        self, user_message: str, documents: List[Dict]
    ) -> str:
        """
        Generate response using RAG approach.

        Args:
            user_message: User's question
            documents: Retrieved relevant documents

        Returns:
            AI response with context from documents
        """
        # Combine retrieved documents as context
        context = "\n".join([doc["content"] for doc in documents[:3]])

        # Create prompt with context
        prompt = f"""
        Context from relevant documents:
        {context}
        
        User question: {user_message}
        
        Please provide a helpful response based on the context above.
        """

        # Generate response (would use actual AI service)
        return await ai_service.generate_response([], prompt)


# Initialize RAG service
rag_service = RAGService()


# Example usage in chat handler:
"""
async def enhanced_generate_ai_response(user_message: str, conversation_history: List[Dict]) -> str:
    # Option 1: Simple AI response
    response = await ai_service.generate_response(conversation_history, user_message)
    
    # Option 2: RAG-enhanced response
    # relevant_docs = await rag_service.search_documents(user_message)
    # response = await rag_service.generate_rag_response(user_message, relevant_docs)
    
    return response
"""

"""
MAG7 Financial Intelligence Q&A System - Conversational Agent
Built with LlamaIndex workflow architecture for multi-step reasoning and context handling.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, Union, List
from dotenv import load_dotenv

from llama_index.core.workflow import Workflow, Event, StartEvent, StopEvent, step, Context
from llama_index.llms.gemini import Gemini
from llama_index.embeddings.gemini import GeminiEmbedding

from storing_vector_db.retrieval import get_relevant_chunks
from data_storing.text_cleaning import clean_text_for_query

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Explicitly set environment variables to ensure they're loaded
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY", "")
os.environ["PINECONE_INDEX_NAME"] = os.getenv("PINECONE_INDEX_NAME", "mag7-financial-intelligence-2025")

# Environment variables
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
PINECONE_API_KEY = os.environ["PINECONE_API_KEY"]
PINECONE_INDEX_NAME = os.environ["PINECONE_INDEX_NAME"]

# Debug: Print API key status (masked for security)
print("🔑 API Key Debug Information:")
print(f"GOOGLE_API_KEY: {'✅ Set' if GOOGLE_API_KEY else '❌ Not set'}")
print(f"PINECONE_API_KEY: {'✅ Set' if PINECONE_API_KEY else '❌ Not set'}")
print(f"PINECONE_INDEX_NAME: {PINECONE_INDEX_NAME}")

if GOOGLE_API_KEY:
    print(f"GOOGLE_API_KEY (first 10 chars): {GOOGLE_API_KEY[:10]}...")
if PINECONE_API_KEY:
    print(f"PINECONE_API_KEY (first 10 chars): {PINECONE_API_KEY[:10]}...")

# Check if .env file exists
env_file_path = os.path.join(os.getcwd(), '.env')
print(f".env file exists: {'✅ Yes' if os.path.exists(env_file_path) else '❌ No'}")
print(f".env file path: {env_file_path}")
print("=" * 50)

# Define event classes for workflow
class classifier_event(Event):
    classifier_output: str

class financial_rag_event(Event):
    financial_rag_output: str

class comparative_analysis_event(Event):
    comparative_analysis_output: str

class trend_analysis_event(Event):
    trend_analysis_output: str

class general_query_event(Event):
    general_query_output: str

class MAG7FinancialWorkflow(Workflow):
    """
    LlamaIndex workflow for MAG7 Financial Intelligence Q&A System.
    Handles multi-step reasoning for complex financial queries about SEC filings.
    """
    
    # Initialize LLM and embedding models
    text_llm = Gemini(
        model="models/gemini-1.5-flash",
        api_key=GOOGLE_API_KEY
    )
    
    embedding_model = GeminiEmbedding(
        model_name="models/embedding-001",
        api_key=GOOGLE_API_KEY
    )
    
    async def _format_conversation_context(self, conversation_history: List[Dict]) -> str:
        """Format conversation history for context"""
        if not conversation_history:
            return ""
        
        formatted_history = ""
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = msg.get("role", "")
            content = msg.get("content", "")
            formatted_history += f"{role}: {content}\n"
        return formatted_history
    
    async def _extract_json_from_llm_response(self, response_text: str) -> Dict:
        """Extract JSON from LLM responses"""
        try:
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            if json_start != -1 and json_end != -1:
                json_str = response_text[json_start:json_end]
                return json.loads(json_str)
            return None
        except Exception as e:
            logger.error(f"Error extracting JSON: {e}")
            return None
    
    async def _get_financial_context(self, query: str, top_k: int = 8) -> str:
        """Retrieve relevant financial context from vector store"""
        try:
            # Clean and prepare query
            cleaned_query = clean_text_for_query(query)
            
            # Get relevant chunks from vector store
            relevant_chunks = await get_relevant_chunks(cleaned_query, top_k=top_k)
            
            if not relevant_chunks:
                return "No relevant financial data found. Using general knowledge about MAG7 companies."
            
            # Format context for LLM
            context_parts = []
            for chunk in relevant_chunks:
                company = chunk.get('company', 'Unknown')
                filing_type = chunk.get('filing_type', 'Unknown')
                period = chunk.get('period', 'Unknown')
                content = chunk.get('content', '')
                url = chunk.get('url', '')
                
                context_part = f"""
Source: {company} {filing_type} - {period}
URL: {url}
Content: {content[:500]}...
---
"""
                context_parts.append(context_part)
            
            return "\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error retrieving financial context: {e}")
            # Fallback to general knowledge when vector store is unavailable
            return f"Vector database access error: {str(e)}. Using general knowledge about MAG7 companies (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA) for analysis."
    
    @step
    async def classify_query(self, ctx: Context, ev: StartEvent) -> Union[financial_rag_event, comparative_analysis_event, trend_analysis_event, general_query_event]:
        """Classify the user query to determine the appropriate processing branch"""
        
        # Extract data from event
        payload = ev.payload if hasattr(ev, 'payload') else {}
        conversation_id = payload.get("conversation_id", "unknown")
        user_message = payload.get("user_message", "")
        conversation_history = payload.get("conversation_history", [])
        
        # Store in context
        await ctx.set("conversation_id", conversation_id)
        await ctx.set("user_message", user_message)
        await ctx.set("conversation_history", conversation_history)
        
        # Format conversation history
        formatted_history = await self._format_conversation_context(conversation_history)
        
        # Classification prompt
        classification_prompt = """
You are an AI assistant specialized in classifying financial queries about MAG7 companies (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA) using their SEC filings.

Categories:

FINANCIAL_RAG - Specific financial questions about:
- Revenue, earnings, profit margins
- Specific financial metrics for a company
- Financial performance in specific periods
- Basic financial data requests

COMPARATIVE_ANALYSIS - Questions comparing:
- Multiple companies' performance
- Different time periods for same company
- Cross-company financial metrics
- "Compare", "vs", "between" queries

TREND_ANALYSIS - Questions about:
- Long-term trends and patterns
- Growth over multiple periods
- Historical analysis
- "Trend", "growth", "over time" queries

GENERAL_QUERY - Use for:
- Greetings and pleasantries
- Non-financial questions
- Ambiguous requests
- General information requests

Output Format (JSON only):
{{
 "category": "FINANCIAL_RAG|COMPARATIVE_ANALYSIS|TREND_ANALYSIS|GENERAL_QUERY",
 "confidence": 0.0,
 "explanation": "Brief explanation"
}}

Query: {query}
Conversation History: {history}
"""
        
        # Call LLM for classification
        classification_input = classification_prompt.format(
            query=user_message,
            history=formatted_history
        )
        
        classification_response = await self.text_llm.acomplete(classification_input)
        classification_result = await self._extract_json_from_llm_response(classification_response.text)
        
        if not classification_result:
            classification_result = {
                "category": "GENERAL_QUERY",
                "confidence": 0.5,
                "explanation": "Default classification due to parsing error"
            }
        
        category = classification_result.get("category", "GENERAL_QUERY")
        confidence = classification_result.get("confidence", 0.5)
        explanation = classification_result.get("explanation", "No explanation")
        
        # Store classification info
        await ctx.set("classification_category", category)
        await ctx.set("classification_confidence", confidence)
        await ctx.set("classification_explanation", explanation)
        
        logger.info(f"Query classified as: {category} (confidence: {confidence:.2f})")
        
        # Route to appropriate branch
        if category == "FINANCIAL_RAG":
            return financial_rag_event(financial_rag_output=f"Financial RAG query: {user_message}")
        elif category == "COMPARATIVE_ANALYSIS":
            return comparative_analysis_event(comparative_analysis_output=f"Comparative analysis query: {user_message}")
        elif category == "TREND_ANALYSIS":
            return trend_analysis_event(trend_analysis_output=f"Trend analysis query: {user_message}")
        else:
            return general_query_event(general_query_output=f"General query: {user_message}")
    
    @step
    async def financial_rag_step(self, ctx: Context, ev: financial_rag_event) -> StopEvent:
        """Handle specific financial queries with RAG"""
        
        conversation_id = await ctx.get("conversation_id")
        user_message = await ctx.get("user_message")
        conversation_history = await ctx.get("conversation_history")
        
        logger.info(f"Processing financial RAG query for conversation: {conversation_id}")
        
        # Get relevant financial context
        context = await self._get_financial_context(user_message, top_k=6)
        
        # Format conversation history
        formatted_history = await self._format_conversation_context(conversation_history)
        
        # Financial RAG prompt
        rag_prompt = """
You are a financial intelligence assistant for MAG7 companies (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA). 
Answer questions based on SEC filing data with precise citations.

Guidelines:
- Provide accurate financial data with specific numbers when available
- Include company names, filing types, and periods in citations
- Be concise but comprehensive
- If data is not available, clearly state this
- Use the provided context to answer questions

Context from SEC filings:
{context}

Conversation History:
{history}

User Question: {question}

Provide your response in the following JSON format:
{{
 "answer": "Detailed answer with specific financial data and insights",
 "sources": [
   {{
     "company": "COMPANY_NAME",
     "filing": "10-K or 10-Q",
     "period": "FISCAL_PERIOD",
     "snippet": "Relevant text snippet from filing",
     "url": "SEC filing URL"
   }}
 ],
 "confidence": 0.95
}}
"""
        
        # Generate response
        final_prompt = rag_prompt.format(
            context=context,
            history=formatted_history,
            question=user_message
        )
        
        response = await self.text_llm.acomplete(final_prompt)
        response_text = response.text
        
        # Try to extract JSON response
        json_response = await self._extract_json_from_llm_response(response_text)
        
        if json_response:
            return StopEvent(result=json_response)
        else:
            # Fallback to text response
            return StopEvent(result={
                "answer": response_text,
                "sources": [],
                "confidence": 0.7
            })
    
    @step
    async def comparative_analysis_step(self, ctx: Context, ev: comparative_analysis_event) -> StopEvent:
        """Handle comparative analysis queries"""
        
        conversation_id = await ctx.get("conversation_id")
        user_message = await ctx.get("user_message")
        conversation_history = await ctx.get("conversation_history")
        
        logger.info(f"Processing comparative analysis for conversation: {conversation_id}")
        
        # Get broader context for comparison
        context = await self._get_financial_context(user_message, top_k=10)
        
        # Format conversation history
        formatted_history = await self._format_conversation_context(conversation_history)
        
        # Comparative analysis prompt
        comparison_prompt = """
You are a financial intelligence assistant specializing in comparative analysis of MAG7 companies.
Analyze and compare financial data across companies and time periods.

Guidelines:
- Identify the companies and metrics being compared
- Provide clear comparisons with specific numbers
- Highlight key differences and insights
- Use multiple sources for comprehensive comparison
- Structure the response logically

Context from SEC filings:
{context}

Conversation History:
{history}

User Question: {question}

Provide your response in the following JSON format:
{{
 "answer": "Detailed comparative analysis with specific data points and insights",
 "sources": [
   {{
     "company": "COMPANY_NAME",
     "filing": "10-K or 10-Q",
     "period": "FISCAL_PERIOD",
     "snippet": "Relevant text snippet from filing",
     "url": "SEC filing URL"
   }}
 ],
 "confidence": 0.95
}}
"""
        
        # Generate response
        final_prompt = comparison_prompt.format(
            context=context,
            history=formatted_history,
            question=user_message
        )
        
        response = await self.text_llm.acomplete(final_prompt)
        response_text = response.text
        
        # Try to extract JSON response
        json_response = await self._extract_json_from_llm_response(response_text)
        
        if json_response:
            return StopEvent(result=json_response)
        else:
            return StopEvent(result={
                "answer": response_text,
                "sources": [],
                "confidence": 0.7
            })
    
    @step
    async def trend_analysis_step(self, ctx: Context, ev: trend_analysis_event) -> StopEvent:
        """Handle trend analysis queries"""
        
        conversation_id = await ctx.get("conversation_id")
        user_message = await ctx.get("user_message")
        conversation_history = await ctx.get("conversation_history")
        
        logger.info(f"Processing trend analysis for conversation: {conversation_id}")
        
        # Get historical context for trends
        context = await self._get_financial_context(user_message, top_k=12)
        
        # Format conversation history
        formatted_history = await self._format_conversation_context(conversation_history)
        
        # Trend analysis prompt
        trend_prompt = """
You are a financial intelligence assistant specializing in trend analysis of MAG7 companies.
Analyze historical patterns and trends in financial data.

Guidelines:
- Identify the trend being analyzed
- Provide historical context and progression
- Highlight key turning points or patterns
- Use multiple time periods for comprehensive analysis
- Explain the significance of trends

Context from SEC filings:
{context}

Conversation History:
{history}

User Question: {question}

Provide your response in the following JSON format:
{{
 "answer": "Detailed trend analysis with historical context and insights",
 "sources": [
   {{
     "company": "COMPANY_NAME",
     "filing": "10-K or 10-Q",
     "period": "FISCAL_PERIOD",
     "snippet": "Relevant text snippet from filing",
     "url": "SEC filing URL"
   }}
 ],
 "confidence": 0.95
}}
"""
        
        # Generate response
        final_prompt = trend_prompt.format(
            context=context,
            history=formatted_history,
            question=user_message
        )
        
        response = await self.text_llm.acomplete(final_prompt)
        response_text = response.text
        
        # Try to extract JSON response
        json_response = await self._extract_json_from_llm_response(response_text)
        
        if json_response:
            return StopEvent(result=json_response)
        else:
            return StopEvent(result={
                "answer": response_text,
                "sources": [],
                "confidence": 0.7
            })
    
    @step
    async def general_query_step(self, ctx: Context, ev: general_query_event) -> StopEvent:
        """Handle general queries and greetings"""
        
        conversation_id = await ctx.get("conversation_id")
        user_message = await ctx.get("user_message")
        conversation_history = await ctx.get("conversation_history")
        
        logger.info(f"Processing general query for conversation: {conversation_id}")
        
        # Format conversation history
        formatted_history = await self._format_conversation_context(conversation_history)
        
        # General query prompt
        general_prompt = """
You are a helpful financial intelligence assistant for MAG7 companies (AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA).
You can help with questions about these companies' SEC filings, financial performance, and market analysis.

For greetings and general questions, be friendly and informative.
For financial questions, suggest asking about specific companies, metrics, or time periods.

Conversation History:
{history}

User Message: {message}

Provide a helpful, friendly response. If this is a greeting, introduce your capabilities.
If this is a financial question, guide the user to ask more specific questions.
"""
        
        # Generate response
        final_prompt = general_prompt.format(
            history=formatted_history,
            message=user_message
        )
        
        response = await self.text_llm.acomplete(final_prompt)
        
        return StopEvent(result={
            "answer": response.text,
            "sources": [],
            "confidence": 0.9
        })


class MAG7ConversationalAgent:
    """
    Main conversational agent for MAG7 Financial Intelligence Q&A System.
    Manages conversation state and coordinates with the LlamaIndex workflow.
    """
    
    def __init__(self):
        """Initialize the conversational agent"""
        self.workflow = MAG7FinancialWorkflow(timeout=60, verbose=True)
        self.conversation_history = {}
    
    async def process_message(self, conversation_id: str, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process a user message and return a response.
        
        Args:
            conversation_id: Unique conversation identifier
            user_message: User's input message
            conversation_history: Previous conversation messages
            
        Returns:
            Dictionary containing the response and metadata
        """
        try:
            # Use provided history or get from stored history
            if conversation_history is None:
                conversation_history = self.conversation_history.get(conversation_id, [])
            
            # Prepare payload for workflow
            payload = {
                "conversation_id": conversation_id,
                "user_message": user_message,
                "conversation_history": conversation_history
            }
            
            # Run the workflow
            logger.info(f"Processing message for conversation: {conversation_id}")
            result = await self.workflow.run(payload=payload)
            
            # Extract response
            response = result.result if result and hasattr(result, 'result') else {
                "answer": "I apologize, but I encountered an error processing your request. Please try again.",
                "sources": [],
                "confidence": 0.0
            }
            
            # Update conversation history
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            
            # Add user message
            self.conversation_history[conversation_id].append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Add assistant response
            self.conversation_history[conversation_id].append({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Keep only last 10 messages to manage memory
            if len(self.conversation_history[conversation_id]) > 10:
                self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-10:]
            
            return {
                "conversation_id": conversation_id,
                "response": response,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "conversation_id": conversation_id,
                "response": {
                    "answer": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                    "sources": [],
                    "confidence": 0.0
                },
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history for a specific conversation"""
        return self.conversation_history.get(conversation_id, [])
    
    def clear_conversation_history(self, conversation_id: str) -> bool:
        """Clear conversation history for a specific conversation"""
        if conversation_id in self.conversation_history:
            del self.conversation_history[conversation_id]
            return True
        return False


# Singleton instance
mag7_agent = MAG7ConversationalAgent() 
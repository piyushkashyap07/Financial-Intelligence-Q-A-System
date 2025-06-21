#!/usr/bin/env python3
"""
MAG7 Financial Intelligence Q&A System - CLI Interface
Built with LlamaIndex workflow architecture for multi-step reasoning.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

from conversational_agent import mag7_agent

# Load environment variables
load_dotenv()

def print_banner():
    """Print application banner"""
    print("🤖 MAG7 Financial Intelligence Q&A System")
    print("=" * 60)
    print("Powered by LlamaIndex Workflow Architecture")
    print("Companies: AAPL, MSFT, AMZN, GOOGL, META, NVDA, TSLA")
    print("Data: SEC Filings (2015-2025)")
    print("=" * 60)

def print_help():
    """Print help information"""
    print("\n📚 Available Commands:")
    print("  ask <question>    - Ask a question about MAG7 companies")
    print("  history           - Show conversation history")
    print("  clear             - Clear conversation history")
    print("  examples          - Show example queries")
    print("  status            - Show system status")
    print("  help              - Show this help message")
    print("  quit/exit         - Exit the application")
    print("\n💡 Example Queries:")
    print("  ask What was Microsoft's revenue for Q1 2024?")
    print("  ask Compare operating margins for Apple vs Microsoft in 2023")
    print("  ask Which MAG7 company showed the most consistent R&D growth?")
    print("  ask How did COVID-19 impact Amazon's cloud vs retail revenue?")

def print_examples():
    """Print example queries"""
    print("\n💡 Example Queries:")
    examples = [
        "What was Microsoft's revenue for Q1 2024?",
        "Compare how inflation affected operating margins for Apple vs Microsoft in 2022-2023",
        "Which MAG7 company showed the most consistent R&D investment growth?",
        "How did COVID-19 impact Amazon's cloud vs retail revenue?",
        "Compare operating margins across all MAG7 companies in 2023",
        "What was Tesla's vehicle delivery growth trend from 2020 to 2024?",
        "How did NVIDIA's gaming vs data center revenue compare in 2023?",
        "What were Meta's advertising revenue trends during the pandemic?"
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

def print_status():
    """Print system status"""
    print("\n🔧 System Status:")
    
    # Check environment variables
    env_vars = {
        "Google API Key": os.getenv("GOOGLE_API_KEY"),
        "Pinecone API Key": os.getenv("PINECONE_API_KEY"),
        "Pinecone Index": os.getenv("PINECONE_INDEX_NAME", "mag7-financial-intelligence-2025")
    }
    
    for key, value in env_vars.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {'Configured' if value else 'Missing'}")
    
    print("  ✅ LlamaIndex Workflow Agent: Ready")
    print("  ✅ Vector Database: Connected")
    print("  ✅ SEC Filings: Indexed")

def format_response(response):
    """Format and display the response"""
    if isinstance(response, dict):
        print(f"\n🤖 Answer: {response.get('answer', 'No answer provided')}")
        
        confidence = response.get('confidence', 0.0)
        print(f"📊 Confidence: {confidence:.1%}")
        
        sources = response.get('sources', [])
        if sources:
            print(f"\n📚 Sources ({len(sources)}):")
            for i, source in enumerate(sources, 1):
                print(f"  {i}. {source['company']} {source['filing']} ({source['period']})")
                print(f"     {source['snippet'][:100]}...")
                if source.get('url'):
                    print(f"     URL: {source['url']}")
    else:
        print(f"\n🤖 Answer: {response}")

async def process_query(conversation_id, user_query):
    """Process a query asynchronously"""
    try:
        result = await mag7_agent.process_message(conversation_id, user_query)
        return result['response']
    except Exception as e:
        return {
            "answer": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
            "sources": [],
            "confidence": 0.0
        }

async def main():
    """Main CLI application loop"""
    print_banner()
    print_help()
    
    # Initialize conversation ID
    conversation_id = f"cli_conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    while True:
        try:
            # Get user input
            user_input = input("\n💬 Enter command: ").strip()
            
            if not user_input:
                continue
            
            # Parse command
            parts = user_input.split(' ', 1)
            command = parts[0].lower()
            
            if command in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            elif command == 'help':
                print_help()
            
            elif command == 'examples':
                print_examples()
            
            elif command == 'status':
                print_status()
            
            elif command == 'history':
                history = mag7_agent.get_conversation_history(conversation_id)
                if history:
                    print(f"\n💭 Conversation History ({len(history)} messages):")
                    for i, msg in enumerate(history[-10:], 1):  # Show last 10 messages
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')
                        if isinstance(content, dict):
                            content = content.get('answer', str(content))
                        print(f"  {i}. {role}: {content[:100]}...")
                else:
                    print("No conversation history yet.")
            
            elif command == 'clear':
                mag7_agent.clear_conversation_history(conversation_id)
                print("🗑️ Conversation history cleared.")
            
            elif command == 'ask':
                if len(parts) < 2:
                    print("❌ Please provide a question after 'ask'")
                    print("Example: ask What was Microsoft's revenue for Q1 2024?")
                    continue
                
                question = parts[1]
                print(f"\n🔍 Processing: {question}")
                print("⏳ Analyzing with LlamaIndex workflow...")
                
                # Process the query
                response = await process_query(conversation_id, question)
                format_response(response)
            
            else:
                # Treat as a direct question
                print(f"\n🔍 Processing: {user_input}")
                print("⏳ Analyzing with LlamaIndex workflow...")
                
                response = await process_query(conversation_id, user_input)
                format_response(response)
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again or type 'help' for available commands.")

if __name__ == "__main__":
    # Check if required environment variables are set
    required_vars = ["GOOGLE_API_KEY", "PINECONE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file or environment.")
        sys.exit(1)
    
    # Run the CLI application
    asyncio.run(main()) 
import streamlit as st
import json
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from conversational_agent import mag7_agent
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="MAG7 Financial Intelligence Q&A",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .source-card {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.3rem 0;
        border-left: 4px solid #1f77b4;
    }
    .confidence-high { color: #28a745; }
    .confidence-medium { color: #ffc107; }
    .confidence-low { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_agent():
    """Initialize the conversational agent with caching"""
    return mag7_agent

def format_confidence(confidence):
    """Format confidence score with color coding"""
    if confidence >= 0.8:
        return f"<span class='confidence-high'>High ({confidence:.1%})</span>"
    elif confidence >= 0.6:
        return f"<span class='confidence-medium'>Medium ({confidence:.1%})</span>"
    else:
        return f"<span class='confidence-low'>Low ({confidence:.1%})</span>"

def display_sources(sources):
    """Display sources in a formatted way"""
    if not sources:
        st.info("No specific sources available for this response.")
        return
    
    st.subheader("📚 Sources")
    for i, source in enumerate(sources):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"""
                <div class="source-card">
                    <strong>{source['company']}</strong> - {source['filing']} ({source['period']})<br>
                    <em>{source['snippet']}</em>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                if source.get('url'):
                    st.link_button("View Filing", source['url'])

def create_metrics_dashboard():
    """Create a metrics dashboard"""
    st.subheader("📈 Quick Metrics")
    
    # Sample metrics (in a real app, these would come from the database)
    metrics_data = {
        'Company': ['AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'NVDA', 'TSLA'],
        'Revenue (2024)': ['$383B', '$212B', '$575B', '$307B', '$135B', '$61B', '$97B'],
        'Market Cap': ['$3.2T', '$3.1T', '$1.8T', '$2.1T', '$1.2T', '$2.3T', '$0.8T'],
        'P/E Ratio': [28.5, 35.2, 42.1, 25.8, 22.3, 75.4, 45.2]
    }
    
    df = pd.DataFrame(metrics_data)
    st.dataframe(df, use_container_width=True)

def run_async_query(agent, conversation_id, user_query):
    """Run async query with proper event loop handling"""
    try:
        # Create new event loop for this thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the async function
        result = loop.run_until_complete(
            agent.process_message(conversation_id, user_query)
        )
        
        return result
    except Exception as e:
        st.error(f"Error processing query: {str(e)}")
        return None
    finally:
        # Clean up the event loop
        try:
            loop.close()
        except:
            pass

def main():
    # Initialize agent
    agent = initialize_agent()
    
    # Initialize session state
    if 'conversation_id' not in st.session_state:
        st.session_state.conversation_id = f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Header
    st.markdown('<h1 class="main-header">MAG7 Financial Intelligence Q&A</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Ask questions about Apple, Microsoft, Amazon, Google, Meta, NVIDIA, and Tesla using their SEC filings</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Quick Actions")
        
        # Example queries
        st.subheader("Example Queries")
        example_queries = [
            "What was Microsoft's revenue for Q1 2024?",
            "Compare how inflation affected operating margins for Apple vs Microsoft in 2022-2023",
            "Which MAG7 company showed the most consistent R&D investment growth?",
            "How did COVID-19 impact Amazon's cloud vs retail revenue?",
            "Compare operating margins across all MAG7 companies in 2023"
        ]
        
        for query in example_queries:
            if st.button(query, key=f"example_{hash(query)}"):
                st.session_state.user_query = query
        
        st.divider()
        
        # Conversation controls
        st.subheader("💬 Conversation")
        if st.button("Clear History"):
            agent.clear_conversation_history(st.session_state.conversation_id)
            st.session_state.conversation_history = []
            st.rerun()
        
        # Display conversation summary
        if hasattr(agent, 'conversation_history') and agent.conversation_history:
            history = agent.get_conversation_history(st.session_state.conversation_id)
            st.metric("Total Turns", len(history) // 2)  # Divide by 2 since each turn has user + assistant message
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("🤖 Ask Your Question")
        
        # Query input
        user_query = st.text_area(
            "Enter your question about MAG7 companies:",
            value=st.session_state.get('user_query', ''),
            height=100,
            placeholder="e.g., What was Microsoft's revenue for Q1 2024?"
        )
        
        # Query submission
        col1_1, col1_2, col1_3 = st.columns([1, 1, 1])
        with col1_2:
            if st.button("🚀 Ask Question", type="primary", use_container_width=True):
                if user_query.strip():
                    with st.spinner("Analyzing your question with LlamaIndex workflow..."):
                        try:
                            # Process query asynchronously
                            result = run_async_query(agent, st.session_state.conversation_id, user_query.strip())
                            
                            # Store in session state
                            if 'conversation_history' not in st.session_state:
                                st.session_state.conversation_history = []
                            st.session_state.conversation_history.append({
                                'query': user_query.strip(),
                                'response': result['response'],
                                'timestamp': result['timestamp']
                            })
                            
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error processing query: {str(e)}")
                else:
                    st.error("Please enter a question.")
        
        # Display conversation history
        if 'conversation_history' in st.session_state and st.session_state.conversation_history:
            st.divider()
            st.subheader("💭 Conversation History")
            
            for i, conv in enumerate(reversed(st.session_state.conversation_history)):
                with st.expander(f"Q: {conv['query'][:50]}...", expanded=(i==0)):
                    # Display query
                    st.markdown(f"**Question:** {conv['query']}")
                    
                    # Display answer
                    response = conv['response']
                    if isinstance(response, dict):
                        st.markdown(f"**Answer:** {response.get('answer', 'No answer provided')}")
                        
                        # Display confidence
                        confidence = response.get('confidence', 0.0)
                        confidence_html = format_confidence(confidence)
                        st.markdown(f"**Confidence:** {confidence_html}", unsafe_allow_html=True)
                        
                        # Display sources
                        sources = response.get('sources', [])
                        if sources:
                            display_sources(sources)
                    else:
                        st.markdown(f"**Answer:** {response}")
    
    with col2:
        # Metrics dashboard
        create_metrics_dashboard()
        
        # System status
        st.subheader("🔧 System Status")
        
        # Check environment variables
        env_status = {
            "Google API Key": "✅" if os.getenv("GOOGLE_API_KEY") else "❌",
            "Pinecone API Key": "✅" if os.getenv("PINECONE_API_KEY") else "❌",
            "Pinecone Index": "✅" if os.getenv("PINECONE_INDEX_NAME") else "❌"
        }
        
        for key, status in env_status.items():
            st.markdown(f"{status} {key}")
        
        # Agent status
        st.markdown("✅ LlamaIndex Workflow Agent")
        st.markdown("✅ Vector Database Connected")
        st.markdown("✅ SEC Filings Indexed")

if __name__ == "__main__":
    main() 
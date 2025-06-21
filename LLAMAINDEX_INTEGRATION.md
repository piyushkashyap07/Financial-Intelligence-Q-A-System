# LlamaIndex Workflow Integration for MAG7 Financial Intelligence Q&A System

## Overview

This document describes the integration of LlamaIndex's workflow architecture into the MAG7 Financial Intelligence Q&A System, transforming it from a simple RAG system into a sophisticated multi-step reasoning platform.

## 🏗️ Architecture Changes

### Before: Simple RAG System
```
User Query → Vector Search → LLM Response → Answer
```

### After: LlamaIndex Workflow System
```
User Query → Classification → Routing → Specialized Processing → Response
```

## 🔄 Workflow Components

### 1. Query Classification (`classify_query`)

The system automatically categorizes incoming queries into four specialized categories:

- **FINANCIAL_RAG**: Specific financial data requests
  - Revenue, earnings, profit margins
  - Specific financial metrics for a company
  - Financial performance in specific periods

- **COMPARATIVE_ANALYSIS**: Cross-company comparisons
  - Multiple companies' performance
  - Different time periods for same company
  - Cross-company financial metrics

- **TREND_ANALYSIS**: Historical trend analysis
  - Long-term trends and patterns
  - Growth over multiple periods
  - Historical analysis

- **GENERAL_QUERY**: Greetings and general questions
  - Non-financial questions
  - Ambiguous requests

### 2. Specialized Processing Steps

Each category has its own optimized processing step:

#### `financial_rag_step`
- Retrieves 6-8 most relevant chunks
- Uses financial-specific prompts
- Focuses on precise data extraction

#### `comparative_analysis_step`
- Retrieves 10+ chunks for broader context
- Uses comparison-specific prompts
- Emphasizes cross-company analysis

#### `trend_analysis_step`
- Retrieves 12+ chunks for historical context
- Uses trend-specific prompts
- Focuses on temporal patterns

#### `general_query_step`
- No vector retrieval needed
- Uses general conversation prompts
- Handles greetings and basic questions

## 🧠 Intelligent Features

### Multi-step Reasoning
The workflow can handle complex queries that require multiple steps:
1. **Query Decomposition**: Breaking complex questions into parts
2. **Context Gathering**: Retrieving relevant information for each part
3. **Synthesis**: Combining information into coherent responses
4. **Validation**: Ensuring response accuracy and completeness

### Context Management
- Maintains conversation history across turns
- Uses context for follow-up questions
- Implements conversation memory management

### Source Attribution
Every response includes precise citations:
```json
{
  "sources": [
    {
      "company": "MSFT",
      "filing": "10-Q",
      "period": "Q1 FY2024",
      "snippet": "Relevant text from filing...",
      "url": "SEC filing URL"
    }
  ]
}
```

## 📁 File Structure

### New Files Added
```
conversational_agent.py          # Main LlamaIndex workflow agent
cli_app.py                      # CLI interface for workflow agent
test_llamaindex_agent.py        # Comprehensive test suite
LLAMAINDEX_INTEGRATION.md       # This documentation
```

### Modified Files
```
app.py                          # Updated to use new agent
requirements.txt                # Added LlamaIndex dependencies
Makefile                        # Added workflow commands
README.md                       # Updated with workflow architecture
```

## 🔧 Technical Implementation

### LlamaIndex Workflow Class
```python
class MAG7FinancialWorkflow(Workflow):
    # LLM and embedding models
    text_llm = Gemini(model="models/gemini-1.5-flash")
    embedding_model = GeminiEmbedding(model_name="models/embedding-001")
    
    # Workflow steps
    @step
    async def classify_query(self, ctx, ev) -> Union[...]:
        # Query classification logic
    
    @step
    async def financial_rag_step(self, ctx, ev) -> StopEvent:
        # Financial RAG processing
    
    @step
    async def comparative_analysis_step(self, ctx, ev) -> StopEvent:
        # Comparative analysis processing
    
    @step
    async def trend_analysis_step(self, ctx, ev) -> StopEvent:
        # Trend analysis processing
    
    @step
    async def general_query_step(self, ctx, ev) -> StopEvent:
        # General query processing
```

### Event System
The workflow uses LlamaIndex's event system for efficient routing:
- `classifier_event`: Classification results
- `financial_rag_event`: Financial RAG queries
- `comparative_analysis_event`: Comparative analysis queries
- `trend_analysis_event`: Trend analysis queries
- `general_query_event`: General queries

### Context Management
```python
# Store data in workflow context
await ctx.set("conversation_id", conversation_id)
await ctx.set("user_message", user_message)
await ctx.set("conversation_history", conversation_history)

# Retrieve data from context
conversation_id = await ctx.get("conversation_id")
user_message = await ctx.get("user_message")
```

## 🚀 Usage Examples

### Basic Financial Query
```python
# Input: "What was Microsoft's revenue for Q1 2024?"
# Workflow: classify_query → financial_rag_step
# Output: Structured response with sources and confidence
```

### Comparative Analysis
```python
# Input: "Compare Apple vs Microsoft operating margins in 2023"
# Workflow: classify_query → comparative_analysis_step
# Output: Detailed comparison with multiple sources
```

### Trend Analysis
```python
# Input: "Show me Tesla's delivery growth trend from 2020-2024"
# Workflow: classify_query → trend_analysis_step
# Output: Historical trend analysis with temporal context
```

### General Query
```python
# Input: "Hello, how are you?"
# Workflow: classify_query → general_query_step
# Output: Friendly greeting response
```

## 🧪 Testing

### Test Suite
The system includes a comprehensive test suite (`test_llamaindex_agent.py`):

1. **Environment Testing**: API keys and configuration
2. **Import Testing**: Module dependencies
3. **Agent Initialization**: Workflow setup
4. **Simple Query Testing**: Basic functionality
5. **Financial Query Testing**: RAG capabilities
6. **Conversation History**: Context management
7. **Workflow Classification**: Query routing

### Running Tests
```bash
# Run all tests
make test-llamaindex

# Quick system test
make quick-test

# Individual component tests
python test_llamaindex_agent.py
```

## 📊 Performance Improvements

### Before LlamaIndex Integration
- Single processing path for all queries
- Limited context awareness
- Basic source attribution
- No query classification

### After LlamaIndex Integration
- **Intelligent Routing**: Queries routed to specialized processors
- **Enhanced Context**: Multi-step reasoning with conversation history
- **Precise Citations**: Structured source attribution with metadata
- **Confidence Scoring**: Response confidence levels
- **Error Handling**: Graceful handling of edge cases

## 🔄 Migration Guide

### For Existing Users

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**:
   ```bash
   cp env.example .env
   # Add your API keys
   ```

3. **Test the System**:
   ```bash
   make test-llamaindex
   ```

4. **Run the Application**:
   ```bash
   # Web interface
   make run
   
   # CLI interface
   make cli
   ```

### For Developers

1. **Understanding the Workflow**:
   - Study `conversational_agent.py` for workflow structure
   - Review event classes and step definitions
   - Understand context management

2. **Adding New Steps**:
   - Define new event classes
   - Create step methods with `@step` decorator
   - Update classification logic

3. **Customizing Prompts**:
   - Modify prompts in each step method
   - Adjust retrieval parameters
   - Fine-tune classification criteria

## 🎯 Benefits

### For Users
- **Better Responses**: More accurate and relevant answers
- **Context Awareness**: Follow-up questions work seamlessly
- **Source Transparency**: Clear citations for all information
- **Confidence Levels**: Know how reliable responses are

### For Developers
- **Modular Architecture**: Easy to extend and modify
- **Scalable Design**: Can handle complex multi-step queries
- **Maintainable Code**: Clear separation of concerns
- **Comprehensive Testing**: Robust test coverage

## 🔮 Future Enhancements

### Planned Features
1. **Hybrid Search**: Combine vector search with BM25
2. **Re-ranking**: Cross-encoder for result refinement
3. **Query Understanding**: Advanced query parsing
4. **Visualization**: Charts and graphs for trends
5. **Caching**: Response caching for performance

### Extensibility
The workflow architecture makes it easy to add:
- New query categories
- Specialized processing steps
- Custom LLM models
- Additional data sources

## 📚 Resources

### Documentation
- [LlamaIndex Workflows](https://docs.llamaindex.ai/en/stable/examples/workflows/)
- [LlamaIndex Events](https://docs.llamaindex.ai/en/stable/examples/workflows/events/)
- [LlamaIndex Steps](https://docs.llamaindex.ai/en/stable/examples/workflows/steps/)

### Code Examples
- `conversational_agent.py`: Complete workflow implementation
- `cli_app.py`: CLI interface example
- `test_llamaindex_agent.py`: Testing patterns

---

This integration transforms the MAG7 Financial Intelligence Q&A System into a sophisticated, production-ready AI platform capable of handling complex financial queries with multi-step reasoning and precise source attribution. 
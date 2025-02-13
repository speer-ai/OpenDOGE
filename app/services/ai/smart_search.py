from typing import Dict, Any, Optional
import json
import httpx
from app.core.config import settings
from app.core.logger import logger

# Initialize HTTP client for XAI API
async def get_xai_client():
    return httpx.AsyncClient(
        base_url="https://api.xai.com/v1",
        headers={"Authorization": f"Bearer {settings.XAI_API_KEY}"}
    )

# Define comprehensive search parameters schema
search_parameters = {
    "type": "object",
    "properties": {
        "keyword": {
            "type": "string",
            "description": "Main search keyword or phrase"
        },
        "agency": {
            "type": "string",
            "enum": ["", "DOD", "HHS", "DOE", "NASA", "DHS", "VA", "DOT", "DOI"],
            "description": "Agency code to filter by"
        },
        "min_amount": {
            "type": "string",
            "enum": ["all", "1m+", "10m+", "100m+", "1b+"],
            "description": "Minimum contract amount filter"
        },
        "max_amount": {
            "type": "string",
            "enum": ["", "10m", "100m", "1b", "10b"],
            "description": "Maximum contract amount filter"
        },
        "days": {
            "type": "integer",
            "minimum": 1,
            "maximum": 365,
            "description": "Number of days to look back"
        },
        "category": {
            "type": "string",
            "enum": ["", "construction", "research", "services", "equipment", "technology", "healthcare", "defense", "infrastructure"],
            "description": "Contract category"
        },
        "state": {
            "type": "string",
            "description": "State code (e.g., CA, NY, TX)"
        },
        "sort_by": {
            "type": "string",
            "enum": ["date", "amount", "relevance"],
            "description": "How to sort the results"
        },
        "sort_order": {
            "type": "string",
            "enum": ["asc", "desc"],
            "description": "Sort order direction"
        }
    },
    "required": ["keyword"]
}

async def process_search_query(query: str) -> Dict[str, Any]:
    """
    Process a natural language search query and return structured search parameters
    """
    try:
        system_prompt = """You are an expert at analyzing government contracts and spending data. 
        Convert natural language queries into structured search parameters. Consider:
        - Monetary amounts (convert text like 'over 10 million' to '10m+')
        - Time periods (convert relative dates to number of days)
        - Agency names (map to correct agency codes)
        - Categories (map to predefined categories)
        - Geographic locations (convert to state codes)
        - Sorting preferences (interpret user's desired ordering)
        
        Always maintain high precision and recall in the search results."""

        async with await get_xai_client() as client:
            response = await client.post("/chat/completions", json={
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "functions": [{
                    "name": "search_contracts",
                    "description": "Search for federal contracts with specific parameters",
                    "parameters": search_parameters
                }],
                "function_call": {"name": "search_contracts"}
            })
            
            response.raise_for_status()
            data = response.json()
            
            # Extract function call arguments
            function_call = data["choices"][0]["message"].get("function_call")
            if function_call and function_call.get("arguments"):
                parameters = json.loads(function_call["arguments"])
                logger.info(f"Processed search query: {query} -> {parameters}")
                return parameters
            
            logger.warning(f"No function call in response for query: {query}")
            return {"keyword": query}  # Fallback to simple keyword search

    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}")
        return {"keyword": query}  # Fallback to simple keyword search

async def get_search_suggestions(query: str) -> Dict[str, Any]:
    """
    Get intelligent search suggestions and explanations for the current query
    """
    try:
        system_prompt = """You are an expert at helping users search through government contracts.
        Provide 3-4 specific suggestions to help refine or improve the search. Consider:
        - More specific agency filters
        - Relevant contract categories
        - Amount ranges that might be relevant
        - Time period adjustments
        - Related search terms
        
        Make suggestions concrete and actionable."""

        async with await get_xai_client() as client:
            response = await client.post("/chat/completions", json={
                "model": "gpt-4",
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": f"Current search: {query}\nProvide specific suggestions to improve this search."
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 200
            })
            
            response.raise_for_status()
            data = response.json()
            
            suggestions = data["choices"][0]["message"]["content"].split("\n")
            
            # Process and structure suggestions
            processed_suggestions = []
            for suggestion in suggestions:
                if suggestion.strip():
                    # Extract any structured data if present
                    try:
                        if ":" in suggestion:
                            category, text = suggestion.split(":", 1)
                            processed_suggestions.append({
                                "category": category.strip(),
                                "text": text.strip(),
                                "query": text.strip()  # The actual query to use
                            })
                        else:
                            processed_suggestions.append({
                                "category": "General",
                                "text": suggestion.strip(),
                                "query": suggestion.strip()
                            })
                    except Exception:
                        processed_suggestions.append({
                            "category": "General",
                            "text": suggestion.strip(),
                            "query": suggestion.strip()
                        })

            return {
                "suggestions": processed_suggestions,
                "original_query": query
            }

    except Exception as e:
        logger.error(f"Error getting search suggestions: {str(e)}")
        return {
            "suggestions": [],
            "original_query": query
        } 
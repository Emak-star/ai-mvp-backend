"""
Service functions for AI operations.
Handles OpenAI API calls for prompt execution.
"""

import os
import asyncio
from typing import Optional
import openai
from openai import AsyncOpenAI

# Initialize OpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def execute_prompt(prompt_template: str, user_input: str) -> str:
    """
    Execute a prompt using OpenAI's ChatGPT API.
    
    Args:
        prompt_template (str): The template for the AI prompt
        user_input (str): User input to be combined with the template
        
    Returns:
        str: The AI's response
        
    Raises:
        ValueError: If required environment variables are missing
        openai.APIError: If the OpenAI API call fails
    """
    # Validate API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Combine prompt template with user input
    combined_prompt = f"{prompt_template}\n\nUser Input: {user_input}"
    
    try:
        # Make async call to OpenAI API
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful AI assistant. Follow the instructions in the prompt carefully."
                },
                {
                    "role": "user",
                    "content": combined_prompt
                }
            ],
            max_tokens=1000,
            temperature=0.7,
            timeout=30.0
        )
        
        # Extract and return the AI's response
        return response.choices[0].message.content.strip()
        
    except openai.APIError as e:
        raise openai.APIError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error during prompt execution: {str(e)}")


async def execute_prompt_with_custom_params(
    prompt_template: str, 
    user_input: str,
    model: str = "gpt-3.5-turbo",
    max_tokens: int = 1000,
    temperature: float = 0.7,
    system_message: Optional[str] = None
) -> str:
    """
    Execute a prompt with custom parameters.
    
    Args:
        prompt_template (str): The template for the AI prompt
        user_input (str): User input to be combined with the template
        model (str): OpenAI model to use (default: gpt-3.5-turbo)
        max_tokens (int): Maximum tokens in response (default: 1000)
        temperature (float): Response randomness (0.0-2.0, default: 0.7)
        system_message (Optional[str]): Custom system message
        
    Returns:
        str: The AI's response
    """
    # Validate API key
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    # Combine prompt template with user input
    combined_prompt = f"{prompt_template}\n\nUser Input: {user_input}"
    
    # Use custom system message or default
    system_content = system_message or "You are a helpful AI assistant. Follow the instructions in the prompt carefully."
    
    try:
        # Make async call to OpenAI API with custom parameters
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": system_content
                },
                {
                    "role": "user",
                    "content": combined_prompt
                }
            ],
            max_tokens=max_tokens,
            temperature=temperature,
            timeout=30.0
        )
        
        # Extract and return the AI's response
        return response.choices[0].message.content.strip()
        
    except openai.APIError as e:
        raise openai.APIError(f"OpenAI API error: {str(e)}")
    except Exception as e:
        raise Exception(f"Unexpected error during prompt execution: {str(e)}")


async def test_openai_connection() -> bool:
    """
    Test the OpenAI API connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        if not os.getenv("OPENAI_API_KEY"):
            return False
            
        # Make a simple test call
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10,
            timeout=10.0
        )
        
        return response.choices[0].message.content is not None
        
    except Exception:
        return False

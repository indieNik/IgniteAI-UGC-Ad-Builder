import os
import json
from typing import Dict, Any, Union, List
from litellm import completion

def get_llm_provider():
    return os.getenv("LLM_PROVIDER", "gemini").lower()

def get_model_name(provider: str, use_case: str = "text") -> str:
    """
    Maps abstract provider names to specific LiteLLM model identifiers.
    
    Args:
        provider: Provider name (gemini, openai, anthropic)
        use_case: "text" for text generation, "image" for multimodal/image tasks
    """
    if provider == "gemini":
        # gemini/ prefixes calls to Google VertexAI or AI Studio via LiteLLM
        if use_case == "image":
            return "gemini/gemini-2.5-flash-image"
        else:
            # For text/JSON generation (Visual DNA, Script, Voice Casting)
            return "gemini/gemini-2.5-flash"
    elif provider == "openai":
        return "gpt-4o"
    elif provider == "anthropic":
        return "claude-3-opus-20240229"
    # Fallback to whatever string is passed if it looks like a model name
    return provider

def generate_content_json(system_prompt: str, user_prompt: Union[str, List[Dict[str, Any]]], use_case: str = "text") -> Dict[str, Any]:
    """
    Generates JSON content using the configured LLM provider via LiteLLM.
    Unified interface for OpenAI, Gemini, Anthropic, etc.
    Supports Multimodal inputs (pass user_prompt as list of content blocks).
    
    Args:
        system_prompt: System prompt
        user_prompt: User prompt (string or multimodal content list)
        use_case: "text" or "image" - determines which model to use
    """
    provider = get_llm_provider()
    model = get_model_name(provider, use_case)
    
    print(f"--- LLM Factory: Using Model '{model}' via LiteLLM ---")

    kwargs = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.8
    }

    # Gemini Image models do not support JSON mode
    if "gemini" in model.lower() and "image" in model.lower():
        pass
    else:
        kwargs["response_format"] = {"type": "json_object"}

    try:
        response = completion(**kwargs)
        
        content = response.choices[0].message.content
        
        # Parse JSON
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            print(f"Warning: Response was not valid JSON. Content: {content[:100]}...")
            data = {"content": content}

        # Inject Metadata using LiteLLM's standardized usage object
        if isinstance(data, dict):
            data["_meta"] = {
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                },
                "model": model,
                "provider": provider
            }
            
        return data

    except Exception as e:
        print(f"LLM Generation Failed ({model}): {e}")
        raise e


def generate_content_json_with_fallback(system_prompt: str, user_prompt: Union[str, List[Dict[str, Any]]], use_case: str = "text") -> Dict[str, Any]:
    """
    Generates JSON content with multi-model fallback to handle model deprecation/failures.
    Tries: Gemini 2.5 Flash → GPT-4o-mini → GPT-3.5-turbo
    """
    # Define fallback chain
    model_chain = [
        ("gemini", "primary"),
        ("gpt-4o-mini", "backup"),
        ("gpt-3.5-turbo", "fallback")
    ]
    
    last_error = None
    
    for model_or_provider, tier in model_chain:
        try:
            # Check if it's a full model name or provider
            if "/" in model_or_provider or model_or_provider.startswith("gpt"):
                model = model_or_provider
            else:
                model = get_model_name(model_or_provider, use_case)
            
            print(f"--- LLM Factory: Attempting Model '{model}' (tier: {tier}) ---")
            
            response = completion(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON
            try:
                data = json.loads(content)
            except json.JSONDecodeError:
                print(f"Warning: Response was not valid JSON. Content: {content[:100]}...")
                data = {"content": content}

            # Inject Metadata
            if isinstance(data, dict):
                data["_meta"] = {
                    "usage": {
                        "input_tokens": response.usage.prompt_tokens,
                        "output_tokens": response.usage.completion_tokens
                    },
                    "model": model,
                    "tier": tier
                }
            
            print(f"✅ Success with {model} ({tier})")
            return data
            
        except Exception as e:
            print(f"⚠️ Model {model_or_provider} ({tier}) failed: {e}")
            last_error = e
            continue
    
    # All models failed
    print(f"❌ All models in fallback chain failed. Last error: {last_error}")
    raise Exception(f"All LLM models failed. Last error: {last_error}")

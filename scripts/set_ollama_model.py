#!/usr/bin/env python3
"""
Script to list available Ollama models and set the default model for the application.
"""
import asyncio
import sys
import os
import logging
from typing import List

# Add the parent directory to sys.path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.llm_service import LLMService, get_llm_service
from app.config import settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


async def get_available_models() -> List[str]:
    """Get a list of available Ollama models."""
    logging.info(f"Fetching available models from Ollama at {settings.OLLAMA_BASE_URL}")
    llm_service = get_llm_service()
    return await llm_service.list_available_models()


def print_model_list(models: List[str], current_model: str) -> None:
    """Print the list of available models with the current model marked."""
    print("\nAvailable Ollama Models:")
    print("=" * 50)
    for i, model in enumerate(models, 1):
        current_marker = " (current)" if model == current_model else ""
        print(f"{i}. {model}{current_marker}")
    print("=" * 50)


async def main():
    try:
        # Get available models
        models = await get_available_models()
        
        if not models:
            logging.error("No Ollama models found. Is Ollama running?")
            print("\nError: No models found. Please ensure Ollama is running at", settings.OLLAMA_BASE_URL)
            print("To install models, run: ollama pull <model-name>")
            print("Example models: llama3, mistral, phi3, mixtral:8x7b, llama3:70b-q4")
            return 1
        
        # Print model list with current model marked
        print_model_list(models, settings.OLLAMA_MODEL)
        
        # Let user select a model
        selection = input("\nEnter number to select a model (or press Enter to keep current): ")
        
        if not selection:
            print(f"Keeping current model: {settings.OLLAMA_MODEL}")
            return 0
        
        try:
            selection_idx = int(selection) - 1
            if selection_idx < 0 or selection_idx >= len(models):
                print(f"Invalid selection. Please enter a number between 1 and {len(models)}")
                return 1
                
            selected_model = models[selection_idx]
            
            # Set the model as default
            success = LLMService.set_default_model(selected_model)
            
            if success:
                print(f"\nDefault model successfully set to: {selected_model}")
                print("Restart the application for changes to take effect.")
            else:
                print("\nFailed to set default model. Please check the logs.")
                return 1
                
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            return 1
            
        return 0
        
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

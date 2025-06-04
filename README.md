# News From Future

![CI](https://github.com/user/news_from_future/actions/workflows/ci.yml/badge.svg)

API that fetches current news and generates future news predictions using a local LLM.

## Features

- Fetches current news from various sources
- Generates hypothetical future news articles based on current trends
- Supports different time frames (day, week, month)
- Supports different news styles (neutral, optimistic, pessimistic)
- Built with FastAPI for high performance and easy API documentation
- Uses local LLM through Ollama for generation

## Development

### Prerequisites

- Python 3.10 or higher
- Poetry (Python package manager)

### Setup
A FastAPI application that fetches current news from public news APIs, uses it as context for a local LLM running on Ollama, and generates predictive "future news" based on current trends.

## Features

- Periodically fetches current news from NewsAPI
- Stores news data in a local cache
- Integrates with Ollama to use local LLM models
- Generates future news predictions based on current news context
- REST API for retrieving news and generating predictions
- Streaming generation support
- Configurable news sources, categories, and update frequency

## Requirements

- Python 3.10 - 3.13
- Poetry for dependency management
- An API key from [NewsData.io](https://newsdata.io/)
- [Ollama](https://ollama.ai/) running locally with models installed

## Recommended LLM Models for NVIDIA 3090 (24GB VRAM)

The application is configured to work well with the following models on an NVIDIA 3090 GPU:

- `llama3` (default) - Good balance of quality and performance
- `mistral` - Great for general text generation
- `phi3` - Efficient model that works well with limited context
- `mixtral:8x7b` - If you want to use a mixture-of-experts model
- `llama3:70b-q4` - Quantized version of larger model for better quality

You can configure the model in the `.env` file or choose at runtime through the API.
# News From Future

FastAPI application to generate future news based on current news using local LLM.

## Dependency Management

This project includes built-in CLI commands for managing dependencies:

### Using the CLI
## Setup
# Grand Lodge of Future Sight

A mystical web application that reveals news from the future, styled with Masonic themes and symbolism.

![Grand Lodge of Future Sight](static/images/screenshot.png)

## Features

- Gaze into the future with customizable time ranges
- Beautifully styled interface with Masonic imagery and symbolism
- Responsive design that works on desktop and mobile devices
- Elegant animations and transitions
- Integration with Ollama for local LLM inference

## Installation on Arch Linux

### Prerequisites

- Arch Linux (or Arch-based distribution)
- Python 3.13+
- Poetry package manager
- Git
- Ollama (for local LLM inference)

### Step 1: Install Dependencies
1. Clone the repository:

```bash
git clone https://github.com/yourusername/news-from-future.git
cd news-from-future

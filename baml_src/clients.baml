client<llm> Ollama {
  provider "openai-generic"
  options {
    base_url env.OLLAMA_BASE_URL
    model env.OLLAMA_MODEL
    api_key env.OLLAMA_API_KEY
  }
}

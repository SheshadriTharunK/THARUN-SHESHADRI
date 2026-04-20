from typing import cast
from pydantic_ai.models import Model
from pydantic_ai.settings import ModelSettings
import os 
from dotenv import load_dotenv

load_dotenv(override=True)

def build_model() -> Model:

    model_name = "groq:llama-3.3-70b-versatile"
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("Warning: GROQ_API_KEY environment variable is not set. GROQ model will not work without it.")
        raise ValueError("GROQ_API_KEY environment variable is not set")
    base_url = ""
    temperature = 0.0
    max_tokens = 1024
    model_settings = ModelSettings(
        temperature=temperature,
        max_tokens=max_tokens,
    )
    if model_name.startswith("openai:"):
        from pydantic_ai.models.openai import OpenAIModel, OpenAIModelName
        from pydantic_ai.providers.openai import OpenAIProvider

        return OpenAIModel(
            cast(OpenAIModelName, model_name[7:]),
            provider=OpenAIProvider(api_key=api_key),
            model_settings=model_settings,
        )

    elif model_name.startswith("anthropic:"):
        from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelName

        return AnthropicModel(
            cast(AnthropicModelName, model_name[10:]),
            api_key=api_key,
            model_settings=model_settings,
        )

    elif model_name.startswith("google-gla:"):
        from pydantic_ai.models.gemini import GeminiModel, GeminiModelName
        from pydantic_ai.providers.google_gla import GoogleGLAProvider

        return GeminiModel(
            cast(GeminiModelName, model_name[11:]),
            provider=GoogleGLAProvider(api_key=api_key),
            model_settings=model_settings,
        )

    elif model_name.startswith("groq:"):
        from pydantic_ai.models.groq import GroqModel, GroqModelName
        from pydantic_ai.providers.groq import GroqProvider

        return GroqModel(
            cast(GroqModelName, model_name[5:]), provider=GroqProvider(api_key=api_key),
            settings = model_settings,
        )

    elif model_name.startswith("mistral:"):
        from pydantic_ai.models.mistral import MistralModel, MistralModelName
        from pydantic_ai.providers.mistral import MistralProvider

        return MistralModel(
            cast(MistralModelName, model_name[8:]),
            provider=MistralProvider(api_key=api_key),
            model_settings=model_settings,
        )

    elif model_name.startswith("ollama:"):
        from pydantic_ai.models.openai import OpenAIModel
        from pydantic_ai.providers.openai import OpenAIProvider

        return OpenAIModel(
            model_name[7:],
            provider=OpenAIProvider(base_url=base_url),
            model_settings=model_settings,
        )

    else:
        raise ValueError(f"Unsupported model name: {model_name}")


if __name__ == "__main__":
    model = build_model()
    print(model)

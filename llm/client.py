"""Module providing a resilient client interface for the Ollama LLM ecosystem."""

import logging
from langchain_ollama import ChatOllama

# Clean, standard module-level logger
logger = logging.getLogger(__name__)


class LLMClient:
    """A resilient client for interacting with localized Ollama language models."""

    def __init__(self, model: str = "llama3.2:3b") -> None:
        """Initializes the LLMClient with safe constructor isolation.

        Args:
            model: The identifier name of the Ollama model executable to bind.
                Defaults to "llama3.2:3b".
        """
        self.model: str = model
        # Modern Python 3.10+ Union syntax used instead of typing.Optional
        self._client: ChatOllama | None = None

        try:
            # Safe initialization: prevents constructor crash if Ollama is missing/uninstalled
            self._client = ChatOllama(model=self.model)
        except Exception as e:
            logger.exception("Failed to initialize ChatOllama driver for model %s: %s", self.model, str(e))

    def generate(self, prompt: str) -> str:
        """Sends a string prompt to Ollama and returns the whitespace-stripped text.

        Args:
            prompt: The raw alphanumeric text string instruction.

        Returns:
            The normalized response string, or an empty string if generation fails.
        """
        if not prompt or not prompt.strip():
            logger.warning("Generation bypassed: Empty prompt received.")
            return ""

        if self._client is None:
            logger.error("Generation failed: ChatOllama driver was not initialized.")
            return ""

        try:
            # Removed unnecessary 'Any' explicit type hint
            response = self._client.invoke(prompt)
            
            if response is None:
                logger.error("Failed to generate response: Received None from Ollama.")
                return ""

            # Direct and clean extraction
            return str(response.content).strip()

        except (RuntimeError, ConnectionError) as net_err:
            logger.error("Network or runtime error during Ollama generation: %s", str(net_err))
            return ""
            
        except Exception as ex:
            logger.exception("Unexpected error during LLM generation: %s", str(ex))
            return ""
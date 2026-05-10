import os
from langchain_core.language_models import BaseChatModel


def get_architect_llm() -> BaseChatModel:
    """Returns the LLM for the Architect agent (Claude Opus 4.7 via OpenRouter)."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("ARCHITECT_MODEL", "anthropic/claude-opus-4-7")

    if not api_key or api_key == "mock":
        return _get_fake_llm("architect")

    from langchain_openrouter import ChatOpenRouter
    return ChatOpenRouter(model=model, openrouter_api_key=api_key)


def get_writer_llm() -> BaseChatModel:
    """Returns the LLM for Writer agents (Claude Sonnet 4.6 via OpenRouter)."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")
    model = os.getenv("WRITER_MODEL", "anthropic/claude-sonnet-4-6")

    if not api_key or api_key == "mock":
        return _get_fake_llm("writer")

    from langchain_openrouter import ChatOpenRouter
    return ChatOpenRouter(model=model, openrouter_api_key=api_key)


def _get_fake_llm(role: str) -> BaseChatModel:
    """FakeLLM for testing — never calls real APIs."""
    from langchain_community.llms.fake import FakeListLLM
    from langchain_core.language_models import BaseChatModel
    from langchain_core.messages import AIMessage
    from langchain_core.outputs import ChatResult, ChatGeneration

    import json

    if role == "architect":
        fake_outline = json.dumps({
            "title": "Tu Libro de Biohacking Personalizado: Optimiza tu Energía y Salud",
            "chapters": [
                {
                    "title": "Introducción",
                    "level": 0,
                    "sections": [
                        {
                            "title": "Por qué el Biohacking",
                            "subsections": [
                                {"title": "Qué es el biohacking moderno", "focus": "Ciencia detrás del hábito"},
                                {"title": "Cómo usar este libro", "focus": "Acciones concretas"},
                            ],
                        }
                    ],
                },
                {
                    "title": "Nivel 1: Fundamentos",
                    "level": 1,
                    "sections": [
                        {
                            "title": "Nutrición Base",
                            "subsections": [
                                {"title": "Hidratación óptima", "focus": "Acciones concretas"},
                                {"title": "Por qué el agua es el primer paso", "focus": "Ciencia detrás del hábito"},
                                {"title": "Protocolo de hidratación diaria", "focus": "Protocolo de implementación"},
                            ],
                        },
                        {
                            "title": "Sueño Reparador",
                            "subsections": [
                                {"title": "Las 8 horas de sueño", "focus": "Acciones concretas"},
                                {"title": "Arquitectura del sueño y recuperación", "focus": "Ciencia detrás del hábito"},
                            ],
                        },
                    ],
                },
                {
                    "title": "Conclusión",
                    "level": 0,
                    "sections": [
                        {
                            "title": "Tu Plan de Acción",
                            "subsections": [
                                {"title": "Primeros 30 días", "focus": "Protocolo de implementación"},
                            ],
                        }
                    ],
                },
            ],
        })
        responses = [fake_outline]
    else:
        responses = [
            "Este es el contenido generado para esta subsección. Incluye información detallada y personalizada "
            "basada en tu perfil. El contenido está adaptado a tus objetivos específicos y considera tu estilo "
            "de vida actual para maximizar la adherencia y los resultados."
        ]

    class FakeChatLLM(BaseChatModel):
        responses: list[str]
        call_count: int = 0

        def _generate(self, messages, stop=None, run_manager=None, **kwargs):
            response = self.responses[min(self.call_count, len(self.responses) - 1)]
            self.call_count += 1
            return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response))])

        @property
        def _llm_type(self) -> str:
            return "fake-chat"

    return FakeChatLLM(responses=responses)

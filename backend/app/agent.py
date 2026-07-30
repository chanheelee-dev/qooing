from __future__ import annotations

import json
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import cast

from pydantic_ai import (
    Agent,
    ModelMessage,
    ModelResponse,
    RunContext,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
)
from pydantic_ai.models import Model
from pydantic_ai.models.function import AgentInfo, FunctionModel

from .schemas import BabyInfo
from .wiki_store import WikiStore


@dataclass
class AgentDependencies:
    wiki: WikiStore


def offline_model(messages: list[ModelMessage], _info: AgentInfo) -> ModelResponse:
    returns = [
        part for message in messages for part in message.parts if isinstance(part, ToolReturnPart)
    ]
    if not returns:
        return ModelResponse(parts=[ToolCallPart("list_wiki", {})])
    if len(returns) == 1:
        content = returns[0].content
        if not isinstance(content, list) or not content:
            return ModelResponse(
                parts=[
                    TextPart(
                        "Offline scaffold response: no wiki documents are available. "
                        "This is a deterministic development response, not medical advice."
                    )
                ]
            )
        first = content[0]
        slug = (
            str(cast(dict[str, object], first).get("slug", ""))
            if isinstance(first, dict)
            else str(first)
        )
        return ModelResponse(parts=[ToolCallPart("read_wiki", {"slug": slug})])

    document = returns[-1].content
    if isinstance(document, dict):
        title = document.get("title", "wiki")
        description = document.get("description", "")
    else:
        title, description = "wiki", str(document)
    return ModelResponse(
        parts=[
            TextPart(
                f"Offline scaffold response based on “{title}”: {description}. "
                "This is a deterministic development response, not medical advice."
            )
        ]
    )


def create_agent(model_name: str | None) -> Agent[AgentDependencies, str]:
    model: str | Model = model_name or FunctionModel(offline_model)
    agent = Agent(
        model,
        deps_type=AgentDependencies,
        instructions=(
            "Answer baby-care questions using the wiki tools. State uncertainty and never present "
            "the response as a medical diagnosis."
        ),
    )

    @agent.tool
    def list_wiki(ctx: RunContext[AgentDependencies]) -> list[dict[str, str]]:
        """List available wiki documents."""
        return [item.model_dump() for item in ctx.deps.wiki.list()]

    @agent.tool
    def read_wiki(ctx: RunContext[AgentDependencies], slug: str) -> dict[str, object]:
        """Read one wiki document by slug."""
        return ctx.deps.wiki.read(slug).model_dump()

    return agent


class ChatService:
    def __init__(self, wiki: WikiStore, model_name: str | None) -> None:
        self.dependencies = AgentDependencies(wiki)
        self.agent = create_agent(model_name)
        self.configured = model_name is not None

    async def stream(self, prompt: str, baby_info: BabyInfo) -> AsyncIterator[str]:
        profile = json.dumps(baby_info.model_dump(mode="json"), ensure_ascii=False)
        enriched_prompt = f"Baby profile: {profile}\n\nQuestion: {prompt}"
        if not self.configured:
            result = await self.agent.run(enriched_prompt, deps=self.dependencies)
            output = result.output
            for start in range(0, len(output), 32):
                yield output[start : start + 32]
            return

        async with self.agent.run_stream(enriched_prompt, deps=self.dependencies) as result:
            async for delta in result.stream_text(delta=True):
                yield delta

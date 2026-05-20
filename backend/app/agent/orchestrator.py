import json
from typing import AsyncGenerator

from openai import AsyncAzureOpenAI

from app.config import Settings
from app.agent.system_prompt import SYSTEM_PROMPT
from app.iac_engine.generator import IaCGenerator


class AgentOrchestrator:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncAzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
        self.generator = IaCGenerator()
        self._sessions: dict[str, list] = {}

    def _get_session_messages(self, session_id: str | None) -> list[dict]:
        if not session_id:
            return [{"role": "system", "content": SYSTEM_PROMPT}]
        if session_id not in self._sessions:
            self._sessions[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
        return self._sessions[session_id]

    async def process_message(
        self, message: str, session_id: str | None, iac_format: str
    ) -> dict:
        messages = self._get_session_messages(session_id)
        messages.append({"role": "user", "content": message})

        tools = self._get_tools()

        response = await self.client.chat.completions.create(
            model=self.settings.azure_openai_deployment,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
        )

        assistant_message = response.choices[0].message

        # Handle tool calls for IaC generation
        if assistant_message.tool_calls:
            messages.append(assistant_message)
            tool_results = await self._execute_tool_calls(
                assistant_message.tool_calls, iac_format
            )
            for result in tool_results:
                messages.append(result)

            # Get final response after tool execution
            final_response = await self.client.chat.completions.create(
                model=self.settings.azure_openai_deployment,
                messages=messages,
            )
            final_message = final_response.choices[0].message
            messages.append({"role": "assistant", "content": final_message.content})

            # Extract IaC from tool results
            iac_code = None
            pattern_used = None
            files = None
            for result in tool_results:
                if result["role"] == "tool":
                    try:
                        data = json.loads(result["content"])
                        if "iac_code" in data:
                            iac_code = data["iac_code"]
                            pattern_used = data.get("pattern")
                            files = data.get("files")
                    except (json.JSONDecodeError, KeyError):
                        pass

            return {
                "reply": final_message.content,
                "iac_code": iac_code,
                "pattern_used": pattern_used,
                "files": files,
            }

        messages.append({"role": "assistant", "content": assistant_message.content})
        return {"reply": assistant_message.content, "iac_code": None, "pattern_used": None, "files": None}

    async def process_message_stream(
        self, message: str, session_id: str | None, iac_format: str
    ) -> AsyncGenerator[str, None]:
        messages = self._get_session_messages(session_id)
        messages.append({"role": "user", "content": message})

        tools = self._get_tools()

        stream = await self.client.chat.completions.create(
            model=self.settings.azure_openai_deployment,
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0.1,
            stream=True,
        )

        collected_content = ""
        tool_calls_data = []

        async for chunk in stream:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta

            if delta.content:
                collected_content += delta.content
                yield json.dumps({"type": "text", "content": delta.content})

            if delta.tool_calls:
                for tc in delta.tool_calls:
                    if tc.index >= len(tool_calls_data):
                        tool_calls_data.append({"id": tc.id, "name": "", "arguments": ""})
                    if tc.function.name:
                        tool_calls_data[tc.index]["name"] = tc.function.name
                    if tc.function.arguments:
                        tool_calls_data[tc.index]["arguments"] += tc.function.arguments

        # If tool calls were made, execute them
        if tool_calls_data:
            for tc_data in tool_calls_data:
                args = json.loads(tc_data["arguments"])
                result = self._execute_single_tool(tc_data["name"], args, iac_format)
                yield json.dumps({"type": "iac", "content": result})

    async def _execute_tool_calls(self, tool_calls, iac_format: str) -> list[dict]:
        results = []
        for tool_call in tool_calls:
            args = json.loads(tool_call.function.arguments)
            result = self._execute_single_tool(
                tool_call.function.name, args, iac_format
            )
            results.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result),
            })
        return results

    def _execute_single_tool(self, name: str, args: dict, iac_format: str) -> dict:
        if name == "generate_iac":
            return self.generator.generate(
                pattern=args.get("pattern", "foundry-agent-basic"),
                parameters=args.get("parameters", {}),
                iac_format=iac_format,
            )
        elif name == "list_available_patterns":
            return {"patterns": self.generator.list_patterns()}
        elif name == "customize_pattern":
            return self.generator.customize(
                pattern=args["pattern"],
                customizations=args.get("customizations", {}),
                iac_format=iac_format,
            )
        return {"error": f"Unknown tool: {name}"}

    def _get_tools(self) -> list[dict]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "generate_iac",
                    "description": "Generate Infrastructure as Code for an Azure AI Agent platform deployment. Call this when the user has provided enough requirements to generate IaC.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {
                                "type": "string",
                                "enum": [
                                    "foundry-agent-basic",
                                    "foundry-agent-vnet",
                                    "multi-agent-orchestrator",
                                    "rag-agent",
                                    "agent-with-mcp",
                                ],
                                "description": "The architecture pattern to use",
                            },
                            "parameters": {
                                "type": "object",
                                "description": "Parameters for the pattern",
                                "properties": {
                                    "project_name": {"type": "string"},
                                    "region": {"type": "string"},
                                    "environment": {
                                        "type": "string",
                                        "enum": ["dev", "staging", "prod"],
                                    },
                                    "enable_vnet": {"type": "boolean"},
                                    "enable_private_endpoints": {"type": "boolean"},
                                    "enable_monitoring": {"type": "boolean"},
                                    "model_deployments": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "model": {"type": "string"},
                                                "capacity": {"type": "integer"},
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        "required": ["pattern"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "list_available_patterns",
                    "description": "List all available architecture patterns for AI Agent platforms",
                    "parameters": {"type": "object", "properties": {}},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "customize_pattern",
                    "description": "Customize an existing pattern with specific modifications",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "pattern": {"type": "string"},
                            "customizations": {
                                "type": "object",
                                "description": "Key-value customizations to apply",
                            },
                        },
                        "required": ["pattern"],
                    },
                },
            },
        ]

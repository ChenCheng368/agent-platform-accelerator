import os
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

PATTERN_REGISTRY = {
    "foundry-agent-basic": {
        "id": "foundry-agent-basic",
        "name": "AI Foundry Agent - Basic",
        "description": "Azure AI Foundry + OpenAI + Managed Identity + Key Vault + App Insights. Ideal for single-agent scenarios.",
        "components": [
            "Azure AI Foundry Hub & Project",
            "Azure OpenAI with model deployments",
            "Key Vault for secrets",
            "Application Insights + Log Analytics",
            "Managed Identity (User-Assigned)",
            "Storage Account",
        ],
        "estimated_monthly_cost": "$150-400 (depends on model usage)",
        "template_dir": "foundry_agent_basic",
    },
    "foundry-agent-vnet": {
        "id": "foundry-agent-vnet",
        "name": "AI Foundry Agent - VNet Secured",
        "description": "Production-ready with VNet integration, Private Endpoints, and NSGs for network isolation.",
        "components": [
            "All of foundry-agent-basic",
            "Virtual Network with subnets",
            "Private Endpoints for all services",
            "Network Security Groups",
            "Private DNS Zones",
        ],
        "estimated_monthly_cost": "$300-700 (depends on model usage)",
        "template_dir": "foundry_agent_vnet",
    },
    "multi-agent-orchestrator": {
        "id": "multi-agent-orchestrator",
        "name": "Multi-Agent Orchestrator",
        "description": "Container Apps + Service Bus + Cosmos DB for multi-agent systems with async communication.",
        "components": [
            "Azure Container Apps Environment",
            "Azure OpenAI",
            "Azure Service Bus (Standard)",
            "Azure Cosmos DB (Serverless)",
            "Application Insights",
            "Key Vault",
            "Container Registry",
            "Managed Identity",
        ],
        "estimated_monthly_cost": "$400-1000 (depends on scale)",
        "template_dir": "multi_agent_orchestrator",
    },
    "rag-agent": {
        "id": "rag-agent",
        "name": "RAG Agent",
        "description": "AI Search + OpenAI + Cosmos DB for retrieval-augmented generation agents.",
        "components": [
            "Azure AI Search (Standard)",
            "Azure OpenAI (with embedding model)",
            "Azure Cosmos DB (Serverless)",
            "Azure Blob Storage",
            "Application Insights",
            "Key Vault",
            "Managed Identity",
        ],
        "estimated_monthly_cost": "$500-1500 (depends on search tier & usage)",
        "template_dir": "rag_agent",
    },
    "agent-with-mcp": {
        "id": "agent-with-mcp",
        "name": "Agent with MCP Server",
        "description": "Container Apps hosting an MCP server alongside an AI agent for tool-augmented workflows.",
        "components": [
            "Azure Container Apps Environment",
            "Azure OpenAI",
            "Container Registry",
            "Application Insights",
            "Key Vault",
            "Managed Identity",
        ],
        "estimated_monthly_cost": "$200-600 (depends on scale)",
        "template_dir": "agent_with_mcp",
    },
}


class IaCGenerator:
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            keep_trailing_newline=True,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def list_patterns(self) -> list[dict]:
        return [
            {
                "id": p["id"],
                "name": p["name"],
                "description": p["description"],
                "components": p["components"],
                "estimated_monthly_cost": p["estimated_monthly_cost"],
            }
            for p in PATTERN_REGISTRY.values()
        ]

    def get_pattern_details(self, pattern_id: str) -> dict:
        if pattern_id not in PATTERN_REGISTRY:
            return {"error": f"Pattern '{pattern_id}' not found"}
        return PATTERN_REGISTRY[pattern_id]

    def generate(self, pattern: str, parameters: dict, iac_format: str) -> dict:
        if pattern not in PATTERN_REGISTRY:
            return {"error": f"Pattern '{pattern}' not found"}

        pattern_info = PATTERN_REGISTRY[pattern]
        template_dir = pattern_info["template_dir"]

        # Apply defaults
        params = {
            "project_name": parameters.get("project_name", "myagent"),
            "region": parameters.get("region", "southeastasia"),
            "environment": parameters.get("environment", "dev"),
            "enable_vnet": parameters.get("enable_vnet", False),
            "enable_private_endpoints": parameters.get("enable_private_endpoints", False),
            "enable_monitoring": parameters.get("enable_monitoring", True),
            "model_deployments": parameters.get("model_deployments", [
                {"name": "gpt-4o", "model": "gpt-4o", "capacity": 30},
            ]),
            "tags": {
                "environment": parameters.get("environment", "dev"),
                "project": parameters.get("project_name", "myagent"),
                "managed-by": "agent-platform-accelerator",
            },
        }

        if iac_format == "bicep":
            return self._generate_bicep(template_dir, params, pattern)
        else:
            return self._generate_terraform(template_dir, params, pattern)

    def customize(self, pattern: str, customizations: dict, iac_format: str) -> dict:
        if pattern not in PATTERN_REGISTRY:
            return {"error": f"Pattern '{pattern}' not found"}

        # Merge customizations into default parameters
        params = {
            "project_name": customizations.get("project_name", "myagent"),
            "region": customizations.get("region", "southeastasia"),
            "environment": customizations.get("environment", "dev"),
            "enable_monitoring": True,
            **customizations,
        }
        params["tags"] = {
            "environment": params.get("environment", "dev"),
            "project": params.get("project_name", "myagent"),
            "managed-by": "agent-platform-accelerator",
        }

        template_dir = PATTERN_REGISTRY[pattern]["template_dir"]

        if iac_format == "bicep":
            return self._generate_bicep(template_dir, params, pattern)
        else:
            return self._generate_terraform(template_dir, params, pattern)

    def _generate_bicep(self, template_dir: str, params: dict, pattern: str) -> dict:
        files = []
        bicep_dir = Path(TEMPLATES_DIR) / "bicep" / template_dir

        if not bicep_dir.exists():
            # Fallback to generating from the base template
            template = self.jinja_env.get_template(f"bicep/{template_dir}/main.bicep.j2")
            main_content = template.render(**params)
            files.append({"filename": "main.bicep", "content": main_content})

            # Try to render parameters file
            try:
                params_template = self.jinja_env.get_template(
                    f"bicep/{template_dir}/main.bicepparam.j2"
                )
                params_content = params_template.render(**params)
                files.append({"filename": "main.bicepparam", "content": params_content})
            except Exception:
                pass
        else:
            for template_file in sorted(bicep_dir.glob("*.j2")):
                template = self.jinja_env.get_template(
                    f"bicep/{template_dir}/{template_file.name}"
                )
                output_name = template_file.stem  # Remove .j2
                content = template.render(**params)
                files.append({"filename": output_name, "content": content})

        combined = "\n\n".join(
            f"// === {f['filename']} ===\n{f['content']}" for f in files
        )

        return {
            "iac_code": combined,
            "pattern": pattern,
            "format": "bicep",
            "files": files,
        }

    def _generate_terraform(self, template_dir: str, params: dict, pattern: str) -> dict:
        files = []
        tf_dir = Path(TEMPLATES_DIR) / "terraform" / template_dir

        if not tf_dir.exists():
            template = self.jinja_env.get_template(f"terraform/{template_dir}/main.tf.j2")
            main_content = template.render(**params)
            files.append({"filename": "main.tf", "content": main_content})

            try:
                vars_template = self.jinja_env.get_template(
                    f"terraform/{template_dir}/variables.tf.j2"
                )
                vars_content = vars_template.render(**params)
                files.append({"filename": "variables.tf", "content": vars_content})
            except Exception:
                pass
        else:
            for template_file in sorted(tf_dir.glob("*.j2")):
                template = self.jinja_env.get_template(
                    f"terraform/{template_dir}/{template_file.name}"
                )
                output_name = template_file.stem
                content = template.render(**params)
                files.append({"filename": output_name, "content": content})

        combined = "\n\n".join(
            f"# === {f['filename']} ===\n{f['content']}" for f in files
        )

        return {
            "iac_code": combined,
            "pattern": pattern,
            "format": "terraform",
            "files": files,
        }

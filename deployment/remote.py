import os
import sys

import vertexai
from dotenv import load_dotenv
from vertexai import agent_engines
from vertexai.preview import reasoning_engines

remote_agent = agent_engines.create(
    config={
        "developer_connect_source": {                   # Required.
            "git_repository_link": "projects/arbor-2026/locations/us-central1/connections/arbor-chat-backend/gitRepositoryLinks/samuelarbolai-arbor-chat-backend",
            "revision": "main",
            "dir": "../chat-agent",
        },
        "entrypoint_module": "main",                   # Required.
        "entrypoint_object": "root_agent",              # Required.
        "requirements_file": "requirements.txt",        # Optional.
        # Other optional configs:
        # "env_vars": {...},
        # "service_account": "...",
    },
)
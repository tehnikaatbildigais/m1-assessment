"""Iestatījumi. Noslēpumus (secrets) nolasa no vides, nekad no koda."""

import os

OMD_BASE_URL = os.getenv("OMD_BASE_URL", "http://localhost:8001")
OMD_API_TOKEN = os.getenv("OMD_API_TOKEN", "")

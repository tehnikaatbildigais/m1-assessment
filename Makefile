# Ezermalas iesniegumu sistēma · komandas. Saraksts: make help
SHELL := /bin/bash
# Marķieris (token) tikai OMD imitācijai. Īstus marķierus šeit neraksta.
OMD_API_TOKEN ?= macibu-tokens-tikai-imitacijai
export OMD_API_TOKEN

.PHONY: help run mock test fmt check

help: ## Parāda komandas
	@awk -F ':.*## ' '/^[a-zA-Z_%-]+:.*## / {printf "  make %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

run: ## Palaiž lietotni (ports 8000: /ui un /docs)
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

mock: ## Palaiž OMD reģistra imitāciju (ports 8001)
	python -m uvicorn mock_omd.main:app --host 0.0.0.0 --port 8001

test: ## Palaiž testus
	python -m pytest -q

fmt: ## Formatē kodu un izlabo stila piezīmes
	ruff format .
	ruff check --fix .

check: ## Skeneri: ruff, bandit, pip-audit (lēmumu pieņemat jūs)
	-ruff check .
	-bandit -q -r app mock_omd
	-pip-audit -r requirements.txt

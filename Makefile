.DEFAULT_GOAL := help

.PHONY: help run session votes

help: ## Show available commands
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

run: ## Run the bot
	uv run --env-file .env python run.py

session: ## Log in to Telegram and print a TG_SESSION string
	uv run --env-file .env python make_session.py

votes: ## Analyze who voted in the polls over the last MONTHS months
	uv run --env-file .env python analyze_votes.py

# Changelog

All notable changes to this project will be documented in this file.

## [1.0.0] - 2026-06-28

### Added

- LangGraph cyclic agent (`agent → tools → summarize_conversation → END`) with Deepseek inference via OpenAI-compatible API
- Three-layer security pipeline: regex pre-filter, Groq PromptGuard2 (`llama-prompt-guard-2-22m`) injection judge, Presidio PII redaction with Faker-based substitution
- PII restoration via Groq `llama-3.1-8b-instant`; Redis session map (`HSET`, 24 h TTL) accumulates pairs across turns
- Redis sliding-window rate limiter (10 req / 60 s per session, sorted set)
- Postgres-backed conversation memory via `AsyncPostgresSaver`; `InMemorySaver` fallback for dev and CI
- Action Ledger summarisation: structured `## Facts & Constraints Learned` / `## Actions Taken` ledger written when message count > 3 or estimated tokens > 1000; orphan-ToolMessage guard and leading-context preservation for `trim_messages`
- Tools: `get_quote` (yfinance, 3× retry with backoff), `budget_calc`, `categorise_expense`
- LangSmith tracing with thread-grouped sessions; `aevaluate` evaluation pipeline against 63-example golden dataset (`finance-agent-golden-v3`)
- Evaluators: `eval_tool_match`, `eval_no_pii_leak`, `eval_injection_refused`, `eval_no_hallucination`, Deepseek LLM-as-judge correctness + relevance
- React 19 + Vite + Tailwind CSS frontend with session management and per-message tool badge
- GitHub Actions CI (`ci.yml`: lint, typecheck, test) and manual eval workflow (`eval.yml`: `workflow_dispatch`, per-category)

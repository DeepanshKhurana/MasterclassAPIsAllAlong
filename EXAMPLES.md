# Example LLM Queries

Five natural-language messages to send to `/chat` once all three services are
running (`scripts/run_all.sh`) and `OPENROUTER_API_KEY` is set in `.env`.
Substitute `<orch_port>` with whatever `03_python_orchestration` printed at
startup.

```bash
curl -X POST http://localhost:<orch_port>/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "YOUR QUERY HERE"}'
```

## 1. "How good is India this year?"

Mentions one team, so `chat.py` calls both `01_r_service` (official
ESPNcricinfo record) and `02_python_data_service` (`cricketstats` computed
form) and combines them into the LLM's context. The core demo.

## 2. "Who's leading the T20 leaderboard by batting average?"

Triggers the leaderboard branch of `_resolve_context`, which pulls the R side
team leaderboard and has the LLM narrate the rankings.

## 3. "What's a googly?"

No data lookup, just plain LLM knowledge explained for a newcomer. Good for
testing the model and prompt in isolation, independent of either data service.

## 4. "Compare India and Australia this season"

Mentions two teams, so both get looked up (again, from both services each),
giving the LLM enough grounded data to contrast them.

## 5. "What's the weather like today?"

Off topic. No team or term is mentioned, so no data is fetched. Tests that the
system prompt (`03_python_orchestration/prompts/chat_system.md`) correctly
redirects the LLM back to cricket instead of answering.

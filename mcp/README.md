# mcp/

TypeScript MCP server, planned for Phase 4. It will wrap the same local
core API, not a second product.

Read-only tools, in the order they should ship:

1. `list_fixtures`
2. `get_market_prices`
3. `research_match`
4. `check_rtp`
5. `get_bankroll`
6. `log_bet`

Write access for placement is out of scope for the first MCP release. An
MCP client does not need to place a bet in order to be useful, and
read-only removes a whole class of risk.

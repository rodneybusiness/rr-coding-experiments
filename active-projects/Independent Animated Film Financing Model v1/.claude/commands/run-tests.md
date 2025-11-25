---
description: Run project tests with coverage
argument-hint: [backend|frontend|all]
---

Run tests for the Film Financing Navigator:

If $1 is "backend" or "all":
- Navigate to backend directory
- Run: `cd /home/user/rr-coding-experiments/active-projects/"Independent Animated Film Financing Model v1"/backend && python -m pytest tests/ -v --tb=short`
- Report pass/fail counts and any failures

If $1 is "frontend" or "all":
- Navigate to frontend directory
- Run: `cd /home/user/rr-coding-experiments/active-projects/"Independent Animated Film Financing Model v1"/frontend && npm test -- --passWithNoTests`
- Report results

Summarize:
- Total tests passed/failed
- Coverage percentage if available
- Any critical failures that need immediate attention

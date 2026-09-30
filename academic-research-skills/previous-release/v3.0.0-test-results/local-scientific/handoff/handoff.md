# Execution handoff — prepared, NOT executed

Capability: analysis-execution

## Original request
Manufactured analytic smoke test only

## Required outputs
["results", "figure", "report"]

## Inputs and constraints
[{"path": "/mnt/data/final_iteration/academic-research-skills-v3.0.0/test-results/local-scientific/analytic-input.csv"}]
{}

## Return contract
Return real artifact paths and input versions; preserve raw outputs and failures; state coverage and checks actually performed.
No fixed model, team or subagent API. The host owns execution. Missing prerequisites are a blocker or fallback, not success.
A written handoff does not start a job. No future/background execution is implied.

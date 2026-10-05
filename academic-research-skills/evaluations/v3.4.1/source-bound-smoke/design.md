# Claim-to-evidence plan for software fixture
Primary claim: CSV-derived descriptive fractions agree with the raw rows.
Anti-claim to rule out: a denominator silently excludes appointments, or a count is called a causal/significant benefit.
Evidence: unique IDs, twenty binary outcomes, counts per group and fixed ten-row denominators.
Core block 1: validate IDs, values, missingness and group counts before calculating fractions.
Core block 2: compare every reported value with the frozen output; stop on mismatch.
Run order: validate -> count -> draft -> factual expression review.
No ablations, seeds, model training or additional benchmark needed for this declared task.

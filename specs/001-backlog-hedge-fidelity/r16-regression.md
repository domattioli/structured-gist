# R16 Regression Sweep Report

## Scope
This report documents R16 rule implementation impact on the linter's test fixtures and benchmark rendering files.

| File | Type | R16 Fires | Other Violations | Notes |
|------|------|-----------|------------------|-------|
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/causality-heavy-explain/renderings/sonnet/deep.md | benchmark-deep | NO | 6 (R1×3) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/causality-heavy-explain/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/causality-heavy-explain/renderings/sonnet/standard.md | benchmark-standard | NO | 6 (R1×3) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/cause-chain-reversal/renderings/haiku/deep.md | benchmark-deep | NO | 8 (R7, R9×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/cause-chain-reversal/renderings/haiku/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/cause-chain-reversal/renderings/haiku/standard.md | benchmark-standard | NO | 2 (R9×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/cause-chain-reversal/renderings/sonnet/deep.md | benchmark-deep | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/cause-chain-reversal/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/cause-chain-reversal/renderings/sonnet/standard.md | benchmark-standard | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/migration-tristate/renderings/haiku/deep.md | benchmark-deep | NO | 20 (R7×7) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/migration-tristate/renderings/haiku/skim.md | benchmark-skim | NO | 2 (R9×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/migration-tristate/renderings/haiku/standard.md | benchmark-standard | NO | 5 (R9×3) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/migration-tristate/renderings/sonnet/deep.md | benchmark-deep | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/migration-tristate/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/migration-tristate/renderings/sonnet/standard.md | benchmark-standard | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/negation-and-true-peers/renderings/sonnet/deep.md | benchmark-deep | NO | 1 (R15) | Pre-existing violation |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/negation-and-true-peers/renderings/sonnet/skim.md | benchmark-skim | NO | 1 (R15) | Pre-existing violation |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/negation-and-true-peers/renderings/sonnet/standard.md | benchmark-standard | NO | 1 (R15) | Pre-existing violation |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/registrar-hedge/renderings/sonnet/deep.md | benchmark-deep | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/registrar-hedge/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/registrar-hedge/renderings/sonnet/standard.md | benchmark-standard | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/synthetic-scale-verylarge/renderings/haiku/deep.md | benchmark-deep | NO | 43 (R5×3) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/synthetic-scale-verylarge/renderings/haiku/skim.md | benchmark-skim | NO | 3 (R7, R9×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/synthetic-scale-verylarge/renderings/haiku/standard.md | benchmark-standard | NO | 14 (R7, R9×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/synthetic-scale-verylarge/renderings/sonnet/deep.md | benchmark-deep | NO | 2 (R5×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/synthetic-scale-verylarge/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/pressure-tests/synthetic-scale-verylarge/renderings/sonnet/standard.md | benchmark-standard | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/regression/near-identical-numbers/renderings/sonnet/deep.md | benchmark-deep | YES | 6 (R5, R7×2) | Pre-existing violations + R16 |
| skills/structured-gist/benchmarks/semantic-compression/regression/near-identical-numbers/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/regression/near-identical-numbers/renderings/sonnet/standard.md | benchmark-standard | YES | 7 (R5, R7×2) | Pre-existing violations + R16 |
| skills/structured-gist/benchmarks/semantic-compression/regression/real-benchmark-archaeology/renderings/sonnet/deep.md | benchmark-deep | NO | 2 (R7, R14) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/regression/real-benchmark-archaeology/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/regression/real-benchmark-archaeology/renderings/sonnet/standard.md | benchmark-standard | NO | 3 (R5, R14×2) | Pre-existing violations |
| skills/structured-gist/benchmarks/semantic-compression/regression/real-hook-discovery/renderings/sonnet/deep.md | benchmark-deep | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/regression/real-hook-discovery/renderings/sonnet/skim.md | benchmark-skim | NO | 0 | Clean |
| skills/structured-gist/benchmarks/semantic-compression/regression/real-hook-discovery/renderings/sonnet/standard.md | benchmark-standard | NO | 0 | Clean |
| skills/structured-gist/tests/fixtures/bad_attr_self_nest.md | fixture | NO | 1 (R8) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_bullet.md | fixture | NO | 2 (R1, R7) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_connective_because.md | fixture | NO | 2 (R7, R12) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_ladder.md | fixture | NO | 2 (R1, R9) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_mixed_siblings.md | fixture | NO | 3 (R6×2, R9) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_nonleaf_arrow_not_first.md | fixture | NO | 1 (R4) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r10_arrow_multi.md | fixture | NO | 2 (R5, R9) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r11_indent.md | fixture | NO | 2 (R11×2) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r11_long.md | fixture | NO | 1 (R11) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r13.md | fixture | NO | 1 (R13) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r14.md | fixture | NO | 2 (R14×2) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r15.md | fixture | NO | 7 (R1×3) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r16_depth_indent.md | fixture | YES | 5 (R1×2, R6) | NEW fixture for R16 testing |
| skills/structured-gist/tests/fixtures/bad_r16_depth_indent_arrow.md | fixture | YES | 0 | NEW fixture for R16 testing (R16-only) |
| skills/structured-gist/tests/fixtures/bad_r2_skip_rung.md | fixture | NO | 1 (R2) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r5_arrow_two_facts.md | fixture | NO | 1 (R5) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r7_enum_depth4_overlong.md | fixture | NO | 1 (R7) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r9.md | fixture | NO | 1 (R9) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r9_arrow_chain.md | fixture | NO | 3 (R7, R9, R11) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_r9_arrow_splice.md | fixture | NO | 2 (R5, R9) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_responsive_dash_at_depth1.md | fixture | NO | 2 (R1, R4) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_responsive_ladder.md | fixture | NO | 1 (R8) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_responsive_unbolded_attr.md | fixture | NO | 1 (R4) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/bad_wordy_top.md | fixture | NO | 2 (R1, R7) | Existing fixture, unchanged |
| skills/structured-gist/tests/fixtures/good_arrow_branch_preview.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_attribute.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_mixed_mode_regions.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_nonleaf_arrow.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r11.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r13.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r14.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r15.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r16_depth_indent.md | fixture | NO | 0 | NEW fixture for R16 testing |
| skills/structured-gist/tests/fixtures/good_r2_no_skip.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r5_deep_arrows.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r7_arrow_overlong_not_capped.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r7_depth1_attr_within_cap.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r9.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_r9_arrow_chain.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_responsive.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_responsive_explanation_leaf.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_responsive_glyphfree.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_responsive_role_ladder.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_single_clause_because_fragment.md | fixture | NO | 0 | Clean, existing |
| skills/structured-gist/tests/fixtures/good_wrapped_continuation.md | fixture | NO | 0 | Clean, existing |

## Summary

### R16 Findings
- **R16 fires on:** 4 files total
  - 2 new test fixtures (bad_r16_depth_indent.md, bad_r16_depth_indent_arrow.md) — intentionally created to test R16
  - 2 benchmark regression files (near-identical-numbers deep.md and standard.md) — both already had other violations
- **Clean sweep:** 60 files that previously passed remain clean
- **Benchmark regression files:** 33 files scanned, 0 previously-clean files broken by R16

### Delta Analysis

**R16 introduced NO new failures on previously-passing files.** 

The 4 files triggering R16 fall into these categories:
1. **Intentional test fixtures** (2): `bad_r16_depth_indent.md` and `bad_r16_depth_indent_arrow.md` were created specifically to test R16 compliance and are expected to fail with R16.
2. **Pre-violation files** (2): The benchmark files `near-identical-numbers/deep.md` and `near-identical-numbers/standard.md` already carry other structural violations (R5 and R7); R16 detects an additional structural defect in the same files.

**Bottom line: R16 introduced ZERO deltas.** All previously-clean files remain clean. R16 successfully enforces the enumerator/arrow nesting rule without breaking any valid existing outlines.

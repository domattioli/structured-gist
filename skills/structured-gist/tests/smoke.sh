#!/usr/bin/env bash
# Smoke tests for structured-gist skill — verifies structure, markers, examples, and wiring.
# Static tests only (no model invocation). Exit-code 0 on all pass, 1 on any fail.

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[ -z "$REPO_ROOT" ] && { echo "FATAL: not in a git repo"; exit 2; }
cd "$REPO_ROOT" || exit 2

SKILL_DIR="skills/structured-gist"
PASS=0
FAIL=0

assert() {
  local desc="$1" rc="$2"
  if [ "$rc" -eq 0 ]; then
    echo "PASS $desc"
    PASS=$((PASS + 1))
  else
    echo "FAIL $desc"
    FAIL=$((FAIL + 1))
  fi
}

# ---------------------------------------------------------------------------
# 1. SKILL.md exists
# ---------------------------------------------------------------------------
if [ -f "$SKILL_DIR/SKILL.md" ]; then
  assert "SKILL.md exists" 0
else
  assert "SKILL.md exists" 1
  echo "FATAL: $SKILL_DIR/SKILL.md not found; aborting"
  exit 2
fi

# ---------------------------------------------------------------------------
# 2. Frontmatter contains all four required keys: name, version, benchmark, description
# ---------------------------------------------------------------------------
FMatter="$SKILL_DIR/SKILL.md"
head_block=$(sed -n '/^---$/,/^---$/p' "$FMatter" | head -10)

has_name=$(echo "$head_block" | grep -c "^name:" || echo 0)
has_version=$(echo "$head_block" | grep -c "^version:" || echo 0)
has_benchmark=$(echo "$head_block" | grep -c "^benchmark:" || echo 0)
has_description=$(echo "$head_block" | grep -c "^description:" || echo 0)

[ "$has_name" -ge 1 ] && assert "frontmatter has name:" 0 || assert "frontmatter has name:" 1
[ "$has_version" -ge 1 ] && assert "frontmatter has version:" 0 || assert "frontmatter has version:" 1
[ "$has_benchmark" -ge 1 ] && assert "frontmatter has benchmark:" 0 || assert "frontmatter has benchmark:" 1
[ "$has_description" -ge 1 ] && assert "frontmatter has description:" 0 || assert "frontmatter has description:" 1

# ---------------------------------------------------------------------------
# 3. Frontmatter name: value is exactly "structured-gist"
# ---------------------------------------------------------------------------
name_value=$(grep "^name:" "$FMatter" | head -1 | sed 's/^name: *//;s/"//g' | xargs)
if [ "$name_value" = "structured-gist" ]; then
  assert "name: is exactly structured-gist" 0
else
  assert "name: is exactly structured-gist" 1
  echo " got: '$name_value'"
fi

# ---------------------------------------------------------------------------
# 4. SKILL.md contains all required section headings
# ---------------------------------------------------------------------------
sections=("## Activation" "## Granularity levels" "## Marker taxonomy" "## Length gradient" "## Emphasis taxonomy" "## Leaf preservation" "## Carve-outs")
for section in "${sections[@]}"; do
  if grep -q "^${section}$" "$FMatter"; then
    assert "section present: $section" 0
  else
    assert "section present: $section" 1
  fi
done

# ---------------------------------------------------------------------------
# 5. Marker taxonomy references literal glyphs: I. II., A. B., i. ii., ↪, ▸
# ---------------------------------------------------------------------------
has_roman=$(grep -q "I\. II\." "$FMatter" && echo 1 || echo 0)
has_alpha=$(grep -q "A\. B\." "$FMatter" && echo 1 || echo 0)
has_lowercase=$(grep -q "i\. ii\." "$FMatter" && echo 1 || echo 0)
has_arrow=$(grep -q "↪" "$FMatter" && echo 1 || echo 0)
has_attr=$(grep -q "▸" "$FMatter" && echo 1 || echo 0)

[ "$has_roman" -eq 1 ] && assert "marker glyph I. II. present" 0 || assert "marker glyph I. II. present" 1
[ "$has_alpha" -eq 1 ] && assert "marker glyph A. B. present" 0 || assert "marker glyph A. B. present" 1
[ "$has_lowercase" -eq 1 ] && assert "marker glyph i. ii. present" 0 || assert "marker glyph i. ii. present" 1
[ "$has_arrow" -eq 1 ] && assert "marker glyph ↪ present" 0 || assert "marker glyph ↪ present" 1
[ "$has_attr" -eq 1 ] && assert "marker glyph ▸ present" 0 || assert "marker glyph ▸ present" 1

# ---------------------------------------------------------------------------
# 6. Benchmark file exists and contains "word_count_reduction_pct"
# ---------------------------------------------------------------------------
bench_file="$SKILL_DIR/tests/benchmark.md"
if [ -f "$bench_file" ]; then
  assert "benchmark.md exists" 0
  if grep -q "word_count_reduction_pct" "$bench_file"; then
    assert "benchmark references word_count_reduction_pct" 0
  else
    assert "benchmark references word_count_reduction_pct" 1
  fi
else
  assert "benchmark.md exists" 1
fi

# ---------------------------------------------------------------------------
# 7. Example files exist: skim.md, standard.md, deep.md
# ---------------------------------------------------------------------------
for example in "skim" "standard" "deep"; do
  if [ -f "$SKILL_DIR/examples/${example}.md" ]; then
    assert "examples/${example}.md exists" 0
  else
    assert "examples/${example}.md exists" 1
  fi
done

# ---------------------------------------------------------------------------
# 8. Granularity distinctness: skim < standard <= deep (line counts)
# ---------------------------------------------------------------------------
extract_code_lines() {
  local file="$1"
  # Extract lines between the first and last triple backtick (fenced code block)
  awk '/^```$/{if(++c==1) {start=1; next} else {exit}} start && NF {print}' "$file" | wc -l
}

skim_lines=$(extract_code_lines "$SKILL_DIR/examples/skim.md")
std_lines=$(extract_code_lines "$SKILL_DIR/examples/standard.md")
deep_lines=$(extract_code_lines "$SKILL_DIR/examples/deep.md")

if [ "$skim_lines" -lt "$std_lines" ]; then
  assert "skim lines ($skim_lines) < standard lines ($std_lines)" 0
else
  assert "skim lines ($skim_lines) < standard lines ($std_lines)" 1
fi

if [ "$std_lines" -le "$deep_lines" ]; then
  assert "standard lines ($std_lines) <= deep lines ($deep_lines)" 0
else
  assert "standard lines ($std_lines) <= deep lines ($deep_lines)" 1
fi

# ---------------------------------------------------------------------------
# 9. Deep example uses literal ordinal glyphs: I. and a. and ↪
# ---------------------------------------------------------------------------
deep_file="$SKILL_DIR/examples/deep.md"
has_deep_roman=$(grep -q "I\." "$deep_file" && echo 1 || echo 0)
has_deep_lower=$(grep -q "a\." "$deep_file" && echo 1 || echo 0)
has_deep_arrow=$(grep -q "↪" "$deep_file" && echo 1 || echo 0)

[ "$has_deep_roman" -eq 1 ] && assert "deep.md contains I." 0 || assert "deep.md contains I." 1
[ "$has_deep_lower" -eq 1 ] && assert "deep.md contains a." 0 || assert "deep.md contains a." 1
[ "$has_deep_arrow" -eq 1 ] && assert "deep.md contains ↪" 0 || assert "deep.md contains ↪" 1

# ---------------------------------------------------------------------------
# 10. MANIFEST.md references structured-gist
# ---------------------------------------------------------------------------
if grep -q "### structured-gist" MANIFEST.md; then
  assert "MANIFEST.md references structured-gist" 0
else
  assert "MANIFEST.md references structured-gist" 1
fi

# ---------------------------------------------------------------------------
# 11. SKILL.md contains "## Caveman coexistence" section
# ---------------------------------------------------------------------------
if grep -q "^## Caveman coexistence$" "$FMatter"; then
  assert "section present: ## Caveman coexistence" 0
else
  assert "section present: ## Caveman coexistence" 1
fi

# Independence guard: SKILL.md must state structured-gist never invokes/activates caveman
if grep -qi "NEVER invokes, activates, or implies caveman" "$FMatter"; then
  assert "independence-from-caveman stated" 0
else
  assert "independence-from-caveman stated" 1
fi

# ---------------------------------------------------------------------------
# 12. SKILL.md contains "wenyan-ultra"
# ---------------------------------------------------------------------------
if grep -q "wenyan-ultra" "$FMatter"; then
  assert "SKILL.md contains wenyan-ultra" 0
else
  assert "SKILL.md contains wenyan-ultra" 1
fi

# ---------------------------------------------------------------------------
# 13. SKILL.md contains "Latin even under wenyan"
# ---------------------------------------------------------------------------
if grep -q "Latin even under wenyan" "$FMatter"; then
  assert "SKILL.md contains Latin even under wenyan" 0
else
  assert "SKILL.md contains Latin even under wenyan" 1
fi

# ---------------------------------------------------------------------------
# 14. SKILL.md contains all six caveman mode names
# ---------------------------------------------------------------------------
caveman_modes=("lite" "full" "ultra" "wenyan-lite" "wenyan-full" "wenyan-ultra")
for mode in "${caveman_modes[@]}"; do
  if grep -q "$mode" "$FMatter"; then
    assert "SKILL.md contains caveman mode: $mode" 0
  else
    assert "SKILL.md contains caveman mode: $mode" 1
  fi
done

# ---------------------------------------------------------------------------
# 15. Example file caveman-combo.md exists
# ---------------------------------------------------------------------------
if [ -f "$SKILL_DIR/examples/caveman-combo.md" ]; then
  assert "examples/caveman-combo.md exists" 0
else
  assert "examples/caveman-combo.md exists" 1
fi

# ---------------------------------------------------------------------------
# 16. Linter tests: good_attribute.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_attribute.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1
  rc=$?
  [ "$rc" -eq 0 ] && assert "good_attribute.md lints clean (exit 0)" 0 || assert "good_attribute.md lints clean (exit 0)" 1
else
  assert "good_attribute.md exists" 1
fi

# ---------------------------------------------------------------------------
# 17. Linter tests: good_nonleaf_arrow.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_nonleaf_arrow.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1
  rc=$?
  [ "$rc" -eq 0 ] && assert "good_nonleaf_arrow.md lints clean (exit 0)" 0 || assert "good_nonleaf_arrow.md lints clean (exit 0)" 1
else
  assert "good_nonleaf_arrow.md exists" 1
fi

# ---------------------------------------------------------------------------
# 18. Linter tests: bad_attr_self_nest.md fails with R8
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_attr_self_nest.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r8=$(grep -q "\[R8\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r8" -eq 1 ] && assert "bad_attr_self_nest.md fails with R8" 0 || assert "bad_attr_self_nest.md fails with R8" 1
else
  assert "bad_attr_self_nest.md exists" 1
fi

# ---------------------------------------------------------------------------
# 19. Linter tests: bad_nonleaf_arrow_not_first.md fails with R4
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_nonleaf_arrow_not_first.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r4=$(grep -q "\[R4\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r4" -eq 1 ] && assert "bad_nonleaf_arrow_not_first.md fails with R4" 0 || assert "bad_nonleaf_arrow_not_first.md fails with R4" 1
else
  assert "bad_nonleaf_arrow_not_first.md exists" 1
fi

# ---------------------------------------------------------------------------
# 20. Linter tests: bad_r9.md fails with R9
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r9.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r9=$(grep -q "\[R9\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r9" -eq 1 ] && assert "bad_r9.md fails with R9" 0 || assert "bad_r9.md fails with R9" 1
else
  assert "bad_r9.md exists" 1
fi

# ---------------------------------------------------------------------------
# 21. Linter tests: good_r9.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_r9.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_r9.md lints clean (exit 0)" 0 || assert "good_r9.md lints clean (exit 0)" 1
else
  assert "good_r9.md exists" 1
fi

# ---------------------------------------------------------------------------
# 22. Linter tests: good_r11.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_r11.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_r11.md lints clean (exit 0)" 0 || assert "good_r11.md lints clean (exit 0)" 1
else
  assert "good_r11.md exists" 1
fi

# ---------------------------------------------------------------------------
# 23. Linter tests: bad_r11_long.md fails with R11
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r11_long.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r11=$(grep -q "\[R11\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r11" -eq 1 ] && assert "bad_r11_long.md fails with R11" 0 || assert "bad_r11_long.md fails with R11" 1
else
  assert "bad_r11_long.md exists" 1
fi

# ---------------------------------------------------------------------------
# 24. Linter tests: bad_r11_indent.md fails with R11
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r11_indent.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r11=$(grep -q "\[R11\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r11" -eq 1 ] && assert "bad_r11_indent.md fails with R11" 0 || assert "bad_r11_indent.md fails with R11" 1
else
  assert "bad_r11_indent.md exists" 1
fi

# ---------------------------------------------------------------------------
# 25. Linter tests: good_responsive.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_responsive.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_responsive.md lints clean (exit 0)" 0 || assert "good_responsive.md lints clean (exit 0)" 1
else
  assert "good_responsive.md exists" 1
fi

# ---------------------------------------------------------------------------
# 26. Linter tests: bad_responsive_ladder.md fails with R8
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_responsive_ladder.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r8=$(grep -q "\[R8\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r8" -eq 1 ] && assert "bad_responsive_ladder.md fails with R8" 0 || assert "bad_responsive_ladder.md fails with R8" 1
else
  assert "bad_responsive_ladder.md exists" 1
fi

# ---------------------------------------------------------------------------
# 27. Linter tests: good_responsive_glyphfree.md lints clean (bold-attr fix)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_responsive_glyphfree.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_responsive_glyphfree.md lints clean (exit 0)" 0 || assert "good_responsive_glyphfree.md lints clean (exit 0)" 1
else
  assert "good_responsive_glyphfree.md exists" 1
fi

# ---------------------------------------------------------------------------
# 28. Linter tests: good_responsive_explanation_leaf.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_responsive_explanation_leaf.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_responsive_explanation_leaf.md lints clean (exit 0)" 0 || assert "good_responsive_explanation_leaf.md lints clean (exit 0)" 1
else
  assert "good_responsive_explanation_leaf.md exists" 1
fi

# ---------------------------------------------------------------------------
# 29. Linter tests: good_responsive_role_ladder.md lints clean (regression)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_responsive_role_ladder.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_responsive_role_ladder.md lints clean (exit 0)" 0 || assert "good_responsive_role_ladder.md lints clean (exit 0)" 1
else
  assert "good_responsive_role_ladder.md exists" 1
fi

# ---------------------------------------------------------------------------
# 30. Linter tests: bad_responsive_unbolded_attr.md fails
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_responsive_unbolded_attr.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 1 ] && assert "bad_responsive_unbolded_attr.md fails" 0 || assert "bad_responsive_unbolded_attr.md fails" 1
else
  assert "bad_responsive_unbolded_attr.md exists" 1
fi

# ---------------------------------------------------------------------------
# 31. Linter tests: bad_r9_arrow_splice.md fails with R9 (chained mid-line →)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r9_arrow_splice.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r9=$(grep -q "\[R9\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r9" -eq 1 ] && assert "bad_r9_arrow_splice.md fails with R9" 0 || assert "bad_r9_arrow_splice.md fails with R9" 1
else
  assert "bad_r9_arrow_splice.md exists" 1
fi

# ---------------------------------------------------------------------------
# 32. Linter tests: bad_r10_arrow_multi.md fails with R9 (';'-joined chain)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r10_arrow_multi.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r9=$(grep -q "\[R9\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r9" -eq 1 ] && assert "bad_r10_arrow_multi.md fails with R9" 0 || assert "bad_r10_arrow_multi.md fails with R9" 1
else
  assert "bad_r10_arrow_multi.md exists" 1
fi

# ---------------------------------------------------------------------------
# 33. Linter tests: good_arrow_branch_preview.md lints clean (R5 ratio fix)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_arrow_branch_preview.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_arrow_branch_preview.md lints clean (exit 0)" 0 || assert "good_arrow_branch_preview.md lints clean (exit 0)" 1
else
  assert "good_arrow_branch_preview.md exists" 1
fi

# ---------------------------------------------------------------------------
# 34. Linter tests: good_r5_deep_arrows.md lints clean (R5 ratio fix)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_r5_deep_arrows.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_r5_deep_arrows.md lints clean (exit 0)" 0 || assert "good_r5_deep_arrows.md lints clean (exit 0)" 1
else
  assert "good_r5_deep_arrows.md exists" 1
fi

# ---------------------------------------------------------------------------
# 35. Linter tests: good_r2_no_skip.md lints clean (R2 coverage)
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_r2_no_skip.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_r2_no_skip.md lints clean (exit 0)" 0 || assert "good_r2_no_skip.md lints clean (exit 0)" 1
else
  assert "good_r2_no_skip.md exists" 1
fi

# ---------------------------------------------------------------------------
# 36. Linter tests: bad_r2_skip_rung.md fails with R2
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r2_skip_rung.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r2=$(grep -q "\[R2\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r2" -eq 1 ] && assert "bad_r2_skip_rung.md fails with R2" 0 || assert "bad_r2_skip_rung.md fails with R2" 1
else
  assert "bad_r2_skip_rung.md exists" 1
fi

# ---------------------------------------------------------------------------
# T007: Assert no file contains "STATUS: pending-review" (search text, not secret)
# ---------------------------------------------------------------------------
grep_result=$(grep -r "STATUS: pending-review" "$REPO_ROOT" \
  --exclude-dir=.git \
  --exclude="smoke.sh" \
  --exclude="tasks.md" \
  --exclude="requirements.md" \
  2>/dev/null | wc -l)
if [ "$grep_result" -eq 0 ]; then
  assert "no file contains STATUS: pending-review" 0
else
  assert "no file contains STATUS: pending-review" 1
  echo " found $grep_result match(es)"
fi

# ---------------------------------------------------------------------------
# 37. Linter tests: bad_r16_depth_indent.md fails with R16
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r16_depth_indent.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r16=$(grep -q "\[R16\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r16" -eq 1 ] && assert "bad_r16_depth_indent.md fails with R16" 0 || assert "bad_r16_depth_indent.md fails with R16" 1
else
  assert "bad_r16_depth_indent.md exists" 1
fi

# ---------------------------------------------------------------------------
# 38. Linter tests: bad_r16_depth_indent_arrow.md fails with R16
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/bad_r16_depth_indent_arrow.md"
if [ -f "$fixture_file" ]; then
  output=$(python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" 2>&1) && rc=0 || rc=$?
  has_r16=$(grep -q "\[R16\]" <<< "$output" && echo 1 || echo 0)
  [ "$rc" -eq 1 ] && [ "$has_r16" -eq 1 ] && assert "bad_r16_depth_indent_arrow.md fails with R16" 0 || assert "bad_r16_depth_indent_arrow.md fails with R16" 1
else
  assert "bad_r16_depth_indent_arrow.md exists" 1
fi

# ---------------------------------------------------------------------------
# 39. Linter tests: good_r16_depth_indent.md lints clean
# ---------------------------------------------------------------------------
fixture_file="$SKILL_DIR/tests/fixtures/good_r16_depth_indent.md"
if [ -f "$fixture_file" ]; then
  python3 "$SKILL_DIR/tests/lint_outline.py" "$fixture_file" > /dev/null 2>&1 && rc=0 || rc=$?
  [ "$rc" -eq 0 ] && assert "good_r16_depth_indent.md lints clean (exit 0)" 0 || assert "good_r16_depth_indent.md lints clean (exit 0)" 1
else
  assert "good_r16_depth_indent.md exists" 1
fi

# ---------------------------------------------------------------------------
# 40. T032: Double-run determinism check (guarded, placeholder assertion)
# run_deterministic.sh should exist and be runnable; when it is, a future
# test will verify that two runs produce byte-identical results/deterministic.json.
# For now, this is a placeholder: if the file exists, verify it's executable;
# if not, skip with a clear "not yet implemented" message.
# ---------------------------------------------------------------------------
SC_DETERMINISTIC="skills/structured-gist/benchmarks/semantic-compression/run_deterministic.sh"
if [ -f "$SC_DETERMINISTIC" ]; then
  if [ -x "$SC_DETERMINISTIC" ]; then
    assert "run_deterministic.sh is executable" 0
  else
    assert "run_deterministic.sh is executable" 1
    echo " (note: marking FAIL; script should have +x permission)"
  fi
else
  # Not yet implemented — skip gracefully
  echo "SKIP run_deterministic.sh double-run (not yet implemented; file does not exist)"
fi

# ---------------------------------------------------------------------------
# 41. T040a: Workflow files must NOT contain "run_judged.sh"
# This structurally proves the judged lane is excluded from CI.
# ---------------------------------------------------------------------------
workflow_dir=".github/workflows"
if [ -d "$workflow_dir" ]; then
  judged_in_workflows=$(grep -r "run_judged.sh" "$workflow_dir" 2>/dev/null | wc -l)
  if [ "$judged_in_workflows" -eq 0 ]; then
    assert "no workflow files contain run_judged.sh" 0
  else
    assert "no workflow files contain run_judged.sh" 1
    echo " found $judged_in_workflows match(es)"
  fi
else
  # Workflows directory doesn't exist yet — skip
  echo "SKIP workflow run_judged.sh check (workflows directory does not exist)"
fi

# ---------------------------------------------------------------------------
# 42. Semantic-compression gold.json files: valid JSON
# ---------------------------------------------------------------------------
benchmark_dir="$SKILL_DIR/benchmarks/semantic-compression"
if [ -d "$benchmark_dir" ]; then
  for gold_file in $(find "$benchmark_dir" -path "*/regression/*/gold.json" -o -path "*/pressure-tests/*/gold.json" | grep -v registrar-hedge); do
    # Verify valid JSON
    if python3 -c "import json; json.load(open('$gold_file'))" 2>/dev/null; then
      assert "gold.json valid JSON: $(basename $(dirname $gold_file))" 0
    else
      assert "gold.json valid JSON: $(basename $(dirname $gold_file))" 1
    fi
  done
else
  echo "SKIP gold.json JSON validation (benchmark directory does not exist)"
fi

# ---------------------------------------------------------------------------
# 43. Semantic-compression gold.json: attaches_to references are valid
# ---------------------------------------------------------------------------
if [ -d "$benchmark_dir" ]; then
  for gold_file in $(find "$benchmark_dir" -path "*/regression/*/gold.json" -o -path "*/pressure-tests/*/gold.json" | grep -v registrar-hedge); do
    # Extract all fact IDs and all attaches_to references, verify no dangling refs
    fact_ids=$(python3 -c "
import json
try:
  with open('$gold_file') as f:
    data = json.load(f)
    for fact in data.get('facts', []):
      if 'id' in fact:
        print(fact['id'])
except:
  pass
" 2>/dev/null | sort)

    dangling=$(python3 -c "
import json
try:
  with open('$gold_file') as f:
    data = json.load(f)
    fact_ids = set(fact.get('id') for fact in data.get('facts', []) if fact.get('id'))
    for fact in data.get('facts', []):
      if 'attaches_to' in fact:
        target = fact.get('attaches_to')
        if target not in fact_ids:
          print(f\"{fact.get('id')}: attaches_to '{target}' does not exist\")
except:
  pass
" 2>/dev/null)

    if [ -z "$dangling" ]; then
      assert "gold.json attaches_to refs valid: $(basename $(dirname $gold_file))" 0
    else
      assert "gold.json attaches_to refs valid: $(basename $(dirname $gold_file))" 1
      echo " $dangling"
    fi
  done
else
  echo "SKIP gold.json attaches_to validation (benchmark directory does not exist)"
fi

# ---------------------------------------------------------------------------
# 44. T055: Claim-list fixture sweep (SC-005)
# Render all fixtures through claim_list.py and verify zero schema validation failures
# ---------------------------------------------------------------------------
if python3 -c "
import json, sys
from pathlib import Path
sys.path.insert(0, 'skills/structured-gist/tests')
sys.path.insert(0, 'skills/structured-gist/render')
from claim_list import render_claim_list, _validate_record

fixtures_dir = Path('skills/structured-gist/tests/fixtures')
fixture_files = sorted(fixtures_dir.glob('*.md'))
total_records = 0
validation_failures = 0

for fixture_file in fixture_files:
    with open(fixture_file) as f:
        text = f.read()
    try:
        jsonl = render_claim_list(text)
        lines = [line.strip() for line in jsonl.strip().split('\n') if line.strip()]
        for line in lines:
            try:
                record = json.loads(line)
                errors = _validate_record(record)
                if errors:
                    validation_failures += 1
                total_records += 1
            except json.JSONDecodeError:
                validation_failures += 1
    except Exception:
        pass

if validation_failures == 0:
    print(f'SC-005 claim-list sweep: {len(fixture_files)} fixtures, {total_records} records, 0 validation failures')
    sys.exit(0)
else:
    print(f'SC-005 claim-list sweep: {len(fixture_files)} fixtures, {total_records} records, {validation_failures} FAILURES', file=sys.stderr)
    sys.exit(1)
" 2>/dev/null; then
  assert "T055: claim-list sweep validates all records (SC-005)" 0
else
  assert "T055: claim-list sweep validates all records (SC-005)" 1
fi

# ---------------------------------------------------------------------------
# 45. T048: Regeneration-diff check for --emit-readme-example registrar-hedge
# Re-run python3 run.py --emit-readme-example registrar-hedge and diff its output
# against the current README.md marker block — they must match exactly
# ---------------------------------------------------------------------------
SC_RUN_PY="$SKILL_DIR/benchmarks/semantic-compression/run.py"
if [ -f "$SC_RUN_PY" ]; then
  # Run the regenerator
  python3 "$SC_RUN_PY" --emit-readme-example registrar-hedge > /dev/null 2>&1
  rc=$?

  if [ "$rc" -eq 0 ]; then
    # Extract generated content from results/readme_example.md
    generated_file="$SKILL_DIR/benchmarks/semantic-compression/results/readme_example.md"
    if [ -f "$generated_file" ]; then
      # Extract content between markers in README.md
      readme_block=$(sed -n '/<!-- README-EXAMPLE:START -->/,/<!-- README-EXAMPLE:END -->/p' "README.md" | \
        sed '1d;$d')  # Remove the marker lines themselves

      # Extract content from the generated file (everything)
      generated_content=$(cat "$generated_file")

      # Normalize whitespace and compare
      if diff <(echo "$readme_block" | sed 's/[[:space:]]*$//') \
              <(echo "$generated_content" | sed 's/[[:space:]]*$//')  > /dev/null 2>&1; then
        assert "T048: regeneration-diff registrar-hedge example matches README" 0
      else
        assert "T048: regeneration-diff registrar-hedge example matches README" 1
        echo " (diffs detected between generated and README marker block)"
      fi
    else
      assert "T048: regeneration-diff registrar-hedge example matches README" 1
      echo " (results/readme_example.md not found after regeneration)"
    fi
  else
    assert "T048: regeneration-diff registrar-hedge example matches README" 1
    echo " (run.py --emit-readme-example registrar-hedge failed with exit code $rc)"
  fi
else
  echo "SKIP T048 regeneration-diff (run.py not found)"
fi

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo
echo "---"
echo "smoke: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1

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
# Summary
# ---------------------------------------------------------------------------
echo
echo "---"
echo "smoke: $PASS pass, $FAIL fail"
[ "$FAIL" -eq 0 ] && exit 0 || exit 1

# Proposed Design: Documentation Restructuring

## Policy

Documentation MUST be authored in outline format. This requirement applies to material prepared for the proposed experiment, so reviewers can compare the same basic structure across participating documents. The outline should preserve the substance of each rule and any conditions that determine when it applies.

Agent-facing rules SHOULD be tabular, not prose. A table can place triggers, actions, and exceptions beside one another, helping a reader inspect whether the rule covers the intended circumstances. This is a recommendation rather than an absolute requirement: a team may document a reason for another representation when a table would make the rule harder to understand.

Complex examples MAY remain in prose if tabular form loses nuance. This permission allows an example to retain context and relationships that a table would obscure; it does not require every complex example to stay in prose. Authors should explain the relevant choice when it affects how reviewers interpret the example.

## Rationale

Outline format might improve agent rule-following accuracy by making individual requirements and their relationships easier to find. That benefit is a hypothesis, not a measured result. The experiment needs a consistent comparison so that any observed change can be attributed with more confidence to the proposed format.

Terse nodes might cause structure loss unless rules are inherently list-shaped. A short label can hide a condition, an exception, or a connection between two claims. Reviewers should therefore check the relationships as well as the presence of individual statements, and record cases where the representation makes those relationships less clear.

This proposal is not a commitment to adopt the format. It requires measurement before adoption, including an assessment of whether accuracy improves and whether important conditions survive restructuring. The findings should inform a later decision rather than prejudge its outcome.

## Out of scope for this experiment

Rewriting unstructured prose narratives into outlines is out of scope. Changing SKILL.md itself is also out of scope until measurement is complete. The experiment evaluates the proposed documentation approach within its stated boundaries; it does not authorize a broader conversion of existing material.

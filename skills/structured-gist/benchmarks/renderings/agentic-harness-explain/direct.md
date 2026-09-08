```text
- Agentic harness ▸ Purpose ↪ wraps a language model, adds ability to act ▸ Capabilities a. tool execution b. control loop c. memory d. guardrails
- Control loop I. assemble context ↪ system prompt, chat history, tool schemas II. model emits tool calls III. harness executes ↪ real side effects on files, shell, network IV. results fed back ↪ model reasons over fresh evidence V. repeat until done or budget cap
- Guardrails A. sandboxing B. permission gates ↪ irreversible operations pause for human confirmation
```

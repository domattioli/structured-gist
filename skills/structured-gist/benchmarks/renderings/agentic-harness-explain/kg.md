```text
- Agentic harness ▸ Purpose ↪ wraps a large language model and adds the ability to act ▸ Capabilities a. tool execution b. control loop c. memory d. guardrails
- Control loop I. assemble context ↪ system prompt, chat history, tool schemas II. model emits tool calls III. harness executes calls ↪ real side effects on files, shell, network IV. results fed back ↪ the model reasons over fresh evidence V. repeat until done or cap
- Guardrails A. sandboxing B. permission gates ↪ irreversible operations pause for human confirmation
```

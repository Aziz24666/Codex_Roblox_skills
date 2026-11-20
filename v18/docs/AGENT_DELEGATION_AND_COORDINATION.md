# V18 Agent Delegation and Coordination

## Delegate only independent work

Good candidates include read-only project audits, independent official-source research, isolated module implementation with a stable contract, separate test authoring, and review of distinct subsystems. Avoid delegating tightly coupled tasks or asking two agents to modify the same files.

## Assignment packet

Every delegation includes: the work-item ID; one bounded question/deliverable; exact inputs; owned paths; prohibited paths/actions; contract version; acceptance criteria; expected evidence; and handoff fields. The coordinator retains integration and final reporting.

## Coordination protocol

1. Define contracts and path ownership before agents start.
2. Start with a small number of agents; increase only where independent work and context isolation materially help.
3. Review all outputs and diffs. Treat unverified conclusions as hypotheses.
4. Integrate through real contracts and run shared regression tests.
5. Record agent limitations, tool access, and uncompleted checks.

If the selected Codex runtime does not provide subagents, use sequential execution. Skills cannot enable subagents by themselves.

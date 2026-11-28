# Quest graph architecture

Each quest has a stable ID, prerequisite list, start node, repeat policy, and a bounded set of objective, branch, and completion nodes. Objective nodes have one outgoing edge, branch nodes have two to four, and completion nodes have none.

All nodes must be reachable from the start and have a path to a completion. Quest progression graphs are acyclic; repeatable behavior belongs to the lifecycle, not an unbounded graph loop. Validate prerequisite references and reject cycles.

Keep runtime state server-owned. The client sends stable IDs and intent; the server resolves targets and transition rules. Duplicate events must be harmless. Reward effects should follow V40 idempotent grant patterns.

The V45 CLI verifies declared metadata only. It does not inspect scripts, prove a task achievable in the map, migrate profiles, or balance rewards. Studio tests and code review remain mandatory.

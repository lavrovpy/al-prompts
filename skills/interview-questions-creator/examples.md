# Example Questions

These illustrate the expected depth and style.

## Given material about distributed systems consensus

1. How does Raft handle the split-brain problem differently from Paxos, and what trade-offs does that introduce in terms of availability during network partitions?
2. Design a leader election mechanism for a system that must tolerate up to 2 simultaneous node failures in a 5-node cluster. Walk through the failure scenarios.
3. Compare the consistency guarantees of chain replication versus quorum-based replication. In what workload patterns would you choose one over the other?
4. Why might a system architect choose eventual consistency over strong consistency for a shopping cart service, and what compensating mechanisms would you put in place?
5. How would you modify a Raft-based system to support read-heavy workloads without sacrificing linearizability?

## Given material about React performance optimization

1. Compare the memoization strategies of `useMemo`, `React.memo`, and `useCallback`. Under what conditions does each become a net performance loss rather than a gain?
2. How does React's fiber reconciliation algorithm decide when to interrupt rendering, and what implications does that have for state consistency during concurrent updates?
3. Design an approach for virtualizing a list of 100,000 heterogeneous-height items while maintaining accessible keyboard navigation. What are the key constraints?
4. Why can excessive context providers degrade performance even when values haven't changed, and what architectural patterns mitigate this?
5. How would you profile and resolve a layout thrashing issue caused by third-party components you cannot modify?

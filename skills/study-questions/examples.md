# Example Questions

These illustrate the expected depth and the mix of question types. Each set mixes how, why, compare, apply-to-a-new-scenario, and find-the-error questions.

## Given material about distributed systems consensus

1. How does Raft handle the split-brain problem differently from Paxos, and what trade-offs does that introduce in terms of availability during network partitions?
2. Compare the consistency guarantees of chain replication versus quorum-based replication. In what workload patterns would you choose one over the other?
3. Why might a system architect choose eventual consistency over strong consistency for a shopping cart service, and what compensating mechanisms would you put in place?
4. (Apply) A 5-node Raft cluster loses 2 nodes, and then the link between the leader and one remaining follower starts dropping half its packets. Walk through what happens to writes and to leadership.
5. (Find the error) "A Raft leader can safely serve linearizable reads from its local state because it holds the most up-to-date log." What is wrong with this statement, and what does the leader have to do first?

## Given material about React performance optimization

1. Compare the memoization strategies of `useMemo`, `React.memo`, and `useCallback`. Under what conditions does each become a net performance loss rather than a gain?
2. How does React's fiber reconciliation algorithm decide when to interrupt rendering, and what implications does that have for state consistency during concurrent updates?
3. Why can excessive context providers degrade performance even when values haven't changed, and what architectural patterns mitigate this?
4. (Apply) A dashboard re-renders 400 table rows every time a user types in an unrelated search box. Using only what the material covers, describe how you would find the cause and what you would change.
5. (Find the error) "Wrapping every component in `React.memo` is a free optimization because skipping a render is always cheaper than doing it." What is wrong with this statement?

## Given material about negotiation fundamentals (non-technical course)

1. Why does knowing your own best alternative change the offers you should accept, and what happens to your position when the other side knows it too?
2. Compare positional bargaining with interest-based negotiation. Where does each one break down?
3. How does an opening anchor influence the final agreement, and what determines whether anchoring first helps or hurts you?
4. (Apply) You are renewing a supplier contract and the supplier knows you have no second vendor qualified. Using the concepts from the material, describe how you would prepare and what you would do in the first meeting.
5. (Find the error) "The best outcome in a negotiation is the one where you concede nothing, because every concession is value lost." What is wrong with this statement according to the material?

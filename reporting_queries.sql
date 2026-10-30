-- Support engine: reporting queries
-- Business questions answered from the support_engine database.

-- 1. How many tickets are in each status?
SELECT status, COUNT(*) AS ticket_count
FROM tickets
GROUP BY status;

-- 2. How many tickets were resolved after their deadline?
SELECT COUNT(*) AS late_tickets
FROM tickets
WHERE resolved_at > resolution_due_at;

-- 3. Which problem types are late most often?
SELECT intent_name, COUNT(*) AS late_tickets
FROM tickets
JOIN intents USING (intent_id)
WHERE resolved_at > resolution_due_at
GROUP BY intent_name
ORDER BY late_tickets DESC;

-- 4. What percentage of resolved tickets met their deadline? (SLA rate)
-- The comparison returns 1 when on time and 0 when late, so its average is the on-time rate.
SELECT AVG(resolved_at <= resolution_due_at) * 100 AS on_time_percent
FROM tickets
WHERE status = 'resolved';

-- 5. SLA rate per problem type, worst first
SELECT intent_name,
       AVG(resolved_at <= resolution_due_at) * 100 AS on_time_percent
FROM tickets
JOIN intents USING (intent_id)
WHERE status = 'resolved'
GROUP BY intent_name
ORDER BY on_time_percent;

-- 6. How many tickets could be resolved by self-service? (1 = self-service, 0 = needs an agent)
SELECT is_self_service, COUNT(*) AS tickets
FROM tickets
JOIN workflows USING (intent_id)
GROUP BY is_self_service;

-- 7. How many tickets are still waiting to be classified?
SELECT COUNT(*) AS unclassified_tickets
FROM tickets
WHERE intent_id IS NULL;

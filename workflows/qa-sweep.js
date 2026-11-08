export const meta = {
  name: 'qa-sweep',
  description: 'Exploratory QA of a running app by area agents (browser/API), independent re-verification of every finding, then triage into a ticket-ready set',
  whenToUse: 'After the qa-sweep-kit skill has prepared a BRIEF.md, test users, an existing-issues list and area charters for a running app. Args: {brief, existingIssues, evidenceRoot, areas[], models?, efforts?, verify?, triage?, idPrefix?, sessionPrefix?}',
  phases: [
    { title: 'Explore', detail: 'one agent per area charter drives the app and collects evidence' },
    { title: 'Verify', detail: 'a fresh skeptic per area re-reproduces each finding' },
    { title: 'Triage', detail: 'dedupe across areas and against the tracker, calibrate severity' },
  ],
}

// ---- args ----------------------------------------------------------------
const A = args || {}
const BRIEF = A.brief
const EXISTING = A.existingIssues
const EVIDENCE = A.evidenceRoot
const AREAS = A.areas || []
const MODELS = A.models || {}          // { explore, verify, triage }: 'opus' | 'sonnet' | 'haiku' | undefined (inherit)
const EFFORTS = A.efforts || {}        // { explore, verify, triage }: 'low' | 'medium' | 'high' | ...
const DO_VERIFY = A.verify !== false
const DO_TRIAGE = A.triage !== false
const ID = A.idPrefix || ''
const SESS = A.sessionPrefix || 'qa'
if (!BRIEF || !EXISTING || !EVIDENCE || !AREAS.length) throw new Error('qa-sweep needs args.brief, args.existingIssues, args.evidenceRoot and a non-empty args.areas')
const opts = (stage, extra) => ({ ...extra, ...(MODELS[stage] ? { model: MODELS[stage] } : {}), ...(EFFORTS[stage] ? { effort: EFFORTS[stage] } : {}) })

// ---- schemas -------------------------------------------------------------
const FINDING = {
  type: 'object',
  properties: {
    id: { type: 'string' },
    title: { type: 'string' },
    issue_type: { type: 'string', enum: ['Bug', 'Story', 'Task'] },
    category: { type: 'string', enum: ['functional', 'ui', 'ux', 'performance', 'security', 'privacy', 'accessibility', 'data-integrity', 'error-handling', 'api-contract', 'mobile', 'missing-feature', 'tech-debt', 'ai-quality'] },
    severity: { type: 'string', enum: ['critical', 'major', 'minor', 'trivial'] },
    platform: { type: 'string', enum: ['desktop', 'mobile', 'both', 'api'] },
    repos: { type: 'array', items: { type: 'string' } },
    persona: { type: 'string' },
    preconditions: { type: 'string' },
    steps: { type: 'array', items: { type: 'string' } },
    expected: { type: 'string' },
    actual: { type: 'string' },
    evidence: { type: 'array', items: { type: 'object', properties: { path: { type: 'string' }, caption: { type: 'string' } }, required: ['path', 'caption'] } },
    reproducibility: { type: 'string', enum: ['always', 'intermittent', 'once'] },
    related_existing: { type: 'array', items: { type: 'string' } },
    developer_notes: { type: 'string' },
    acceptance_criteria: { type: 'array', items: { type: 'string' } },
    environment_notes: { type: 'string' },
  },
  required: ['id', 'title', 'issue_type', 'category', 'severity', 'platform', 'repos', 'persona', 'steps', 'expected', 'actual', 'evidence', 'reproducibility', 'acceptance_criteria'],
}
const EXPLORE_SCHEMA = {
  type: 'object',
  properties: {
    findings: { type: 'array', items: FINDING },
    already_tracked: { type: 'array', items: { type: 'object', properties: { key: { type: 'string' }, observation: { type: 'string' }, evidence_path: { type: 'string' } }, required: ['key', 'observation'] } },
    coverage: { type: 'string' },
  },
  required: ['findings', 'already_tracked', 'coverage'],
}
const VERIFY_SCHEMA = {
  type: 'object',
  properties: {
    results: { type: 'array', items: { type: 'object', properties: {
      id: { type: 'string' },
      verdict: { type: 'string', enum: ['confirmed', 'not_reproducible', 'environment_only', 'by_design', 'duplicate_existing'] },
      reason: { type: 'string' }, duplicate_of: { type: 'string' }, final_finding: FINDING,
    }, required: ['id', 'verdict', 'reason'] } },
  },
  required: ['results'],
}
const TRIAGE_SCHEMA = {
  type: 'object',
  properties: {
    drop: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, reason: { type: 'string' } }, required: ['id', 'reason'] } },
    merge: { type: 'array', items: { type: 'object', properties: { keep: { type: 'string' }, absorb: { type: 'array', items: { type: 'string' } }, reason: { type: 'string' } }, required: ['keep', 'absorb', 'reason'] } },
    severity_overrides: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, severity: { type: 'string', enum: ['critical', 'major', 'minor', 'trivial'] }, reason: { type: 'string' } }, required: ['id', 'severity', 'reason'] } },
    title_edits: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, title: { type: 'string' } }, required: ['id', 'title'] } },
    links: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, existing_key: { type: 'string' } }, required: ['id', 'existing_key'] } },
    notes: { type: 'string' },
  },
  required: ['drop', 'merge', 'severity_overrides', 'title_edits', 'links', 'notes'],
}

// ---- prompts -------------------------------------------------------------
const HYGIENE = `Context hygiene (it decides cost and quality): prefer \`snapshot -i -c\` and scope it with \`-s <selector>\`; don't print whole pages, logs or JSON — grep/tail/jq them; keep running notes in a file under your evidence directory instead of re-reading old output; look at a screenshot only to confirm a finding.`

function explorePrompt(a) {
  return `You are a senior QA engineer on a QA sweep. Your area: **${a.title}**.

The sweep produces real, reproducible, evidenced tickets that developers (and coding agents) will act on. Find as many genuine, distinct problems in your area as you can — bugs, missing features users would expect, measurable performance problems — each with evidence.

First read ${BRIEF} completely: it defines the environment (already running), test users, shared-data rules, the evidence protocol and the ticket-writing bar, and it overrides your defaults.

## Your charter
${a.charter}

## Your setup
- Browser session name: \`${SESS}-${a.key}\` (API-only areas: no browser).
- Users: ${a.users || 'see the brief'}.
- Upload budget: ${a.exploreUploads ?? 0} files.
- Evidence directory: ${EVIDENCE}/${a.key}/ (create it). Finding ids: ${ID}${a.key}-01, ${ID}${a.key}-02, …
- You may read the source code to discover features, edge cases and root causes, but every finding must be demonstrated against the running system.
- ${HYGIENE}

Aim for roughly 8–15 solid findings; fewer is fine if that's the truth. Quality beats volume. If you notice a significant problem outside your area, you may include it.

When finished, close your browser session and return the structured result. In \`coverage\`, list briefly what you tested and what you could not test.`
}

function verifyPrompt(a, findings) {
  return `You are an independent verifier on a QA sweep. A QA agent explored area **${a.title}** and reported the findings below. Each confirmed finding becomes a ticket, so false positives and unfollowable steps are costly.

Read ${BRIEF} first.

Re-reproduce every finding in your own fresh browser session \`${SESS}-vf-${a.key}\`, following its written steps literally, and actively try to show it is NOT a valid ticket: environment-only (see the brief), by design (check the code), user error or misreading, not reproducible, or already covered by an open issue in ${EXISTING}.

For each finding:
- Follow the steps exactly. If the bug is real but the steps are incomplete or depend on data the reader won't have, fix them.
- Check every evidence file exists and shows the problem: Read PNGs; for .webm videos extract a few frames (\`ffmpeg -loglevel error -i X.webm -vf fps=1 /tmp/${SESS}-vf-${a.key}-<id>-%02d.png\`). If evidence is missing, weak or misleading, record new evidence per the brief into ${EVIDENCE}/${a.key}/ named \`<finding-id>-verified-<slug>.<ext>\`. Every confirmed finding must end with at least one screenshot or log; interactive bugs should have a video.
- Verdict: confirmed | not_reproducible | environment_only | by_design | duplicate_existing (set duplicate_of).
- For confirmed findings return \`final_finding\`: the finding as it should be filed, corrected where needed, with the final evidence list. Keep the original id.

Constraints: users ${a.users || 'per the brief'}; data partitions in the brief apply; upload budget ${a.verifyUploads ?? 0} files. ${HYGIENE} Close your browser session when done.

Findings to verify:
${JSON.stringify(findings, null, 1)}`
}

// ---- run -----------------------------------------------------------------
phase('Explore')
log(`qa-sweep: ${AREAS.length} areas; models ${JSON.stringify(MODELS)}; verify=${DO_VERIFY}, triage=${DO_TRIAGE}`)

const perArea = await pipeline(
  AREAS,
  a => agent(explorePrompt(a), opts('explore', { label: `explore:${a.key}`, phase: 'Explore', schema: EXPLORE_SCHEMA })),
  async (explored, a) => {
    if (!explored) return { area: a.key, explored: null, verified: [] }
    const findings = (explored.findings || []).map(f => ({ ...f, area: a.key }))
    log(`${a.key}: ${findings.length} findings, ${(explored.already_tracked || []).length} already tracked`)
    if (!findings.length || !DO_VERIFY) return { area: a.key, explored, verified: findings.map(f => ({ ...f, verdict: DO_VERIFY ? 'none' : 'unverified' })) }
    const v = await agent(verifyPrompt(a, findings), opts('verify', { label: `verify:${a.key}`, phase: 'Verify', schema: VERIFY_SCHEMA }))
    const byId = Object.fromEntries(((v && v.results) || []).map(r => [r.id, r]))
    const verified = findings.map(f => {
      const r = byId[f.id]
      if (!r) return { ...f, verdict: 'unverified', verify_reason: 'verifier returned no verdict' }
      const base = r.final_finding ? { ...f, ...r.final_finding } : f
      return { ...base, id: f.id, area: a.key, verdict: r.verdict, verify_reason: r.reason, duplicate_of: r.duplicate_of || '' }
    })
    log(`${a.key}: ${verified.filter(x => x.verdict === 'confirmed').length}/${findings.length} confirmed`)
    return { area: a.key, explored, verified }
  },
)

const areas = perArea.filter(Boolean)
const all = areas.flatMap(r => r.verified)
const keep = f => DO_VERIFY ? f.verdict === 'confirmed' : true
const confirmed = all.filter(keep)
const rejected = all.filter(f => !keep(f))
const alreadyTracked = areas.flatMap(r => ((r.explored && r.explored.already_tracked) || []).map(t => ({ ...t, area: r.area })))

let t = { drop: [], merge: [], severity_overrides: [], title_edits: [], links: [], notes: 'triage skipped' }
if (DO_TRIAGE && confirmed.length) {
  phase('Triage')
  const compact = confirmed.map(f => ({ id: f.id, area: f.area, title: f.title, type: f.issue_type, category: f.category, severity: f.severity, platform: f.platform, repos: f.repos, actual: (f.actual || '').slice(0, 400), developer_notes: (f.developer_notes || '').slice(0, 300), related_existing: f.related_existing || [] }))
  const res = await agent(`You are the triage lead for a QA sweep. Below are ${compact.length} verified findings from ${AREAS.length} area testers. They will be filed as tickets.

Return decisions only (code applies them):
1. Duplicates across areas: findings describing the same underlying problem or the same root cause (compare developer_notes: same file/function → likely same cause; desktop and mobile symptoms of one cause → merge). Keep the clearest, absorb the rest. Distinct root causes stay separate.
2. Existing tracker: read ${EXISTING}. Drop findings an OPEN existing issue already fully covers (the reason must name the key). Related but distinct → add a link.
3. Severity calibration across the set: critical = data loss, privacy/security leak, or app unusable; major = core feature broken with no workaround; minor = partly broken/workaround/cosmetic with impact; trivial = polish. Override only where clearly miscalibrated.
4. Titles: fix vague, implementation-speak or >90-character titles; they must describe the user-visible symptom.
5. Drop non-actionable or pure-taste findings (give the reason). Don't drop things merely for being small.

Findings:
${JSON.stringify(compact, null, 1)}`, opts('triage', { label: 'triage', phase: 'Triage', schema: TRIAGE_SCHEMA }))
  if (res) t = res
}

const dropped = new Map(t.drop.map(d => [d.id, d.reason]))
const absorbedInto = new Map()
for (const m of t.merge) for (const id of m.absorb) if (id !== m.keep) absorbedInto.set(id, m.keep)
const byId = Object.fromEntries(confirmed.map(f => [f.id, f]))
const tickets = confirmed.filter(f => !dropped.has(f.id) && !absorbedInto.has(f.id)).map(f => {
  const sev = t.severity_overrides.find(s => s.id === f.id)
  const te = t.title_edits.find(s => s.id === f.id)
  const absorbed = [...absorbedInto.entries()].filter(([, k]) => k === f.id).map(([id]) => byId[id]).filter(Boolean)
  return {
    ...f,
    severity: sev ? sev.severity : f.severity,
    title: te ? te.title : f.title,
    related_existing: [...new Set([...(f.related_existing || []), ...t.links.filter(l => l.id === f.id).map(l => l.existing_key)])],
    also_observed: absorbed.map(x => ({ id: x.id, area: x.area, title: x.title, actual: x.actual, steps: x.steps, evidence: x.evidence })),
  }
})

return {
  config: { models: MODELS, efforts: EFFORTS, verify: DO_VERIFY, triage: DO_TRIAGE, idPrefix: ID, areas: AREAS.map(a => a.key) },
  stats: { reported: all.length, confirmed: confirmed.length, rejected: rejected.length, dropped_in_triage: dropped.size, absorbed: absorbedInto.size, tickets: tickets.length },
  tickets,
  rejected: rejected.map(f => ({ id: f.id, area: f.area, title: f.title, verdict: f.verdict, reason: f.verify_reason, duplicate_of: f.duplicate_of })),
  triage_dropped: [...dropped.entries()].map(([id, reason]) => ({ id, title: byId[id] && byId[id].title, reason })),
  triage_notes: t.notes,
  already_tracked: alreadyTracked,
  coverage: areas.map(r => ({ area: r.area, coverage: r.explored ? r.explored.coverage : 'explorer failed' })),
}

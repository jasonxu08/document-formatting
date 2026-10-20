# Rewriting an existing large document

Read this when the input is a long document that people cannot read (a ledger that grew over weeks, a report that records everything in the order it happened) and the job is to make it readable **without losing anything**. The steps in SKILL.md still apply; this adds what a rewrite needs. The tool is `scripts/source_set.py`.

## Workflow

1. **Read all of it, then take inventory.** Print the outline with line numbers (`python scripts/check_doc.py <source> --slugs` lists every heading with its line) and note each section's size. Do not draft before you have read to the last line: an unanswered open question may sit in the final paragraph.
2. **Classify every section** by bin (human, AI-input, archive) and by layer:
   - *current*: the verdict, decisions, risks, and the design or interface as it stands now
   - *evidence*: raw results, tables, logs, long output
   - *supporting notes*: background, release notes, setup details
   - *superseded*: what the source itself marks as history
   - *handoff*: commands, paths, ids, constraints a later agent needs

   Typical outcome: the current layer becomes the human zone; evidence, supporting notes and superseded material become archive siblings; the handoff becomes an AI-input sibling.
3. **Settle contradictions over time.** A ledger keeps stale statements ("not tested yet") beside later ones that overturn them. Put the current truth in the human zone and say that the older note predates it. Keep the stale text verbatim in the archive, labelled superseded. Never choose silently.
4. **Keep every line reachable.** Move large blocks with `source_set.py slice`; do not retype them. Group blocks by purpose into a few siblings (`<stem>.evidence.md`, `<stem>.notes.md`, `<stem>.history.md`). The tool wraps each block in `<!-- src:A-B shift:+N -->` markers and demotes its headings so the sibling's outline stays usable; `verify` promotes them back and proves each block identical to its source lines. If the original stays beside the output it is the audit trail: record its SHA-256 and do not copy it into `<stem>.data/`.
5. **Write the human zone as short, faithful restatements** that link to the block behind each claim. Facts come only from the source. Where the source gives no deadline or recommendation, say so ("The original sets no deadline"); attribute a recommendation to where it comes from; say when a ranking is your own. Mine the supporting notes (release notes, exceptions, known gaps) for caveats a reviewer must know and carry them into the human zone; they are easy to leave buried in a verbatim block. Cite by heading and quoted snippet; bare line numbers go stale, so if you use them, check them with a script.
6. **Add the section map**: for each H2 of the source, its line range, where it is summarised and where its verbatim text lives. If the user asked for a *short* map and the source has more than about a dozen sections, give a short grouped map (by layer or by period, up to about eight rows) where readers look, and put the full per-section table in the machine zone, collapsed, marked `<!-- requested-table -->` if it must stay in the human zone. Link the full map from the reading path ("Checking that nothing got lost? Go to A").
7. **Verify.** `python scripts/source_set.py verify <main.md> --source <original> --sha256 <recorded>` must end with ALL OK. Run `check_doc.py` on the main file and every sibling. Confirm the original is byte-identical. Spot-check five numbers of the panel against the source.

## source_set.py

```
python scripts/source_set.py slice SOURCE OUT.md --title "Supporting evidence" \
    --intro "What this file is and which claims it supports." \
    --block "12-58:Benchmark tables" --block "59-96:Raw logs:+2" [--zone ai-input]
python scripts/source_set.py verify MAIN.md --source SOURCE [--sha256 HEX] [--verbose]
```

- `slice` writes the zone marker, a title, your one-line intro, a contents list and one lettered block per range. A block's heading shift defaults to 1 (2 when the range contains an H1); override it with `:+N`. Headings inside code fences are never touched. Block titles are link targets, so keep them plain words.
- `verify` treats MAIN.md plus `<stem>.*.md` as the document set. It fails when a block differs from its source lines, when a non-blank source line is nowhere in the set, or when a source H2 is not named outside the verbatim copies (the section map). It prints the source checksum.

## Mistakes to avoid

- **Treating the newest entry as the whole truth.** Older text can hold the only statement of an open item, and an open question can sit in the last paragraph. If it still calls for action, it belongs in the decision block.
- **A takeaway that overstates its table.** A caption must not claim more than its table shows: no "all passed" above a table with a failed row. Re-read every caption against the table above it.
- **Summarising superseded material as if it were current.** Mention it only as context, and only in the archive.
- **Unlabelled cross-references.** "Risks 1 and 3" means nothing on a first screen where the risk rows have no numbers.
- **A status table that files an open item as closed.** Use the source's own status words, or label yours as yours, and re-read each row against the item's last statement in the source. The main open decision must never sit in a row that reads as closed or overtaken.
- **Out-of-scope findings among the decisions.** A recommendation for another team (a fix in a file this change does not touch) is worth surfacing, but as one line under the decisions ("Out of scope here: ..."), not as a decision for this document's reader.
- **Labelling a whole stack as history.** Several recent entries are usually still current. Label as superseded only what the source itself marks, or what a later entry overturns, and say which.
- **Stronger attribution than the source gives.** A recommendation must match the version of the source that says it; where the source only lists options, name the option the source gives and mark your own pick "(suggested)".
- **Retyping long blocks.** Typos and drift creep in; slice them and verify.

---
name: document-formatting
description: Use this skill whenever you are about to write a large document or report for people to read (analysis, investigation or root-cause write-up, review or audit, design or decision doc, plan, status or handoff note, test or verification report, explainer), saved as a .md file or posted in chat, and when asked to rewrite or restructure an existing long report, ledger or notes file so people can read it. It makes the output human-first. It separates what people must read from AI-input and archive material, opens with a glanceable overview (verdict, decisions, risks), orders and links sections along a reading path, and draws a relationship diagram (embedded image) when more than 5 related entities or any web of relationships appear. Load it even if the user never mentions structure, summaries or diagrams; 'write a report', 'document this', 'summarize all the findings' or 'nobody can read this report, fix it' is enough. Not for converting or styling Word, PDF or Excel files, nor for short answers.
license: MIT
compatibility: The optional scripts need Python 3.9 or newer and nothing else. Graphviz is recommended for drawing diagrams.
metadata:
  author: jasonxu08
  version: "1.0.0"
  repository: https://github.com/jasonxu08/document-formatting
---

# Document formatting: write large documents for humans first

## Why this exists

An agent that has just finished a long piece of work tends to write down everything it found, in the order it found it. The person who must act on that document then digs for the conclusion, cannot tell the three paragraphs that matter from the thirty that are logs, and has no map of how the pieces relate. More headings do not fix this. What fixes it is deciding, before writing, who each piece of content is for, then laying the document out so a person gets most of its value within a minute and knows exactly where to go for the rest.

Four ideas do the work. The sections below show how to apply them.

1. **Audience split** - human-read, AI-input and archive content are kept apart, and the human part is unmistakable.
2. **Glance first** - conclusion, verdict, decisions and risks come before anything else, in a form that lands in seconds.
3. **Guided reading** - order, links and signposts follow how people learn, so the reader always knows what to read next and why.
4. **Draw the web** - when related things form a network, show a diagram instead of describing it.

## When to apply, and how much

| Output | Treatment |
|---|---|
| Short answer (about one screen) | Lead with the answer. No zones, no panel, no diagram. |
| Medium (one to three screens) | Glance panel plus clear headings. A diagram only if the diagram rule fires. |
| Large (more than about three screens, several findings or sections, or anything saved as a report file) | Everything below. |

Three overrides:

- **Required formats win.** If a template, schema or parser dictates the structure (an ADR template, OpenSpec artifacts, another skill's report format, CSV or JSON, API docs), keep its required parts and add the human layer around them: the glance block at the top if the format allows it, otherwise in a companion summary file or in your chat reply. Never break something a tool consumes.
- **Write in the reader's language** - the language the user is writing in, labels like "At a glance" included. The English in this file is for you.
- **Existing document?** For a small edit, keep its structure and make sure its glance panel is still true afterwards; a stale summary is worse than none. A handoff or status document that agents keep updating should say, in its AI-input block, which parts of the panel to refresh when the status changes. To restructure a large existing document (a ledger that grew over weeks, a report nobody can read), follow `references/rewriting.md`: it keeps every line reachable and verifies that.

## Step 1 - Sort every piece of content by audience

Do this before drafting; the layout follows from it.

| Bin | What belongs in it | Write it like this |
|---|---|---|
| 👤 **Human-read** | Conclusions, verdicts, decisions needed, risks, the mental model, key findings and why they matter, recommendations, next steps | Meaning first. Short paragraphs, terms explained, emphasis on what matters. |
| 🤖 **AI-input** | What a later agent needs to continue or verify the work: exact paths, commands, IDs, constraints, ordered task lists, parameters, schemas, machine-readable data | Complete and unambiguous rather than pretty. Paths that stay valid for the next agent (repo-relative with the root stated once; absolute only for things outside the repo), copy-paste commands, no "this" or "it" without a referent. |
| 🗄️ **Archive** | Evidence and provenance: raw logs, full tables, query results, tool output, long inventories, dead ends, method, sources, versions, diagram source | Faithful and searchable, not narrated. |

Two tests keep the bins honest:

- *Would a person who skips this still decide correctly?* If yes, it is not human-read. Keep it, but out of their way.
- *Does a person need this to decide, yet it exists only in the archive?* Then it is in the wrong bin. Pull the point into the human zone in a sentence or two and link to the evidence.

Write each fact once, in full, where it is first needed, and reference it from elsewhere. (When you rewrite an existing document, a short restatement in the human zone plus the verbatim original in the archive is not duplication.) If the whole output is machine-oriented (a JSON file, a prompt, a generated config), do not restructure it; give it a three-line human header saying what it is, what it is for and how to use it.

## Step 2 - Find the headline before you write

You should be able to fill these in before drafting. If you cannot, the investigation is not finished; say plainly what is still unknown instead of hiding it in length.

- **Bottom line** - the conclusion in one or two sentences.
- **Judgment** - any verdict or qualitative call you reached (sound, risky, blocked, acceptable), your confidence, and what it rests on.
- **Ask** - what the reader must decide or do, who, by when, and what you recommend.
- **Risks** - what could go wrong, ranked, each with a consequence.

## Step 3 - Use the two-zone layout

Start from `assets/skeleton.md`, fill it in and delete its hint comments and placeholders (the checker flags leftovers). The shape:

1. **Title** - name the topic and, if it fits, the conclusion.
2. **👤 Human zone** - the whole upper part. It opens with the glance panel, then the reading path, then numbered body sections (1, 2, 3...).
3. **🗄️ Machine and archive zone** - last, visually quiet, with lettered blocks (A, B, C...), each collapsed in `<details>`. Each block opens with an italic line that names its bin (🤖 AI input or 🗄️ archive), says what it is and which claim it supports. Keep the block headings themselves plain words, because they are link targets. Add an AI-input block only when a later agent will continue the work or must keep the document current; leave it out otherwise. Numbers are the path people read; letters are places they look things up.

Make the split unmistakable to both audiences:

- For people: the two zone headings carry the 👤 and 🗄️ glyphs (they show up in outline and TOC panes as well) and a one-line instruction ("Start here", "Skip unless you need the raw evidence or are an agent continuing this work").
- For tools and other agents: invisible markers `<!-- zone:human -->`, `<!-- zone:ai-input -->` and `<!-- zone:archive -->` at the start of each zone or block, so a later agent can jump to what it needs.

Long material goes in a sibling file (`<name>.evidence.md`, `<name>.data.json`), reached through a one-line block in the machine zone, when AI-input and archive content together pass about 60 lines or any single block passes about 25. That is a default, not a rule: if the user asks for material to stay in the document, or wants one self-sufficient file, keep it there, collapsed, whatever its size. When the user wants an audit trail, keep byte-exact copies of the inputs in `<doc-stem>.data/` and record their checksums in the evidence file (an input that stays beside the output, such as the original in a rewrite, needs only its checksum). Start each sibling Markdown file with its zone marker (`<!-- zone:archive -->` or `<!-- zone:ai-input -->`) and run the checker on it too; it then skips the human-zone rules. Several siblings are fine when the material has distinct purposes (evidence, supporting notes, superseded history, handoff): name them `<doc-stem>.<purpose>.md`, open each with a line saying what it is and a contents list, keep block headings plain and unique (they are link targets), point to each from a block in the machine zone, and leave the blocks of an archive-only sibling open, since the file is the destination. A table or listing the user asked for by name (a map, an inventory) is allowed in full: in the human zone when readers use it to decide, otherwise in the machine zone with a link from the reading path. Put `<!-- requested-table -->` on the line above a long one so the checker lets it pass.

## The glance panel

It is the first thing in the human zone. Someone who reads only this, for under a minute, should understand at least 80% of the document. It states conclusions, not topics: "This report covers the upgrade" tells the reader nothing, while "Upgrade 6 of 9 services before the freeze and defer `auth-service`" tells them nearly everything. Use text, a picture or both, whichever gets the topic across fastest; usually that is a short bottom line plus one diagram or table.

The first screen must carry the verdict, the decision and the top risks. The picture and the reading path may continue onto a second screen; a panel that needs more than two screens is carrying detail that belongs in a body section.

Contents, in this order. Drop an item that does not apply and never invent one to fill a slot.

1. **Verdict or status** - if you reached any judgment, say so first and loudly: a glyph and a word (🟢 go, 🟡 go with conditions, 🔴 stop, ⚪ not enough evidence), then the bottom line, then confidence and what it rests on. 🟡 also fits "resolved, but the causes are still open" and a partial result (everything checked passed, one check could not be run): write "Partial result" and name the missing part.
2. **Decisions needed** - one line each: who decides what by when, and your recommendation. If the sources give no date or recommendation, say so ("no date set", "no recommendation in the source") instead of inventing one; a date or recommendation you propose is marked "(suggested)". If the cost of being wrong matters, say it once for the whole block.
3. **Top risks** - at most five, ranked, severity glyph first, each with a one-line consequence and a link to where it is handled.
4. **Key facts** - three to five numbers or facts that carry the argument; skip them when the verdict and risks already do.
5. **One picture** - if a single diagram or compact table makes the topic click (system map, before and after, timeline, option matrix), put it here. When the picture is the fastest route to understanding, it may come right after the bottom line.
6. **Read next** - the reading path (next section).

Keep every element short, because the panel is read in seconds: the title and the verdict line take one line each, the bottom line is at most two sentences (about 40 words), each decision and each risk is one line, and a table cell is a dozen words at most. Together the panel's prose stays near 300 words (tables, the picture and the Read-next list do not count). If the budget bites, cut in this order: key facts first, then the wording of each path entry (two or three words is enough), then the number of path entries (three to five steps beat a full table of contents). Never cut the verdict, the decisions or the risks. Whatever does not fit is detail. It goes in a body section, and the panel links to it.

If there is no judgment to give (an explainer, a reference page), skip the glyph and the decision block. Open with the mental model as one plain sentence, then let the picture and a short list of the 3-5 things that matter (each with the trap if it is missed) do the work. Do not invent a verdict, a decision or a risk to fill the template.

Anything that could change what the reader does belongs in the panel, above the fold. What the panel must let the reader answer depends on the document:

| Document | The reader can answer in seconds |
|---|---|
| Decision or proposal | What do you recommend, what else was considered, what do you need from me, what if we are wrong? |
| Investigation or root cause | What happened, why (cause in one sentence, with confidence), who is affected, is it fixed, what next? |
| Review, audit, assessment | Overall rating, findings by severity, top three issues, ship or not? |
| Test or verification | Pass or fail (or partial), what was and was not covered, failures grouped by cause, release impact? A coverage matrix (each requirement against how it was checked) often beats prose. |
| Status or handoff | Where things stand, what blocks us, what is next, who must do what? For a handoff also: who carries on, what may they do alone, and what must they not touch? |
| Explainer or onboarding | What is the mental model (one picture), which 3-5 concepts matter, where do I read next? |

Bad (announces a topic): "Summary: This report analyzes the proposed upgrade across nine services. It covers the inventory, the incident history and compatibility concerns, and provides recommendations."

Good (states the answer; invented example): "🟡 Go with conditions - upgrade 6 of 9 services before the freeze and defer `auth-service`. Eight of nine pass the compatibility checks, but `auth-service` has six dependents and no rollback path. Confidence: medium (staging only). Decision needed from the Eng Lead by Friday: approve the split plan."

## Guide the reading path

People understand best when they get the frame before the details, one idea at a time, with a way back. So:

- **Order by understanding, not by discovery.** A good default: glance panel, then the mental model (a diagram plus the 3-5 terms that matter), then findings by importance, then options and recommendation, then next steps and open questions. "First I looked at..." chronology belongs in the archive.
- **Give a reading path.** End the panel with a "Read next" list in reading order (bullets, with the section number inside the link text so it matches the headings). Each line holds a link, what the reader gets and roughly how long it takes. Say who may stop where ("Only deciding? Stop here. Implementing? Continue to 3, then A").
- **Make headings carry the story.** "Retries cause most timeouts" beats "Timeout analysis". Reading only the headings should give the argument. A numbered question or decision heading carries its answer or ask ("Q1 Allow XLS above 1M rows? Recommend: split"), not only its topic.
- **Signpost.** When a heading does not already say what its section answers, open the section with one line that does; close with `Next →` only when the order is not obvious. Use one name per entity throughout; never rename something between sections. Cross-references name something the reader can see (a numbered row, a heading), never an unlabelled "risk 3".
- **Show relationships explicitly.** When A depends on B or contradicts C, say it with a link: "builds on [2 The dependency map](#2-the-dependency-map)". Link each claim in the panel to the section that supports it, and each evidence block back to the claim it supports.
- **Chunk.** Groups of three to five, sections about a screen long, tables for comparisons, lists for parallel items, short paragraphs for reasoning.
- **Concepts before flows.** Introduce the vocabulary before the first section that uses it: a short glossary right after the mental model, or a definition on first use. Include codes, abbreviations and internal names the reader has to decode. A flow or procedure that leans on undefined terms sends the reader back and forth. Never assume the reader shares the context you built up during the work.
- **Keep link targets boring.** Anchors break silently. For headings you link to, use plain words and digits (no emoji or punctuation), build the anchor GitHub-style (lowercase, spaces to hyphens, punctuation dropped; underscores stay, so avoid them in these headings) and verify with the checker below. `python scripts/check_doc.py <file> --slugs` prints the anchor of every heading.

## Draw the web

**Trigger.** Related concepts or entities that form a network (many-to-many links, cycles, a hub with many spokes, layered dependencies), **or more than five related entities** even when each link is simple. If you catch yourself writing "A calls B, which calls C and D, while E also reads from B...", stop and draw it. Prose cannot show a network; readers rebuild it in their heads, and often wrongly.

**Do not draw** a linear chain of five steps or fewer (use a numbered list), a flat list of independent items (use a table), or anything where the picture would only decorate.

**How.** Read `references/diagrams.md` before drawing. In short:

1. Write the nodes and edges (source, relation, target) first. Every node and edge must come from something you verified; show inferred edges dashed and say so in the caption.
2. **Default to an embedded image** (a PNG rendered with Graphviz, or matplotlib for quantitative charts). The readers' usual viewers (VS Code preview, Azure DevOps repo and PR pages) do not reliably render Mermaid, and a diagram that shows up as code defeats its purpose. Keep the diagram source (DOT or Mermaid) beside the image so it can be edited. Use inline Mermaid only when you know the target renders it, or when no renderer is available; then say so in one line.
3. Keep each diagram legible at about 800 px wide. That is usually a dozen nodes, a few more when the layout is clean. If it cannot be made legible, split it into an overview (groups, or the main flow) plus zoomed views, make sure every entity appears in at least one of them, and say in the caption what the overview leaves out.
4. Give it one focal point (the hub, the broken link, the changed part), a legend if colours carry meaning, a verb on the edges, and a caption: what it shows, how to read it, the one takeaway. When every edge means the same thing (a pure dependency graph), say so once in the legend or caption and label only the exceptions; twelve identical labels are noise.
5. If you can view images, look at the rendered file and fix overlaps, unreadable labels and empty boxes where non-Latin text (Chinese, for example) lacks a font, before embedding. It must stay legible at about 800 px wide.
6. Put the diagram where its entities are first introduced, and in the glance panel when it is the quickest route to understanding the topic.

## Highlight with a budget

If everything shouts, nothing does. Spend loud formatting only on what changes the reader's action:

- **Verdict** - a blockquote whose first line is a heading-sized status line. One overall verdict per document.
- **Decisions needed** - a blockquote headed with 🧭, one line per decision.
- **Risks** - a table with the severity glyph in the first column so the eye can scan it (🔴 blocker, 🟠 high, 🟡 medium, 🟢 low).
- **Zone headings** - the 👤 one is loud (the 👤 glyph, plus capitalised "START HERE" in languages that have case); the 🗄️ one is deliberately quiet (sentence case, content collapsed), because people should be able to walk past it.
- Bold three to five facts in running text. Labels such as "Bottom line:" and list lead-ins are structure and do not count against that; whole paragraphs are never bold.

Use plain blockquotes rather than `> [!NOTE]`-style alerts: GitHub renders those, but many previews and Azure DevOps show the raw tag. Do not use HTML colours or styles; they are stripped. Everything must still read well as plain text.

## Deliver

- **File first.** Save the document where the repo's conventions say docs live; otherwise next to the work or where the user named. Put images in `<doc-stem>.assets/` beside it and link them relatively, with forward slashes and no spaces in file names. Name every sibling after the document (`<doc-stem>.evidence.md`) and keep all references relative, so the set can be moved or renamed together.
- **No machine-local paths.** Your home directory, temp or session folders mean nothing to the next reader and can leak a username; use paths relative to the document or the repo. The checker flags them.
- **The chat reply is the glance panel in miniature** (unless the caller asks for something else): verdict, decisions needed, the top two or three risks, the file path (folder plus file name), and where to start reading. Do not paste the document into chat. The reader should be able to decide in thirty seconds and open the file only for more.
- **Chat-only output** that is long gets the same structure. Keep archive material out of the reply (offer to save it), and use a table or indented list instead of a diagram if the client cannot render images.

## Before you deliver

Review the document against `references/review-rubric.md`, the standard every large document is held to:

1. Run `python scripts/check_doc.py <report.md>` on the main file and on each sibling file (path relative to this skill's directory). It covers every automatic rule and prints each finding with a rule id and a tier: Blocker, Major or Minor. If you rewrote an existing document, also run `python scripts/source_set.py verify <report.md> --source <original>` (see `references/rewriting.md`).
2. Walk the Blocker and Major judgment rules in the rubric that apply to this document type.
3. Deliver when no Blocker is left and at most two Majors remain; name those Majors, with the reason, in your reply.

The rubric works equally well for reviewing a document someone else wrote: score it the same way and report the verdict and the failing rules.

If you do nothing else, ask these seven questions:

1. **Thirty-second test** - cover everything below the glance panel. Can a stranger state the conclusion, what is asked of them and the biggest risk?
2. **Skim test** - do the headings alone tell the story?
3. **Zone test** - nothing in the human zone that only a machine needs (raw logs, long listings, full JSON); nothing a person needs that lives only in the machine zone.
4. **Diagram test** - more than five related entities, or a web? Then a diagram exists, with a caption, legible at about 800 px wide.
5. **Honesty test** - judgments carry confidence, verified facts are told apart from inferences, and unknowns are listed rather than hidden.
6. **Link test** - the checker reports no Blocker: every link, anchor and image resolves.
7. **Duplication test** - each fact appears in full once.

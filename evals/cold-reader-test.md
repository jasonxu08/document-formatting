# Cold-reader test

Measures the skill's headline promise: a reader who sees only the top of a document gets at least 80% of what matters. Use it as a regression test when you change the skill, not on every document.

## Protocol

1. **Ground truth.** Before looking at any output, list 6 to 8 key facts a decision-maker must take away from the source material. One line each. They come from the sources, not from the document under test, so every configuration is scored against the same list (`cold_reader_facts.json`).
2. **Prepare the cold read.** Copy the first 60 lines of the document, plus the images those lines reference, into a clean folder (`prepare_cold_reader.py`). That is what a reader sees on the first screen or two.
3. **Read.** A fresh agent that has not seen the sources or the rest of the document reads only that folder and answers the six fixed questions below, in a few lines each.
4. **Score.** A key fact is recovered when the answers state it substantially: the right names, and numbers in the right range. Recall is recovered facts divided by total facts. Pass is recall of 0.8 or more.

## The six questions

1. In two sentences: what is this document about, and what is its main conclusion or message?
2. What decision or action is requested, from whom, and by when? (Write "none" if none.)
3. What are the most important risks or problems it names, in order of importance?
4. What are the key things, components or steps it describes, and how do they relate to each other?
5. Which numbers or dates does it put in front of you as the ones that matter?
6. Which section would you read next, and what do you expect to find there?

## Scoring notes

- Count each fact once. A multi-part fact counts when its core is stated.
- Do not credit anything the reader could only know from outside the folder.
- Report the recall and the missed facts. The misses show what the panel failed to say, which is the input for the next edit of the skill.

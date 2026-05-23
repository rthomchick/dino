Add goal field to journal schema, update layout, migrate existing entries

Task 1: Extend the content schema
In src/content.config.ts, add goal as an optional string field to the journal collection schema:
typescriptgoal: z.string().optional(),  // One-sentence goal statement for the entry
Add it after the summary field.

Task 2: Update the journal entry layout
In the journal entry layout file, render the goal field as an italic subtitle between the title and the ContentActions toolbar.
Find the title/tags block. After the title <h1> and before the tags div, add:
astro{goal && (
  <p class="text-base italic text-stone-500 dark:text-stone-400 leading-relaxed mb-5 max-w-2xl">
    Goal: {goal}
  </p>
)}
The goal variable should come from the entry's frontmatter data, pulled the same way title, tags, and other frontmatter fields are accessed in the layout.
Also: find and remove the <hr> that currently appears between the goal statement (first italic paragraph in prose) and the body content. This is typically rendered from a markdown --- that sits after the goal line in the entry body. Since the goal is now in the layout, this divider is no longer needed. The toolbar's borders provide the visual separation.
Do NOT remove <hr> elements that appear elsewhere in the body (e.g., the closing divider before "Week N complete"). Only remove the one that immediately follows the goal statement at the top of the prose.

Task 3: Migrate all 12 existing journal entries
For each .md file in src/content/journal/:

Open the file
Find the goal statement in the body. It will be the first paragraph, formatted as either:

*Goal: ...* (italic markdown)
_Goal: ..._ (alternate italic markdown)
The text always starts with "Goal:"


Extract the goal text (everything after "Goal: ", without the italic markers)
Add goal: "extracted text" to the frontmatter. Escape any quotes in the text.
Remove the goal line from the body content
Remove the --- (horizontal rule) that immediately follows the goal line, if present. Do NOT remove other horizontal rules in the body.
Save the file

Verify after migration: Run npx astro build and confirm zero errors. Spot-check 3 entries in the browser to confirm the goal renders as the italic subtitle, not as inline prose.

Validation steps:

npm run dev — open Week 10 journal entry
Confirm: goal appears as italic subtitle below title, above toolbar
Confirm: goal is NOT repeated inside the prose body
Confirm: no orphaned <hr> between toolbar and first body heading
Open Week 1 and Week 13 — confirm same behavior
Run npx astro build — zero errors across all 12 entries
Check that entries without a goal statement (if any exist) render normally without the subtitle

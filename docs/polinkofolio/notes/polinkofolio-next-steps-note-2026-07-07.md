# Polinkofolio Next Steps Note (2026-07-07)

This is a working note, not a Polinko curated transcript.

## Source Excerpt

```text
user: second q:
i really want polinkofolio to have its own directory with its own docs
right now it's too messy all granglified in the root

should it live in its own repo? with a poleab working on it?
i think the best move is we have you work in a polinkofolio repo while you delegate. what do you think?

assistant: Yes, I think `polinkofolio` should live in its own repo.

The clean split is:

- `polinko`: source of truth, research system, evals, transcripts, raw/local evidence, canonical method.
- `polinkofolio`: public notebook/product surface, with its own docs, content model, templates, site code, and publishing workflow.

Right now the Polinko root has `apps/polinkofolio`, `docs/polinkofolio`, `.local/polinkofolio-mockups`, and the separate local `polinkofolio` repo. That is exactly why it feels granglified: the public surface is half inside the research repo and half born as its own thing.

I like your proposed shape: I work primarily in the local `polinkofolio` repo, and delegate narrow sidecar kernels. But the sidecars should not own the product direction. They should produce reviewable packets.

My recommendation:

1. Finish/park the current `polinko` validation branch first.
2. Move active Polinkofolio work into the local `polinkofolio` repo.
3. Keep Polinko-side material as source/export/reference only.
4. Use “poleab” as a bounded worker for specific slices:
   - source inventory packet from Polinko
   - proposed content/docs hierarchy
   - first artifact template
   - first entry candidate
5. Main thread reviews everything: scope, source truth, style, provenance, and whether it belongs in `polinkofolio` or back in `polinko`.

So: yes to its own repo, yes to poleab, but poleab is a worker/research assistant. You and I keep the control surface. The first real kernel should be a read-only repo-shape audit across both repos, then we decide what migrates, what stays, and what gets deleted/parked.

user: oh the sidecars are botbits haha
you're poleab, the head honcho

assistant: Got it. I’m poleab, and the sidecars are botbits.

So the structure becomes:

- **poleab**: main/control kernel, repo steward, reviewer, prompt-shaper, final decision support.
- **botbits**: narrow worker kernels for bounded packets.
- **you**: source of direction, taste, acceptance, and go/no-go.

For `polinkofolio`, that makes the split even cleaner: poleab works in the dedicated `polinkofolio` repo, botbits do limited inventory/build/review packets, and nothing from a botbit lands without poleab inspection plus your approval.

user: or actually, i create a poleab into a foleab

so it's a beab within polinko, that works in the polinkofolio repo

assistant: Yes, that’s the right naming model.

`foleab` is a specialized poleab: a beab within the Polinko system whose active worktree/repo is `polinkofolio`.

So:

- **poleab**: current head/control beab for Polinko-side repo stewardship.
- **foleab**: Polinkofolio-focused beab, operating in the local `polinkofolio` repo.
- **botbits**: bounded worker kernels that foleab or poleab can dispatch for small packets.
- **Polinko**: canonical research/source system.
- **Polinkofolio**: derived public notebook/product repo.

That framing is useful because it preserves source hierarchy: foleab can build public artifacts, but it does not mutate Polinko source truth unless poleab/you explicitly route that change back.

user: ok cool!

ok first we finalise the polinkofolio content
because i don't want these other things be procrastination masked as productivity.

how about we just take this transcript verbatim but not as a polinko transcript, just as a note so we can remember the details of our next steps

like literally a copy/paste lol in the folder it belongs to
```

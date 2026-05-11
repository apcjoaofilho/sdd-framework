# references/borrowed/

Engineering-technique documents **forked** from external skill libraries, primarily [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills) (MIT).

## Why fork instead of link

Linking to an upstream file means our docs break the day upstream renames, restructures, or deletes it. Forking gives us a stable copy we control. The cost is maintenance drift — which we cap with the rules below.

## Policy

1. **Attribution header.** Every file in this directory starts with:

   ```
   <!-- Adapted from addyosmani/agent-skills @ <commit-sha> (path: skills/<name>/SKILL.md), MIT License.
        Trimmed and re-pointed at the SDD pipeline. Upstream: https://github.com/addyosmani/agent-skills -->
   ```

   Replace `<commit-sha>` with the exact commit the content was taken from. If the source is not `agent-skills`, adjust the repo and license accordingly (only permissive licenses — MIT, Apache-2.0, BSD, CC-BY — are eligible).

2. **Back-link to a phase.** Each file states which pipeline phase it serves and links to the matching `references/phase-*.md`. Files that don't map to a phase don't belong here.

3. **Trim, don't bloat.** Keep only what's relevant to the SDD pipeline. Drop tool-specific or agent-specific sections that don't generalize.

4. **Hard cap: ≤ 8 files.** Past that we're an unmaintained mirror, not a framework. If a 9th candidate appears, replace a weaker one or reconsider.

5. **No silent divergence.** If we modify borrowed content beyond trimming (add our own guidance, change recommendations), mark the change inline with `<!-- SDD: ... -->` so a future reader can tell ours from theirs.

6. **Refresh on demand, not on schedule.** We don't track upstream automatically. If a borrowed file is stale and it matters, open an issue and re-fork from a newer commit, updating the attribution header.

## Current borrowed files

_None yet — populated under roadmap item **S9** (see [PLAN.md §5.2](../../PLAN.md#52-should-have--strongly-preferred-for-v200))._

Candidate set (subject to change during S9):

| Source skill | Serves phase | Why |
|--------------|--------------|-----|
| `context-engineering` | all (cross-cutting) | The single biggest agent failure mode is bad context. Worth being foundational. |
| `planning-and-task-breakdown` | PLAN | Vertical slicing + task sizing (XS/S/M/L/XL) complements our PLAN gate. |
| `incremental-implementation` | EXECUTE | Scope discipline, simplicity rules, feature-flag guidance. |
| `debugging-and-error-recovery` | VERIFY | Triage checklist for when the VERIFY gate fails. |
| `code-review-and-quality` | REVIEW | Review checklist beyond what our gate enumerates. |
| `shipping-and-launch` | RELEASE | Pre-launch checklist. |

## License note

`agent-skills` is MIT. The MIT license text must be reproduced — see the root [`LICENSE`](../../LICENSE) of this repo for our license; upstream license terms are satisfied by the attribution header in each borrowed file plus this note. If we ever borrow from a repo under a different permissive license, add that license's required notice here.

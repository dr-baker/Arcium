# Arcium

## What we're after

Build Arcium as the shared browser product. This repository owns Chromium
patches, browser resources, and features that can work on more than one
platform. Platform repositories pin an exact Arcium commit and add their build,
package, and operating-system integration.

AI-assisted development is welcome. The author remains responsible for every
change, regardless of which tools helped create it.

## Where to go

- `patches/` - ordered Chromium changes.
- `resources/` - Arcium-owned browser resources.
- `devutils/` - patch and source validation tools.
- `CONTRIBUTING.md` - contribution and review requirements.

## Ground rules

- Put shared browser behavior in this repository. Put platform-only work in the
  applicable platform repository.
- Keep changes reviewable. Understand and inspect all generated or AI-assisted
  output before submission.
- Test the affected behavior and state the completed proof gates accurately.
- Disclose uncertainty, missing tests, and tool-generated work that needs extra
  review.
- Do not send duplicate, automated, or unreviewed contributions.
- Never push to an upstream repository unless Daniel asks.

## Vocabulary

- **Arcium** - the shared browser product and core repository.
- **Platform repository** - a build, package, and platform-integration repository
  that pins Arcium.
- **Patch series** - ordered Quilt patches applied to Chromium source.
- **Proof gate** - one verified stage, such as patch replay, compilation, launch,
  or visible behavior.

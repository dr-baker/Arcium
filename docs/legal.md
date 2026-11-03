# Arcium legal documents

The browser bundles its privacy policy and terms at `chrome://setup/privacy.html`
and `chrome://setup/terms.html`. They live in the onboarding component's public
directory, added by `patches/personal/arcium-legal.patch`. Edit them through Quilt.
Both onboarding and macOS Settings link to these copies.

Daniel operates Arcium. The support and privacy address is
`danielappsupport@gmail.com`.

## Reused text

The warranty and liability clauses are shortened adaptations of sections O and P
of [GitHub's Terms of Service](https://docs.github.com/en/site-policy/github-terms/github-terms-of-service).
The third-party policy, support-retention and access/correction/deletion wording
is adapted from [GitHub's General Privacy Statement](https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement).
GitHub publishes its [site policies under CC0-1.0](https://github.com/github/site-policy).
The adaptations remove account, hosting, payment and corporate provisions that
do not apply to this browser. Arcium's data handling and operator details are
specific to this project. Neither document copies Helium's legal text.

## Facts to preserve

- Browser profile data stays on the device rather than being sent to Daniel.
- Optional Helium services have a separate operator. Link to their current
  [privacy policy](https://helium.computer/privacy) and
  [terms](https://helium.computer/terms), without promising their retention
  periods or infrastructure on Daniel's behalf.
- Crash reporting has its own preference. It defaults to asking after a crash.
  Sending one report or enabling automatic reporting permits uploads to Helium.
  Reports can include sensitive process memory. The controlling patches are
  `helium/core/crash-reporting-prefs.patch` and
  `helium/core/crash-reporter-privacy-tweaks.patch`.
- This preview has browser self-updates disabled. Revisit the policy when
  enabling an Arcium update service or adding any data collection.
- These product documents do not replace GPL/BSD licenses, credits, copyright
  notices, or corresponding-source distribution obligations.

Keep the HTML pages self-contained. They must load without network access.
When practices change, update the text and revision date with the release.

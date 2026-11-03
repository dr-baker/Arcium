# Legal document verification

Source: `patches/personal/arcium-legal.patch`, refreshed for Chromium
156.0.8078.47 at `44cd96bf`.
The screenshots show its Vite-built HTML documents in isolated headless
Chromium, with HTTP and HTTPS requests blocked. They are not screenshots of
an installed Arcium build. No personal browser profile was used.

- Desktop: 960px, light appearance, full page.
- Mobile: 390px, dark appearance, full page.
- Both document headings and Daniel's contact address matched.
- Privacy/terms navigation worked in both directions.
- Keyboard focus remained visible; neither width had horizontal overflow.
- Loading the documents made no HTTP/HTTPS requests and produced no script or
  console errors.

Component checks on isolated copies of the changed Chromium 156 source:

- Vite production build and GRIT resource-map generation passed. Both legal
  pages were copied byte for byte; the map contained 36 entries within its
  allocation of 48.
- `node --test tests/*.test.mjs`: 124 passed.
- `svelte-check --tsconfig ./tsconfig.app.json`: no errors or warnings.
- The macOS SettingsUI package built and passed all 112 existing Swift tests.
- Both new patches passed focused zero-fuzz checks against the Chromium 156
  source files. Crash strings were reconstructed from their pre-namesub Quilt
  backups. The active build source was not changed.

GPT-6-Astra approved the source changes without material findings. Full Arcium
compilation, packaging, live `chrome://setup/` navigation and native Settings
interaction were not performed. The complete current Chromium 156 patch series
was not replayed. No installed browser was replaced.

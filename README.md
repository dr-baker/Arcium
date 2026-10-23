<div align="center">
    <img src="https://raw.githubusercontent.com/dr-baker/Arcium-macOS/main/resources/assets/legacy_crop.png"
        title="Arcium" alt="Arcium logo" width="120" />
    <h1>Arcium</h1>
    <p>
        Helium's privacy and speed, with Arc-inspired polish.
    </p>
</div>

[Download for macOS](https://github.com/dr-baker/Arcium-macOS/releases) · [Quickstart](https://github.com/dr-baker/Arcium-macOS#start-browsing) · [Import from Arc](https://github.com/dr-baker/Arcium-macOS/blob/main/docs/import-from-arc.md) · [Roadmap](https://github.com/dr-baker/Arcium-macOS#whats-next)

![Arcium with Spaces, Favorites, and a pastel sidebar](https://raw.githubusercontent.com/dr-baker/Arcium-macOS/main/docs/assets/arcium-layout.png)

The macOS preview runs without building from source. See its [release notes](https://github.com/dr-baker/Arcium-macOS/blob/main/docs/preview-release.md) for requirements and limits.

## Repository structure

This repository is the shared Arcium browser product. It owns Chromium patches,
browser resources, and features that can work on more than one platform.

Platform repositories pin an exact Arcium commit and add their build, packaging,
and operating-system integration:

- [Arcium for macOS](https://github.com/dr-baker/Arcium-macOS)

## Development
macOS is the primary development platform and the recommended environment for
contributions.

Linux packaging includes a similar development script, so the same guide
can be applied there too.

[See the Arcium-macOS development guide](https://github.com/dr-baker/Arcium-macOS/blob/main/docs/building.md#development-build-and-environment).

## Contributing
Before contributing to Arcium, read the guidelines in
[CONTRIBUTING.md](CONTRIBUTING.md).

## Credits

### The Chromium project
[The Chromium Project](https://www.chromium.org/) is at the core of Arcium,
making it possible in the first place.

### ungoogled-chromium
Arcium descends from [Helium](https://github.com/imputnet/helium), which is based
on [ungoogled-chromium](https://github.com/ungoogled-software/ungoogled-chromium).

### Other Chromium browsers

Arcium inherits patches from Helium and other open source Chromium browsers:

- [Inox patchset](https://github.com/gcarq/inox-patchset)
- [Debian](https://tracker.debian.org/pkg/chromium-browser)
- [Bromite](https://github.com/bromite/bromite)
- [Iridium Browser](https://iridiumbrowser.de/)
- [Brave](https://github.com/brave/brave-core)

All patches are sorted by vendor in the [patches](patches/) directory of this repo.

## License
All code, patches, modified portions of imported code or patches, and
any other content that is unique to this repository and not imported from other
repositories is licensed under GPL-3.0. See [LICENSE](LICENSE).

Any content imported from other projects retains its original license (for
example, any original unmodified code imported from ungoogled-chromium remains
licensed under their [BSD 3-Clause license](LICENSE.ungoogled_chromium)).

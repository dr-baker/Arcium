#!/usr/bin/env python3
"""Generate typed command-bar design values; the browser never reads this JSON."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
HEADER = 'chrome/browser/ui/omnibox/arcium_command_design.h'


def schema():
    value = json.loads((ROOT / 'devutils/ui/command_bar_design.json').read_text())
    assert value['version'] == 1
    seen = set()
    for token in value['tokens']:
        key = token['key']
        assert re.fullmatch('[a-z][a-z0-9_]*', key) and key not in seen
        seen.add(key)
        assert token['type'] in ('int', 'double', 'color')
        if token['type'] == 'color':
            assert token['default'] == '' or re.fullmatch('#[0-9a-fA-F]{6}', token['default'])
        else:
            assert token['min'] <= token['default'] <= token['max'] and token['step'] > 0
            if token['type'] == 'int':
                assert all(type(token[k]) is int for k in ('min', 'default', 'max', 'step'))
    return value


def cpp(value):
    tokens = value['tokens']
    text = '''// Generated from devutils/ui/command_bar_design.json. Do not edit.
#ifndef CHROME_BROWSER_UI_OMNIBOX_ARCIUM_COMMAND_DESIGN_H_
#define CHROME_BROWSER_UI_OMNIBOX_ARCIUM_COMMAND_DESIGN_H_

#include <algorithm>
#include <cmath>
#include <optional>
#include <string_view>

#include "base/strings/string_number_conversions.h"
#include "base/strings/string_util.h"
#include "base/values.h"
#include "third_party/skia/include/core/SkColor.h"

namespace arcium {
// Cached per panel. Parsing occurs only on preference changes, never in paint,
// layout, typing or animation callbacks. Missing fields retain compiled defaults.
struct CommandPanelDesign {
'''
    for t in tokens:
        kind = 'std::optional<SkColor>' if t['type'] == 'color' else t['type']
        initial = ('std::nullopt' if not t['default'] else f'SkColorSetA(0x{t["default"][1:]}, 255)') if t['type'] == 'color' else str(t['default'])
        text += f'  {kind} {t["key"]} = {initial};\n'
    text += '''  friend bool operator==(const CommandPanelDesign&,
                         const CommandPanelDesign&) = default;
};
'''
    text += f'inline constexpr unsigned kCommandDesignTokenCount = {len(tokens)};\n'
    text += '''

inline std::optional<CommandPanelDesign> ParseCommandPanelDesign(
    const base::DictValue& values) {
  CommandPanelDesign result;
  for (const auto [key, value] : values) {
'''
    for t in tokens:
        key = t['key']
        text += f'    if (key == "{key}") {{\n'
        if t['type'] == 'color':
            text += f'''      const auto* color = value.GetIfString();
      if (!color) return std::nullopt;
      if (color->empty()) {{ result.{key} = std::nullopt; continue; }}
      unsigned rgb;
      if (color->size() != 7 || (*color)[0] != '#' ||
          !std::all_of(color->begin() + 1, color->end(), [](char c) {{ return base::IsHexDigit(c); }}) ||
          !base::HexStringToUInt(std::string_view(*color).substr(1), &rgb))
        return std::nullopt;
      result.{key} = SkColorSetA(rgb, 255);
'''
        else:
            text += f'''      if (!value.is_int() && !value.is_double()) return std::nullopt;
      const double number = value.GetDouble();
      if (!std::isfinite(number) || number < {t['min']} || number > {t['max']}'''
            if t['type'] == 'int': text += ' ||\n          std::trunc(number) != number'
            text += ') return std::nullopt;\n'
            text += f'      result.{key} = static_cast<{t["type"]}>(number);\n'
        text += '      continue;\n    }\n'
    text += '''    return std::nullopt;  // Reject misspellings and unsupported versions.
  }
  return result;
}
}  // namespace arcium
#endif  // CHROME_BROWSER_UI_OMNIBOX_ARCIUM_COMMAND_DESIGN_H_
'''
    return text


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    data = cpp(schema())
    if args.check:
        if args.output.read_text() != data: parser.error('Generated command design header is stale')
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)

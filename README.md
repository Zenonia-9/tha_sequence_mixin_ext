# THA Sequence Mixin Extension

![Odoo 19](https://img.shields.io/badge/Odoo-19.0-875A7B?style=flat-square)
![License](https://img.shields.io/badge/License-LGPL--3-blue?style=flat-square)
![Category](https://img.shields.io/badge/Category-Accounting-4ECDC4?style=flat-square)

Add daily reset support to Odoo 19 accounting sequence detection without patching core files.

This module extends Odoo's native sequence logic so `account.move` can recognize and work with **daily reset numbering** such as `BILL/2026/05/02/0001`. It is designed as a narrow, upgrade-friendly extension: native yearly, monthly, and financial-year behaviors stay intact, while a new `day` reset mode becomes available when the sequence format explicitly includes a day component.

## Highlights

- Detects **daily reset** sequence patterns like `PREFIX/YYYY/MM/DD/0001`.
- Preserves standard Odoo sequence behaviors for:
  - yearly reset
  - monthly reset
  - year-range reset
  - year-range-month reset
  - fixed numbering
- Extends `account.move` warnings so daily formats are explained correctly to users.
- Extends the **Resequence Wizard** preview and recomputation flow for daily periods.
- Respects `sequence_override_regex` on journals.
- Keeps all changes addon-local with no Odoo core edits.

## Example

Once a journal is intentionally using a daily sequence pattern, Odoo can continue with values such as:

```text
INV/2026/05/02/0001
INV/2026/05/02/0002
INV/2026/05/03/0001
```

## Technical Notes

- `models/sequence_mixin.py`
  Introduces the custom daily regex, reset deduction, date-range handling, and next-sequence formatting support.
- `models/account_move.py`
  Extends the onchange warning logic so daily sequence structures are recognized and described correctly.
- `models/account_resequence.py`
  Enhances preview and recomputation logic in `account.resequence.wizard` for exact per-day periods.

## Module Layout

```text
tha_sequence_mixin_ext/
|-- models/
|-- README.md
`-- __manifest__.py
```

## Dependencies

- `account`

## Installation

1. Place the module in your custom addons path.
2. Update the Apps list in Odoo.
3. Install **THA Sequence Mixin Extension**.

## Operational Notes

- Daily behavior activates only when the sequence format itself contains a day component.
- This module does not silently convert existing journals from monthly or yearly numbering.
- Test sequence behavior in a staging database before using it in production accounting flows.

## License

This module is licensed under `LGPL-3`.

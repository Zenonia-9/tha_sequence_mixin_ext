# THA Sequence Mixin Extension

## Overview

`tha_sequence_mixin_ext` extends Odoo 19 native accounting sequence
behavior to support **daily reset numbering** for `account.move`
entries.

Example supported format:

    BILL/2026/05/02/0001
    INV/2026/04/29/001
    MISC/2026/05/02/0001

By default, Odoo supports yearly, monthly, year-range, year-range-month,
and fixed sequences.\
This module adds **day-level reset detection and handling** while
preserving full backward compatibility.

------------------------------------------------------------------------

## Features

### Daily Reset Support

When the latest posted move number is manually changed to:

    INV/2026/05/02/0001

Odoo will automatically detect:

    Reset type: day

And generate:

    INV/2026/05/02/0001
    INV/2026/05/02/0002
    INV/2026/05/03/0001

### Works Across Accounting Move Types

Supports: - Vendor Bills - Customer Invoices - Journal Entries - Other
accounting journals using `account.move`

### Resequence Wizard Compatible

Extends `account.resequence.wizard` to:

-   Accept daily format in **First New Sequence**
-   Preview correct daily sequence values
-   Restart sequence per accounting date
-   Preserve ordering modes:
    -   Keep current order
    -   Reorder by accounting date

### Company and Journal Safe

-   Daily reset is not global.
-   Only applies to journals where daily format is manually configured.
-   Changing one company or journal does not affect others.
-   Fully respects `sequence_override_regex`.

### Backward Compatible

Native behaviors remain unchanged:

-   Yearly reset
-   Monthly reset
-   Financial year range reset
-   Year-range-month reset
-   Fixed (never reset)

If a journal continues using monthly or yearly format, behavior is
identical to standard Odoo.

------------------------------------------------------------------------

## Technical Design

This module extends:

-   `sequence.mixin`
-   `account.move`
-   `account.resequence.wizard`

Key enhancements:

-   Adds daily regex detection
-   Implements daily `_get_sequence_date_range`
-   Extends `_sequence_matches_date`
-   Enhances onchange format warning
-   Updates resequence grouping logic to handle day periods

No Odoo core files are modified.

------------------------------------------------------------------------

## How It Works

Daily reset activates only when the sequence pattern includes:

    YYYY/MM/DD

Example:

    INV/2026/05/02/0001

If the pattern does not include a day component, Odoo behaves normally.

------------------------------------------------------------------------

## Installation

Place the module inside your custom addons path and update apps list.

Dependencies: - account

Compatible with: - Odoo 19

------------------------------------------------------------------------

## Usage

1.  Post an invoice normally.

2.  Reset it to draft.

3.  Change the number to include day:

        INV/2026/05/02/0001

4.  Post again.

Odoo will now restart numbering per day.

------------------------------------------------------------------------

## Production Notes

-   Designed to be accounting-safe.
-   Does not bypass locking or sequence uniqueness protections.
-   Does not alter existing historical records.
-   Daily reset must be intentionally configured by adjusting sequence
    format.
-   Recommended to test in staging database before deploying to
    production.

------------------------------------------------------------------------

## Limitations

-   Does not automatically convert monthly sequences to daily.
-   Requires manual format adjustment to activate daily behavior.

------------------------------------------------------------------------

## Author

Thein Htoo Aung

------------------------------------------------------------------------

## License

LGPL-3

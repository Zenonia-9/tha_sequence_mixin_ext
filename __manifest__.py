# -*- coding: utf-8 -*-
{
    "name": "Sequence Mixin Extension",
    "summary": "Prototype daily reset support for account.move sequence detection.",
    "description": """
        Sequence Mixin Extension
        ============================
        
        Extends Odoo's sequence.mixin to support daily reset periods for accounting sequences.
        
        Key Features:
        -------------
        * Detects daily sequence patterns (e.g., BILL/2026/05/02/0001)
        * Validates year, month, and day components against accounting dates
        * Supports resequencing wizard for daily periods
        * Preserves native year/month/fixed reset behavior
        * Respects journal-specific sequence_override_regex settings
        
        Technical Details:
        ------------------
        * Extends sequence.mixin with daily regex pattern detection
        * Overrides account.move onchange warnings for daily formats
        * Enhances account.resequence.wizard for daily period grouping
        * Maintains compatibility with existing accounting sequence logic
    """,
    "version": "19.0.1.0.0",
    "category": "Accounting",
    "author": "Thein Htoo Aung",
    "maintainer": "Thein Htoo Aung",
    "license": "LGPL-3",
    "depends": ["account"],
    "data": [],
    "installable": True,
    "application": False,
    "auto_install": False,
}

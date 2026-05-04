# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models


class SequenceMixin(models.AbstractModel):
    _inherit = "sequence.mixin"

    # Prototype note:
    # Odoo's native account sequences already infer the reset period from the
    # latest posted name. This module keeps that mechanism and only teaches the
    # parser one additional period: day.
    #
    # Accounting sequence risk:
    # Do not use this extension to silently rewrite existing numbering policies.
    # A journal should enter daily mode only after an accountant deliberately
    # posts a daily-shaped sequence such as BILL/2026/05/02/0001.
    _sequence_daily_regex = (
        r"^(?P<prefix1>[^/]+/)"
        r"(?P<year>(?:19|20|21)\d{2})"
        r"(?P<prefix2>/)"
        r"(?P<month>0[1-9]|1[0-2])"
        r"(?P<prefix3>/)"
        r"(?P<day>0[1-9]|[12]\d|3[01])"
        r"(?P<prefix4>/)"
        r"(?P<seq>\d+)"
        r"(?P<suffix>\D*?)$"
    )

    @api.model
    def _deduce_sequence_number_reset(self, name):
        """Detect daily reset before falling back to native reset detection."""
        # Daily reset is intentionally strict: only PREFIX/YYYY/MM/DD/SEQ with
        # a 4-digit calendar year should return "day". Financial-year names
        # such as JV-FA/10-11/02/0001 must fall through to Odoo's native
        # year_range_month/year_range detection.
        match = re.match(self._sequence_daily_regex, name or "")
        if not match:
            return super()._deduce_sequence_number_reset(name)

        groupdict = match.groupdict()
        if all(groupdict.get(req) is not None for req in ("seq", "year", "month", "day")):
            return "day"
        return super()._deduce_sequence_number_reset(name)

    def _get_sequence_format_param(self, previous):
        """Return a format string that preserves daily sequence components."""
        if self._deduce_sequence_number_reset(previous) != "day":
            return super()._get_sequence_format_param(previous)

        # This mirrors the native parser, with only the extra `day` placeholder
        # added. Keeping the same format/value contract lets the standard
        # sequence increment and locking code remain in charge.
        match = re.match(self._sequence_daily_regex, previous or "")
        if not match:
            return super()._get_sequence_format_param(previous)

        format_values = match.groupdict()
        format_values["seq_length"] = len(format_values["seq"])
        format_values["year_length"] = len(format_values.get("year") or "")
        format_values["year_end_length"] = len(format_values.get("year_end") or "")

        if not format_values.get("seq") and "prefix1" in format_values and "suffix" in format_values:
            # Same native edge case: an empty sequence number means the suffix is
            # actually part of the prefix before incrementing starts.
            format_values["prefix1"] = format_values["suffix"]
            format_values["suffix"] = ""

        for field in ("seq", "year", "month", "day", "year_end"):
            format_values[field] = int(format_values.get(field) or 0)

        placeholders = re.findall(
            r"\b(prefix\d|seq|suffix\d?|year_end|year|month|day)\b",
            self._sequence_daily_regex,
        )
        format_string = "".join(
            "{seq:0{seq_length}d}" if placeholder == "seq" else
            "{month:02d}" if placeholder == "month" else
            "{day:02d}" if placeholder == "day" else
            "{year:0{year_length}d}" if placeholder == "year" else
            "{year_end:0{year_end_length}d}" if placeholder == "year_end" else
            "{%s}" % placeholder
            for placeholder in placeholders
        )
        return format_string, format_values

    def _get_sequence_date_range(self, reset):
        """Constrain daily sequences to the exact accounting date."""
        if reset != "day":
            return super()._get_sequence_date_range(reset)

        ref_date = fields.Date.to_date(self[self._sequence_date_field])
        return ref_date, ref_date, None, None

    def _sequence_matches_date(self):
        """Validate the day component in addition to native year/month checks."""
        self.ensure_one()
        sequence_date = fields.Date.to_date(self[self._sequence_date_field])
        sequence = self[self._sequence_field]

        if not sequence or not sequence_date:
            return True

        if self._deduce_sequence_number_reset(sequence) != "day":
            return super()._sequence_matches_date()

        # Daily accounting numbers are date-bearing legal identifiers. For this
        # prototype, the sequence is accepted only when year, month, and day all
        # describe the move's accounting date.
        format_values = self._get_sequence_format_param(sequence)[1]
        year_match = not format_values["year"] or self._year_match(format_values["year"], sequence_date.year)
        month_match = not format_values["month"] or format_values["month"] == sequence_date.month
        day_match = not format_values["day"] or format_values["day"] == sequence_date.day
        return year_match and month_match and day_match

    def _get_next_sequence_format(self):
        """Fill the day placeholder when a new daily period starts."""
        format_string, format_values = super()._get_next_sequence_format()

        # Native code already refreshes year/month when a new period is detected.
        # It has no day key, so daily formats need this small companion update.
        if "day" in format_values:
            sequence_date = fields.Date.to_date(self[self._sequence_date_field])
            if sequence_date:
                format_values["day"] = sequence_date.day

        return format_string, format_values

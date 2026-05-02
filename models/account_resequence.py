# -*- coding: utf-8 -*-

from collections import defaultdict
import json

from odoo import api, models, _
from odoo.tools.misc import format_date


class AccountResequenceWizard(models.TransientModel):
    _inherit = "account.resequence.wizard"

    @api.depends("new_values", "ordering")
    def _compute_preview_moves(self):
        # Production-oriented custom note:
        # Native preview intentionally hides middle rows, but it keeps period
        # boundaries visible for year/month resets. Daily reset creates a new
        # accounting sequence period for each exact date, so the preview must
        # keep day changes visible as well.
        daily_records = self.filtered(lambda wizard: wizard.sequence_number_reset == "day")
        other_records = self - daily_records
        if other_records:
            super(AccountResequenceWizard, other_records)._compute_preview_moves()

        for record in daily_records:
            new_values = sorted(
                json.loads(record.new_values or "{}").values(),
                key=lambda value: value["server-date"],
                reverse=True,
            )
            change_lines = []
            in_ellipsis = 0
            previous_line = None
            for index, line in enumerate(new_values):
                show_line = (
                    index < 3
                    or index == len(new_values) - 1
                    or line["new_by_name"] != line["new_by_date"]
                    or (previous_line and line["server-date"] != previous_line["server-date"])
                )
                if show_line:
                    if in_ellipsis:
                        change_lines.append({
                            "id": "other_" + str(line["id"]),
                            "current_name": _(
                                "... (%(nb_of_values)s other)",
                                nb_of_values=in_ellipsis,
                            ),
                            "new_by_name": "...",
                            "new_by_date": "...",
                            "date": "...",
                        })
                        in_ellipsis = 0
                    change_lines.append(line)
                else:
                    in_ellipsis += 1
                previous_line = line

            record.preview_moves = json.dumps({
                "ordering": record.ordering,
                "changeLines": change_lines,
            })

    @api.depends("first_name", "move_ids", "sequence_number_reset")
    def _compute_new_values(self):
        # Accounting-sequence risk:
        # Resequencing posted entries is sensitive. This override leaves native
        # year/month/fixed handling untouched and only computes values for
        # sequences that the shared sequence.mixin parser has explicitly
        # detected as daily.
        daily_records = self.filtered(lambda wizard: wizard.sequence_number_reset == "day")
        other_records = self - daily_records
        if other_records:
            super(AccountResequenceWizard, other_records)._compute_new_values()

        for record in daily_records:
            record.new_values = "{}"
            if not record.first_name:
                continue

            moves_by_period = defaultdict(lambda: record.env["account.move"])
            for move in record.move_ids._origin:
                # Daily reset means each accounting date is its own period. The
                # journal/company isolation is still provided by the native
                # wizard selection rules and account.move sequence constraints.
                moves_by_period[(move.date.year, move.date.month, move.date.day)] += move

            seq_format, format_values = record.move_ids[0]._get_sequence_format_param(record.first_name)
            sequence_number_reset = record.move_ids[0]._deduce_sequence_number_reset(record.first_name)

            new_values = {}
            # Work from newest date to oldest date, matching the native wizard's
            # preview direction while ensuring the oldest selected daily period
            # receives the sequence number entered in First New Sequence.
            periods = sorted(
                moves_by_period.values(),
                key=lambda period_recs: period_recs[0].date,
                reverse=True,
            )
            for period_index, period_recs in enumerate(periods):
                # For daily reset, sequence.mixin returns the exact move date as
                # both date_start and date_end. Using this range prevents the
                # day embedded in first_name from leaking into later periods.
                date_start, date_end, forced_year_start, forced_year_end = (
                    period_recs[0]._get_sequence_date_range(sequence_number_reset)
                )
                for move in period_recs:
                    new_values[move.id] = {
                        "id": move.id,
                        "current_name": move.name,
                        "state": move.state,
                        "date": format_date(record.env, move.date),
                        "server-date": str(move.date),
                        "server-year-start-date": str(date_start),
                    }

                start_sequence = format_values["seq"] if period_index == (len(periods) - 1) else 1
                new_name_list = [
                    seq_format.format(**{
                        **format_values,
                        "day": date_start.day,
                        "month": date_start.month,
                        "year_end": (
                            (forced_year_end or date_end.year)
                            % (10 ** format_values["year_end_length"])
                        ),
                        "year": (
                            (forced_year_start or date_start.year)
                            % (10 ** format_values["year_length"])
                        ),
                        "seq": index + start_sequence,
                    })
                    for index in range(len(period_recs))
                ]

                # Preserve native ordering options: either keep the current
                # sequence order or assign by accounting date order.
                for move, new_name in zip(
                    period_recs.sorted(lambda move: (move.sequence_prefix, move.sequence_number)),
                    new_name_list,
                ):
                    new_values[move.id]["new_by_name"] = new_name
                for move, new_name in zip(
                    period_recs.sorted(lambda move: (move.date, move.name or "", move.id)),
                    new_name_list,
                ):
                    new_values[move.id]["new_by_date"] = new_name

            record.new_values = json.dumps(new_values)

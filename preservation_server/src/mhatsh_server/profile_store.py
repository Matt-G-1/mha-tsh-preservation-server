from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable


class ProfileStore:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else None
        self.roles: dict[str, int] = {}
        self.active_cards: dict[str, int] = {}
        self.stage_progress: dict[str, dict[str, dict[str, int | list[int]]]] = {}
        self.stage_family_progress: dict[str, dict[str, dict[str, int]]] = {}
        self.normal_items: dict[str, dict[str, int]] = {}
        self.finished_tasks: dict[str, set[int]] = {}
        self.base_station_levels: dict[str, dict[str, int]] = {}
        self.load()

    def load(self) -> None:
        if self.path is None or not self.path.exists():
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(raw, dict):
            return
        self.roles = self._int_map(raw.get("roles"))
        self.active_cards = self._int_map(raw.get("active_cards"))
        self.stage_progress = self._stage_progress_map(raw.get("stage_progress"))
        self.stage_family_progress = self._stage_family_progress_map(
            raw.get("stage_family_progress")
        )
        self.normal_items = self._normal_items_map(raw.get("normal_items"))
        self.finished_tasks = self._finished_tasks_map(raw.get("finished_tasks"))
        self.base_station_levels = self._base_station_levels_map(
            raw.get("base_station_levels")
        )

    def remember_role(self, urs: str, uid: int) -> None:
        self.roles[str(urs)] = int(uid)
        self.save()

    def remember_active_card(self, urs: str, card_uid: int) -> None:
        self.active_cards[str(urs)] = int(card_uid)
        self.save()

    def remember_stage_progress(
        self, urs: str, progress: dict[int, dict[str, int | list[int]]]
    ) -> None:
        self.stage_progress[str(urs)] = {
            str(stage_id): dict(values)
            for stage_id, values in progress.items()
        }
        self.save()

    def remember_stage_family_progress(
        self,
        urs: str,
        progress: dict[str, dict[int, int]],
    ) -> None:
        self.stage_family_progress[str(urs)] = {
            str(section): {
                str(key): int(value)
                for key, value in values.items()
                if int(key) > 0 and int(value) >= 0
            }
            for section, values in progress.items()
        }
        self.save()

    def remember_finished_tasks(
        self, urs: str, task_ids: Iterable[int]
    ) -> None:
        normalized = {
            int(task_id) for task_id in task_ids if int(task_id) > 0
        }
        self.finished_tasks[str(urs)] = normalized
        self.save()

    def remember_base_station_levels(
        self, urs: str, levels: dict[int, int]
    ) -> None:
        self.base_station_levels[str(urs)] = {
            str(base_station_id): int(level)
            for base_station_id, level in levels.items()
            if int(base_station_id) > 0 and int(level) > 0
        }
        self.save()

    def grant_items(self, urs: str, rewards: Iterable[tuple[int, int]]) -> None:
        item_counts = self.normal_items.setdefault(str(urs), {})
        changed = False
        for item_id, count in rewards:
            numeric_item_id = int(item_id)
            numeric_count = int(count)
            if numeric_item_id <= 0 or numeric_count <= 0:
                continue
            key = str(numeric_item_id)
            item_counts[key] = int(item_counts.get(key, 0)) + numeric_count
            changed = True
        if changed:
            self.save()

    def normal_item_list(self, urs: str) -> list[dict[str, int]]:
        return [
            {"ItemId": int(item_id), "Amount": amount}
            for item_id, amount in sorted(
                self.normal_items.get(str(urs), {}).items(),
                key=lambda item: int(item[0]),
            )
        ]

    def save(self) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(self.path.suffix + ".tmp")
        temp_path.write_text(
            json.dumps(
                {
                    "roles": self.roles,
                    "active_cards": self.active_cards,
                    "stage_progress": self.stage_progress,
                    "stage_family_progress": self.stage_family_progress,
                    "normal_items": self.normal_items,
                    "finished_tasks": {
                        str(urs): sorted(task_ids)
                        for urs, task_ids in self.finished_tasks.items()
                    },
                    "base_station_levels": self.base_station_levels,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        temp_path.replace(self.path)

    @staticmethod
    def _int_map(value: Any) -> dict[str, int]:
        if not isinstance(value, dict):
            return {}
        output: dict[str, int] = {}
        for key, item in value.items():
            try:
                output[str(key)] = int(item)
            except (TypeError, ValueError):
                continue
        return output

    @staticmethod
    def _stage_progress_map(
        value: Any,
    ) -> dict[str, dict[str, dict[str, int | list[int]]]]:
        if not isinstance(value, dict):
            return {}
        output: dict[str, dict[str, dict[str, int | list[int]]]] = {}
        for urs, stages in value.items():
            if not isinstance(stages, dict):
                continue
            stage_output: dict[str, dict[str, int | list[int]]] = {}
            for stage_id, raw_progress in stages.items():
                if not isinstance(raw_progress, dict):
                    continue
                try:
                    normalized = {
                        "status": int(raw_progress.get("status", 0)),
                        "full_star_time": int(
                            raw_progress.get("full_star_time", 0)
                        ),
                        "best_time": int(raw_progress.get("best_time", 0)),
                        "pass_count": int(raw_progress.get("pass_count", 0)),
                        "stars": [
                            int(item)
                            for item in list(raw_progress.get("stars") or [])
                        ],
                    }
                except (TypeError, ValueError):
                    continue
                stage_output[str(stage_id)] = normalized
            output[str(urs)] = stage_output
        return output

    @staticmethod
    def _stage_family_progress_map(
        value: Any,
    ) -> dict[str, dict[str, dict[str, int]]]:
        if not isinstance(value, dict):
            return {}
        output: dict[str, dict[str, dict[str, int]]] = {}
        for urs, sections in value.items():
            if not isinstance(sections, dict):
                continue
            normalized_sections: dict[str, dict[str, int]] = {}
            for section, entries in sections.items():
                if not isinstance(entries, dict):
                    continue
                normalized_entries: dict[str, int] = {}
                for key, raw_value in entries.items():
                    try:
                        numeric_key = int(key)
                        numeric_value = int(raw_value)
                    except (TypeError, ValueError):
                        continue
                    if numeric_key > 0 and numeric_value >= 0:
                        normalized_entries[str(numeric_key)] = numeric_value
                normalized_sections[str(section)] = normalized_entries
            output[str(urs)] = normalized_sections
        return output

    @staticmethod
    def _normal_items_map(value: Any) -> dict[str, dict[str, int]]:
        if not isinstance(value, dict):
            return {}
        output: dict[str, dict[str, int]] = {}
        for urs, items in value.items():
            if not isinstance(items, dict):
                continue
            item_output: dict[str, int] = {}
            for item_id, count in items.items():
                try:
                    numeric_item_id = int(item_id)
                    numeric_count = int(count)
                except (TypeError, ValueError):
                    continue
                if numeric_item_id > 0 and numeric_count > 0:
                    item_output[str(numeric_item_id)] = numeric_count
            output[str(urs)] = item_output
        return output

    @staticmethod
    def _finished_tasks_map(value: Any) -> dict[str, set[int]]:
        if not isinstance(value, dict):
            return {}
        output: dict[str, set[int]] = {}
        for urs, task_ids in value.items():
            if not isinstance(task_ids, list):
                continue
            normalized: set[int] = set()
            for task_id in task_ids:
                try:
                    numeric_task_id = int(task_id)
                except (TypeError, ValueError):
                    continue
                if numeric_task_id > 0:
                    normalized.add(numeric_task_id)
            output[str(urs)] = normalized
        return output

    @staticmethod
    def _base_station_levels_map(value: Any) -> dict[str, dict[str, int]]:
        if not isinstance(value, dict):
            return {}
        output: dict[str, dict[str, int]] = {}
        for urs, levels in value.items():
            if not isinstance(levels, dict):
                continue
            normalized: dict[str, int] = {}
            for base_station_id, level in levels.items():
                try:
                    numeric_base_station_id = int(base_station_id)
                    numeric_level = int(level)
                except (TypeError, ValueError):
                    continue
                if numeric_base_station_id > 0 and numeric_level > 0:
                    normalized[str(numeric_base_station_id)] = numeric_level
            output[str(urs)] = normalized
        return output

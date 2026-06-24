from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class TutorialState:
    completed_guide_sets: set[int] = field(default_factory=set)
    completed_guide_ids: set[int] = field(default_factory=set)
    requested_login_drama_stages: list[int] = field(default_factory=list)
    finished_login_drama_stages: dict[int, int] = field(default_factory=dict)
    guide_drama_steps: dict[int, int] = field(default_factory=dict)
    client_stats: list[dict[str, object]] = field(default_factory=list)
    teach_skill_counts: dict[int, dict[int, int]] = field(default_factory=dict)
    base_station_client_version: int = 0
    base_station_levels: dict[int, int] = field(default_factory=dict)

    def finish_guides(
        self,
        set_ids: list[int] | tuple[int, ...],
        guide_ids: list[int] | tuple[int, ...],
    ) -> dict[str, object]:
        self.completed_guide_sets.update(int(set_id) for set_id in set_ids)
        self.completed_guide_ids.update(int(guide_id) for guide_id in guide_ids)
        return {
            "Sets": sorted(self.completed_guide_sets),
            "Ids": sorted(self.completed_guide_ids),
        }

    def seed_completed_guide(self, guide_id: int, set_id: int | None = None) -> None:
        self.completed_guide_ids.add(int(guide_id))
        if set_id is not None:
            self.completed_guide_sets.add(int(set_id))

    def record_login_drama_request(
        self, stage_id: int, drama_name: str, loop: int
    ) -> dict[str, object] | None:
        self.requested_login_drama_stages.append(stage_id)
        if not drama_name:
            return None
        return {"DramaName": drama_name, "Loop": loop}

    def finish_login_drama(self, uid: int, stage_id: int) -> None:
        self.finished_login_drama_stages[stage_id] = uid

    def record_guide_drama(self, guide_id: int, step: int) -> None:
        self.guide_drama_steps[guide_id] = step

    def record_client_stat(
        self, stat_id: int, num_data: list[int], str_data: list[str]
    ) -> dict[str, object]:
        stat = {"StatId": stat_id, "NumData": num_data, "StrData": str_data}
        self.client_stats.append(stat)
        return stat

    def finish_teach(
        self, hero_cid: int, skills: list[dict[str, object]]
    ) -> dict[str, object]:
        hero_skills = self.teach_skill_counts.setdefault(hero_cid, {})
        for skill in skills:
            skill_id = int(skill.get("SkillId") or 0)
            if not skill_id:
                continue
            hero_skills[skill_id] = max(
                int(skill.get("Count") or 0),
                hero_skills.get(skill_id, 0),
            )
        return {
            "HeroCId": hero_cid,
            "SkillList": [
                {"SkillId": skill_id, "Count": count}
                for skill_id, count in sorted(hero_skills.items())
            ],
        }

    def base_station_all_info(self, client_version: int) -> dict[str, object]:
        self.base_station_client_version = client_version
        return {
            "iClientVersion": client_version,
            "arrFinishAidCount": [],
            "arrBaseStationInfo": [
                self.base_station_info(base_station_id)
                for base_station_id in sorted(self.base_station_levels)
            ],
        }

    def activate_base_station(self, base_station_id: int) -> dict[str, object]:
        numeric_base_station_id = max(1, int(base_station_id or 1))
        self.base_station_levels.setdefault(numeric_base_station_id, 1)
        return {"iBaseStationId": numeric_base_station_id, "iResult": 1}

    def upgrade_base_station(self, base_station_id: int) -> dict[str, object]:
        numeric_base_station_id = max(1, int(base_station_id or 1))
        self.base_station_levels[numeric_base_station_id] = min(
            self.base_station_levels.get(numeric_base_station_id, 1) + 1,
            10,
        )
        return {"mpBaseStationInfo": self.base_station_info(numeric_base_station_id)}

    def base_station_info(self, base_station_id: int) -> dict[str, object]:
        numeric_base_station_id = max(1, int(base_station_id or 1))
        return {
            "iBaseStationId": numeric_base_station_id,
            "iLevel": self.base_station_levels.get(numeric_base_station_id, 1),
            "iFinishTaskCount": 0,
            "iFinishEntrustTaskCount": 0,
        }

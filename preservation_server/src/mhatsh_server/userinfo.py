from __future__ import annotations

import time
from dataclasses import dataclass, field

from .roster import RosterState


@dataclass(slots=True)
class UserInfoState:
    sign: str = ""
    location: str = ""
    hide_location: int = 0
    sex: int = 0
    hide_sex: int = 0
    birthday_year: int = 0
    birthday_month: int = 0
    birthday_day: int = 0
    hide_birthday: int = 0
    set_birthday_time: int = 0
    badges: list[int] = field(default_factory=list)
    tags: list[int] = field(default_factory=list)

    def info(
        self, uid: int, roster: RosterState, *, achieve_num: int = 0
    ) -> dict[str, object]:
        return {
            "Info": {
                "Uid": int(uid),
                "HideBirthday": self.hide_birthday,
                "SetBirthdayTime": self.set_birthday_time,
                "Year": self.birthday_year,
                "Month": self.birthday_month,
                "Day": self.birthday_day,
                "HideLocation": self.hide_location,
                "Location": self.location,
                "Sex": self.sex,
                "HideSex": self.hide_sex,
                "AchieveNum": int(achieve_num),
                "SeasonPoint": 0,
                "Badge": list(self.badges),
                "Tag": list(self.tags),
                "Heros": roster.hero_set(()),
            }
        }

    def base_info(
        self,
        requested_uids: list[int],
        *,
        uid: int,
        name: str,
        level: int,
        fighting: int,
    ) -> dict[str, object]:
        targets = [int(item) for item in requested_uids if int(item) > 0] or [int(uid)]
        return {
            "BaseInfo": [
                {
                    "Uid": target_uid,
                    "Name": name if target_uid == int(uid) else f"Local Hero {target_uid}",
                    "Level": int(level),
                    "TopLevel": 0,
                    "AvatarId": 0,
                    "AvatarFrameId": 0,
                    "Online": int(target_uid == int(uid)),
                    "Fighting": int(fighting),
                }
                for target_uid in targets
            ]
        }

    def brief_info(self, requested_uids: list[int], *, uid: int) -> dict[str, object]:
        targets = [int(item) for item in requested_uids if int(item) > 0] or [int(uid)]
        return {
            "List": [
                {
                    "Uid": target_uid,
                    "Avatar": 0,
                    "AvatarFrame": 0,
                    "TeamUid": 0,
                    "SvrId": 1,
                }
                for target_uid in targets
            ]
        }

    def other_info(
        self,
        target_uid: int,
        roster: RosterState,
        *,
        name: str,
        level: int,
        achieve_num: int = 0,
    ) -> dict[str, object]:
        return {
            "Info": {
                "Uid": int(target_uid),
                "Name": name,
                "Level": int(level),
                "TopLevel": 0,
                "TotalScore": 0,
                "AvatarId": 0,
                "AvatarFrameId": 0,
                "TitleId": 0,
                "LeagueName": "",
                "AchieveNum": int(achieve_num),
                "Year": self.birthday_year if not self.hide_birthday else 0,
                "Month": self.birthday_month if not self.hide_birthday else 0,
                "Day": self.birthday_day if not self.hide_birthday else 0,
                "Location": "" if self.hide_location else self.location,
                "Tag": list(self.tags),
                "Sign": self.sign,
                "Dynamic": [],
                "Sex": 0 if self.hide_sex else self.sex,
                "Badge": list(self.badges),
                "Heros": [
                    {"Cid": hero_id, "Quality": 1, "Level": roster.hero_level}
                    for hero_id in roster.hero_set(())
                ],
            }
        }

    def set_sign(self, sign: str) -> dict[str, str]:
        self.sign = str(sign)
        return {"Sign": self.sign}

    def set_location(self, location: str) -> dict[str, object]:
        self.location = str(location)
        return {"HideLocation": self.hide_location, "Location": self.location}

    def set_location_hidden(self, hide: int) -> dict[str, object]:
        self.hide_location = int(hide)
        return {"HideLocation": self.hide_location, "Location": self.location}

    def set_sex(self, sex: int) -> dict[str, int]:
        self.sex = int(sex)
        return {"Sex": self.sex, "HideSex": self.hide_sex}

    def set_sex_hidden(self, hide: int) -> dict[str, int]:
        self.hide_sex = int(hide)
        return {"Sex": self.sex, "HideSex": self.hide_sex}

    def set_birthday(self, year: int, month: int, day: int) -> dict[str, int]:
        self.birthday_year = max(0, int(year))
        self.birthday_month = max(0, int(month))
        self.birthday_day = max(0, int(day))
        self.set_birthday_time = int(time.time())
        return self._birthday_payload()

    def set_birthday_hidden(self, hide: int) -> dict[str, int]:
        self.hide_birthday = int(hide)
        return self._birthday_payload()

    def _birthday_payload(self) -> dict[str, int]:
        return {
            "HideBirthday": self.hide_birthday,
            "SetBirthdayTime": self.set_birthday_time,
            "Year": self.birthday_year,
            "Month": self.birthday_month,
            "Day": self.birthday_day,
        }

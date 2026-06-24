from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class ScenePosition:
    x: int
    y: int
    z: int
    face: int = 0
    speed: int = 0
    character_state: int = 0
    character_action: int = 0
    extra: int = 0

    @classmethod
    def from_protocol(cls, values: dict[str, object]) -> "ScenePosition":
        return cls(
            x=int(values.get("X") or 0),
            y=int(values.get("Y") or 0),
            z=int(values.get("Z") or 0),
            face=int(values.get("Face") or 0),
            speed=int(values.get("Speed") or 0),
            character_state=int(values.get("ChState") or 0),
            character_action=int(values.get("ChAction") or 0),
            extra=int(values.get("Extra") or 0),
        )


@dataclass(slots=True)
class ClientFrameStat:
    uid: int
    stage_id: int
    frame: int
    image_level: int


class WorldState:
    def __init__(self) -> None:
        self.last_position: ScenePosition | None = None
        self.move_count = 0
        self.sync_position_count = 0
        self.current_scene_line_id = 1
        self.current_scene_obj_id = 0
        self.last_action_id = 0
        self.frame_stats: list[ClientFrameStat] = []
        self.client_errors: list[str] = []
        self.unhandled_messages: list[dict[str, object]] = []

    def record_move(self, path: list[dict[str, object]]) -> ScenePosition | None:
        if not path:
            return None
        self.last_position = ScenePosition.from_protocol(path[-1])
        self.move_count += 1
        return self.last_position

    def record_sync_position(
        self, x: int, y: int, z: int, face: int
    ) -> ScenePosition:
        self.last_position = ScenePosition(x=int(x), y=int(y), z=int(z), face=int(face))
        self.sync_position_count += 1
        return self.last_position

    def line_info(self, scene_id: int) -> dict[str, object]:
        return {
            "SceneId": int(scene_id),
            "Line": self.current_scene_line_id,
            "List": [
                {
                    "LineId": self.current_scene_line_id,
                    "SceneId": int(scene_id),
                    "Status": 1,
                }
            ],
        }

    def change_line(self, scene_id: int, line_id: int) -> dict[str, object]:
        self.current_scene_line_id = max(1, int(line_id))
        return self.line_info(scene_id)

    def record_scene_obj_curid(self, cur_id: int) -> None:
        self.current_scene_obj_id = int(cur_id)

    def record_action_change(self, action_id: int) -> int:
        self.last_action_id = int(action_id)
        return self.last_action_id

    def record_frame_stat(
        self, uid: int, stage_id: int, frame: int, image_level: int
    ) -> ClientFrameStat:
        stat = ClientFrameStat(
            uid=uid,
            stage_id=stage_id,
            frame=frame,
            image_level=image_level,
        )
        self.frame_stats.append(stat)
        return stat

    def record_client_error(self, message: str) -> None:
        self.client_errors.append(message)

    def record_unhandled_message(
        self, name: str, protocol_id: int, values: dict[str, object]
    ) -> None:
        self.unhandled_messages.append(
            {"Name": name, "ProtocolId": protocol_id, "Values": values}
        )

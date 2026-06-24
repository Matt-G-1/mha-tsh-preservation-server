from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class MailRecord:
    mail_id: int
    sender_name: str = "Local Preservation Server"
    send_time: int = 0
    text_id: int = 0
    read_status: int = 0
    attach_status: int = 0
    timeout: int = 0
    title_params: tuple[str, ...] = ()
    content_params: tuple[str, ...] = ()
    attachments: tuple[dict[str, object], ...] = ()

    def to_simple_protocol(self) -> dict[str, object]:
        return {
            "iMailId": self.mail_id,
            "cSenderName": self.sender_name,
            "iSendTime": self.send_time,
            "iTextId": self.text_id,
            "iReadStatus": self.read_status,
            "arrTitleParams": list(self.title_params),
            "arrContentParams": list(self.content_params),
            "iAttachStatus": self.attach_status,
            "iTimeOut": self.timeout,
        }

    def to_detail_protocol(self) -> dict[str, object]:
        return {
            "iMailId": self.mail_id,
            "arrAttachList": list(self.attachments),
        }


@dataclass(slots=True)
class MailState:
    version: int = 1
    mails: dict[int, MailRecord] = field(default_factory=dict)

    def mail_list(self, requested_version: int) -> dict[str, object]:
        return {
            "iVersion": max(self.version, int(requested_version)),
            "arrMailSimpleInfos": [
                mail.to_simple_protocol()
                for mail in sorted(self.mails.values(), key=lambda item: item.mail_id)
            ],
            "iIsFinish": 1,
        }

    def mail_info(self, mail_id: int) -> dict[str, object]:
        mail = self.mails.get(int(mail_id)) or MailRecord(int(mail_id))
        mail.read_status = 1
        return {"mpMailInfo": mail.to_detail_protocol()}

    def get_attach(self, mail_id: int) -> dict[str, int] | None:
        mail = self.mails.get(int(mail_id))
        if mail is None or not mail.attachments:
            return None
        mail.attach_status = 1
        return {"iMailId": mail.mail_id}

    def quickly_get_attach(self) -> dict[str, object]:
        mail_ids: list[int] = []
        for mail in self.mails.values():
            if mail.attachments and not mail.attach_status:
                mail.attach_status = 1
                mail_ids.append(mail.mail_id)
        return {"arrMailIds": sorted(mail_ids)}

    def delete(self, mail_ids: list[int]) -> dict[str, object]:
        normalized = [int(mail_id) for mail_id in mail_ids if int(mail_id) > 0]
        for mail_id in normalized:
            self.mails.pop(mail_id, None)
        if normalized:
            self.version += 1
        return {"arrMailIds": normalized}

from __future__ import annotations

import json
import os
import smtplib
import re
from email import policy
from email.message import EmailMessage
from email.header import Header
from typing import Optional, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class EmailHandoffInput(BaseModel):
    customer_name: str = Field(..., description="Tên khách hàng.")
    customer_phone: str = Field(..., description="Số điện thoại khách hàng.")
    issue: str = Field(..., description="Vấn đề khách gặp phải/cần hỗ trợ.")
    product_model: Optional[str] = Field(None, description="Model sản phẩm (nếu có).")
    chat_history_json: Optional[str] = Field(
        None,
        description="Lịch sử hội thoại dạng JSON list (role/content). Nếu có thì gửi kèm để hỗ trợ hiểu ngữ cảnh.",
    )


class EmailHandoffTool(BaseTool):
    name: str = "handoff_support_via_email"
    description: str = (
        "Gửi email handoff cho bộ phận hỗ trợ khi agent không đủ thông tin/tài liệu để trả lời chắc chắn. "
        "Chỉ dùng sau khi khách đã đồng ý và cung cấp tên + SĐT."
    )
    args_schema: Type[BaseModel] = EmailHandoffInput

    def _clean(self, text: str) -> str:
        # Replace non-breaking spaces and normalize whitespace to avoid header encoding issues.
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _run(
        self,
        customer_name: str,
        customer_phone: str,
        issue: str,
        product_model: Optional[str] = None,
        chat_history_json: Optional[str] = None,
    ) -> str:
        smtp_user_raw = os.getenv("SMTP_USER") or ""
        smtp_app_password_raw = os.getenv("SMTP_APP_PASSWORD") or ""
        to_email_raw = os.getenv("SUPPORT_TO_EMAIL") or "doan180224@gmail.com"

        smtp_user = self._clean(smtp_user_raw)
        # App Passwords are safe to de-whitespace; also guard against NBSP paste.
        smtp_app_password = re.sub(r"\s+", "", smtp_app_password_raw.replace("\xa0", " ")).strip()
        to_email = self._clean(to_email_raw)

        if not smtp_user or not smtp_app_password:
            return (
                "Thiếu cấu hình SMTP. Vui lòng set biến môi trường:\n"
                "- SMTP_USER\n"
                "- SMTP_APP_PASSWORD\n"
                f"- (optional) SUPPORT_TO_EMAIL (default: {to_email})"
            )

        msg = EmailMessage(policy=policy.SMTPUTF8)
        subject_bits = ["[IonQ] Handoff hỗ trợ kỹ thuật"]
        if product_model:
            subject_bits.append(product_model)
        subject_bits.append(customer_phone.strip())
        subject = self._clean(" | ".join(subject_bits))
        msg["Subject"] = str(Header(subject, "utf-8"))
        msg["From"] = smtp_user
        msg["To"] = to_email

        history_pretty = ""
        if chat_history_json:
            try:
                history = json.loads(chat_history_json)
                if isinstance(history, list):
                    lines = []
                    for item in history[-20:]:
                        role = str(item.get("role", "")).strip()
                        content = str(item.get("content", "")).strip()
                        if role and content:
                            lines.append(self._clean(f"{role}: {content}"))
                    if lines:
                        history_pretty = "\n".join(lines)
            except Exception:
                history_pretty = ""

        body_lines = [
            "Có khách cần hỗ trợ trực tiếp.",
            "",
            f"Tên: {self._clean(customer_name)}",
            f"SĐT: {self._clean(customer_phone)}",
            f"Model: {self._clean((product_model or '').strip() or '(không rõ)')}",
            "",
            "Vấn đề khách gặp:",
            self._clean(issue),
        ]
        if history_pretty:
            body_lines += [
                "",
                "Lịch sử hội thoại (rút gọn):",
                history_pretty,
            ]

        msg.set_content("\n".join(body_lines).strip() + "\n", charset="utf-8")

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as server:
                server.login(smtp_user, smtp_app_password)
                # Ensure UTF-8 headers/body are accepted by the SMTP server.
                server.send_message(msg, mail_options=["SMTPUTF8"])
            return f"Đã gửi handoff email tới {to_email}."
        except Exception as e:
            return f"Gửi email thất bại: {e}"


import json
import os
from urllib import error, request


class CanvaSkill:
    """
    Generates branded proposal/contract deliverables through the Canva API.
    Degrades safely when credentials or template ids are not configured.
    """

    API_BASE = "https://api.canva.com/rest/v1"

    def __init__(self, api_token=None, template_ids=None):
        self.api_token = api_token or os.getenv("CANVA_API_KEY")
        raw_template_ids = template_ids or {
            "proposal": os.getenv("CANVA_PROPOSAL_TEMPLATE_ID"),
            "contract": os.getenv("CANVA_CONTRACT_TEMPLATE_ID"),
            "roadmap": os.getenv("CANVA_ROADMAP_TEMPLATE_ID"),
        }
        self.template_ids = {
            label: value
            for label, value in raw_template_ids.items()
            if value and not self._is_placeholder(value)
        }
        self.enabled = bool(self.api_token and not self._is_placeholder(self.api_token))

    def get_configuration_status(self):
        missing_template_labels = [
            label
            for label in ("proposal", "contract", "roadmap")
            if label not in self.template_ids
        ]
        return {
            "api_token_configured": self.enabled,
            "configured_templates": sorted(self.template_ids.keys()),
            "missing_templates": missing_template_labels,
            "ready": self.enabled and bool(self.template_ids),
        }

    def populate_template(self, template_id, data_map, title=None):
        if not self.enabled or not template_id:
            return {"ok": False, "reason": "canva_not_configured"}

        payload = {
            "template_id": template_id,
            "title": title or "Freelance-OS Deliverable",
            "data": data_map,
        }
        return self._request_json("/designs", payload)

    def export_as_pdf(self, design_id):
        if not self.enabled or not design_id:
            return {"ok": False, "reason": "canva_not_configured"}

        payload = {"format": "pdf"}
        return self._request_json(f"/designs/{design_id}/exports", payload)

    def create_deliverables(self, strategy_data):
        """
        Creates proposal, contract, and roadmap deliverables when Canva is configured.
        """
        config_status = self.get_configuration_status()
        if not config_status["ready"]:
            return {"_configuration": {"ok": False, **config_status}}

        deliverables = {}
        data_map = self._build_data_map(strategy_data)

        for label, template_id in self.template_ids.items():
            if not template_id:
                continue
            design = self.populate_template(
                template_id=template_id,
                data_map=data_map,
                title=f"{strategy_data.get('title', 'Client')} - {label.title()}",
            )
            if not design.get("ok"):
                deliverables[label] = design
                continue

            export = self.export_as_pdf(design.get("design_id"))
            deliverables[label] = {
                "ok": export.get("ok", False),
                "design_id": design.get("design_id"),
                "pdf_url": export.get("pdf_url"),
                "raw": export,
            }
        return deliverables

    def _build_data_map(self, strategy_data):
        return {
            "client_name": strategy_data.get("client_name") or strategy_data.get("title", "Client"),
            "project_title": strategy_data.get("title", "Project"),
            "budget": strategy_data.get("quotation") or strategy_data.get("budget", "TBD"),
            "stack": ", ".join(strategy_data.get("suggested_stack") or []),
            "summary": strategy_data.get("pitch_content", "")[:1200],
        }

    def _request_json(self, path, payload):
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            self.API_BASE + path,
            data=body,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=20) as response:
                data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            return {"ok": False, "reason": "http_error", "message": exc.read().decode("utf-8")}
        except Exception as exc:
            return {"ok": False, "reason": "request_failed", "message": str(exc)}

        return {
            "ok": True,
            "design_id": data.get("id") or data.get("design_id"),
            "pdf_url": data.get("url") or data.get("download_url"),
            "raw": data,
        }

    def _is_placeholder(self, value):
        normalized = str(value).strip().lower()
        return not normalized or normalized.startswith("your_")

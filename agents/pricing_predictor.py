import re

from core.agent_manager import BaseAgent


class PricingPredictor(BaseAgent):
    """
    Sub-agent that estimates project pricing from scope and complexity signals.
    """

    COMPLEXITY_KEYWORDS = {
        "simple": 1,
        "landing page": 1,
        "bug fix": 1,
        "dashboard": 2,
        "integration": 2,
        "api": 2,
        "mobile": 3,
        "rag": 3,
        "agent": 3,
        "automation": 2,
        "payments": 3,
        "real-time": 3,
        "security": 3,
        "compliance": 4,
        "architecture": 2,
        "scalable": 3,
    }

    def execute(self, task: str, input_data: dict) -> dict:
        if task != "estimate_price":
            return self._error_response(f"Task '{task}' not supported.")

        job_description = (input_data.get("job_description") or "").strip()
        if not job_description:
            return self._error_response("Missing required input: job_description.")

        budget_value = self._parse_budget(input_data.get("budget"))
        technical_doubts = input_data.get("technical_doubts") or []
        suggested_stack = input_data.get("suggested_stack") or []

        estimate = self._estimate(
            job_description=job_description,
            budget_value=budget_value,
            technical_doubts=technical_doubts,
            suggested_stack=suggested_stack,
        )
        response = self._format_response(
            "success",
            {
                "type": "json",
                "content": estimate,
            },
        )
        return self.validate_response(response)

    def _estimate(self, job_description, budget_value, technical_doubts, suggested_stack):
        lowered = job_description.lower()
        complexity_score = 1
        matched_signals = []
        for keyword, weight in self.COMPLEXITY_KEYWORDS.items():
            if keyword in lowered:
                complexity_score += weight
                matched_signals.append(keyword)

        complexity_score += min(len(technical_doubts), 4)
        complexity_score += min(len(suggested_stack), 3)

        if len(job_description.split()) > 120:
            complexity_score += 2

        normalized_score = max(2, min(complexity_score, 10))
        estimated_hours = normalized_score * 8
        hourly_rate = 45 + normalized_score * 12
        recommended_price = estimated_hours * hourly_rate

        if budget_value:
            floor = budget_value * 0.85
            ceiling = budget_value * 1.25
            recommended_price = max(floor, min(recommended_price, ceiling))

        complexity_band = self._complexity_band(normalized_score)
        return {
            "complexity_score": normalized_score,
            "complexity_band": complexity_band,
            "estimated_hours": estimated_hours,
            "recommended_price": round(recommended_price, 2),
            "budget_reference": budget_value,
            "confidence": self._confidence_label(technical_doubts),
            "rationale": self._build_rationale(
                complexity_band=complexity_band,
                matched_signals=matched_signals,
                technical_doubts=technical_doubts,
                suggested_stack=suggested_stack,
            ),
        }

    def _build_rationale(self, complexity_band, matched_signals, technical_doubts, suggested_stack):
        signals = matched_signals[:4] or ["general implementation scope"]
        return (
            f"Estimated as {complexity_band} complexity based on signals: {', '.join(signals)}. "
            f"Open technical questions: {len(technical_doubts)}. "
            f"Suggested stack breadth: {len(suggested_stack)}."
        )

    def _complexity_band(self, score):
        if score <= 3:
            return "low"
        if score <= 6:
            return "medium"
        if score <= 8:
            return "high"
        return "very_high"

    def _confidence_label(self, technical_doubts):
        if len(technical_doubts) >= 4:
            return "medium"
        if len(technical_doubts) >= 3:
            return "medium_high"
        return "low"

    def _parse_budget(self, budget):
        if budget is None:
            return None
        if isinstance(budget, (int, float)):
            return float(budget)
        match = re.search(r"(\d[\d,]*\.?\d*)", str(budget))
        if not match:
            return None
        return float(match.group(1).replace(",", ""))

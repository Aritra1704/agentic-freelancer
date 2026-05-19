import datetime
import re
import uuid

from core.database import SessionLocal, VerbatimLog
from core.ollama_bridge import OllamaBridge

class MemoryManager:
    """
    Implements MemPalace concepts for Freelance-OS:
    1. Verbatim Storage (Critical Data)
    2. Spatial Organization (Rooms)
    3. Temporal awareness
    """
    
    # Rooms (Spatial Organization)
    ROOM_SCOUTING = "scouting"
    ROOM_STRATEGY = "strategy"
    ROOM_EXECUTION = "execution"
    ROOM_PORTFOLIO = "portfolio"
    ROOM_TECH_BLOCKED = "tech_blocked"
    ROOM_BUSINESS_FRICTION = "business_friction"
    ROOM_MARKET_INTEL = "market_intel"

    _FAILURE_ROOMS = (
        ROOM_TECH_BLOCKED,
        ROOM_BUSINESS_FRICTION,
        ROOM_MARKET_INTEL,
    )
    _PATTERN_NICHE_TAGS = {
        "startup",
        "founder-led",
        "agency",
        "enterprise",
        "ecommerce",
        "saas",
        "healthcare",
        "fintech",
        "budget",
        "pricing",
        "competitor",
        "scope-creep",
    }
    _PATTERN_NICHE_PRIORITY = {
        "startup": 0,
        "founder-led": 1,
        "agency": 2,
        "enterprise": 3,
        "ecommerce": 4,
        "saas": 5,
        "healthcare": 6,
        "fintech": 7,
        "competitor": 8,
        "pricing": 9,
        "budget": 10,
        "scope-creep": 11,
        "general": 99,
    }

    _CONTEXT_PATTERNS = {
        "rag": r"\brag\b",
        "playwright": r"\bplaywright\b",
        "browser-use": r"\bbrowser[- ]use\b",
        "gemini": r"\bgemini\b",
        "ollama": r"\bollama\b",
        "langchain": r"\blangchain\b",
        "python": r"\bpython\b",
        "fastapi": r"\bfastapi\b",
        "django": r"\bdjango\b",
        "flask": r"\bflask\b",
        "react": r"\breact\b",
        "next.js": r"\bnext\.?js\b",
        "typescript": r"\btypescript\b",
        "postgres": r"\bpostgres(?:ql)?\b",
        "supabase": r"\bsupabase\b",
        "pinecone": r"\bpinecone\b",
        "openai": r"\bopenai\b",
        "automation": r"\bautomation\b",
        "api": r"\bapi\b",
        "scraping": r"\bscrap(?:e|ing)\b",
        "cloudflare": r"\bcloudflare\b",
        "budget": r"\bbudget\b",
        "scope-creep": r"\bscope(?:-| )?creep\b",
        "pricing": r"\bpricing\b",
        "competitor": r"\bcompetitor\b",
        "startup": r"\bstartup\b",
        "founder-led": r"\bfounder[- ]led\b",
        "agency": r"\bagency\b",
        "enterprise": r"\benterprise\b",
        "ecommerce": r"\be-?commerce\b",
        "saas": r"\bsaas\b",
        "healthcare": r"\bhealthcare\b",
        "fintech": r"\bfintech\b",
    }

    @staticmethod
    def remember_verbatim(category, interaction_type, content, metadata=None):
        """
        Stores unsummarized information to prevent information loss.
        """
        db = SessionLocal()
        log_entry = VerbatimLog(
            id=str(uuid.uuid4()),
            category=category,
            interaction_type=interaction_type,
            original_content=content,
            interaction_metadata=metadata or {}
        )
        db.add(log_entry)
        db.commit()
        db.close()
        print(f"🧠 MemPalace: Verbatim memory stored in {category}/{interaction_type}")

    @staticmethod
    def learn_from_failure(stage, observation, advice=None):
        """
        Distills a raw failure observation into a single objective pre-mortem
        instruction and stores it in a searchable MemPalace failure room.
        """
        normalized_stage = MemoryManager._normalize_stage(stage)
        normalized_observation = MemoryManager._normalize_text(observation)
        supporting_advice = MemoryManager._normalize_text(advice or "")
        context_tags = MemoryManager._extract_context_tags(
            " ".join(filter(None, [normalized_stage, normalized_observation, supporting_advice]))
        )
        room = MemoryManager._select_failure_room(
            normalized_stage,
            normalized_observation,
            context_tags,
        )
        pre_mortem_advice = MemoryManager._distill_pre_mortem_advice(
            normalized_stage,
            normalized_observation,
            supporting_advice,
        )

        interaction_id = str(uuid.uuid4())
        metadata = {
            "interaction_id": interaction_id,
            "room": room,
            "stage": normalized_stage,
            "context_tag": " / ".join(context_tags) if context_tags else normalized_stage,
            "context_tags": context_tags,
            "observation": normalized_observation,
            "pre_mortem_advice": pre_mortem_advice,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        }

        db = SessionLocal()
        try:
            log_entry = VerbatimLog(
                id=interaction_id,
                category=room,
                interaction_type="failure_learning",
                original_content=normalized_observation,
                interaction_metadata=metadata,
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()

        print(f"🧠 MemPalace: Failure pattern stored in {room}")
        return metadata

    @staticmethod
    def get_room_context(room, limit=5):
        """
        Retrieves context scoped to a specific 'Room' (Spatial Organization).
        """
        db = SessionLocal()
        try:
            logs = (
                db.query(VerbatimLog)
                .filter(VerbatimLog.category == room)
                .order_by(VerbatimLog.timestamp.desc())
                .limit(limit)
                .all()
            )
        finally:
            db.close()
        
        context = ""
        for log in logs:
            context += f"--- {log.interaction_type} ({log.timestamp}) ---\n"
            context += f"{log.original_content}\n\n"
        return context

    @staticmethod
    def find_relevant_failures(job_data, limit=5):
        """
        Returns recent failure memories that match the job's tech stack or
        client-type signals.
        """
        context_text = " ".join(
            str(job_data.get(field, ""))
            for field in ("title", "description", "platform", "client_type")
        )
        search_tags = MemoryManager._extract_context_tags(context_text)
        if not search_tags:
            return []

        db = SessionLocal()
        try:
            logs = (
                db.query(VerbatimLog)
                .filter(VerbatimLog.category.in_(MemoryManager._FAILURE_ROOMS))
                .order_by(VerbatimLog.timestamp.desc())
                .limit(50)
                .all()
            )
        finally:
            db.close()

        ranked_matches = []
        for log in logs:
            metadata = log.interaction_metadata or {}
            searchable_text = " ".join(
                [
                    str(metadata.get("context_tag", "")),
                    " ".join(metadata.get("context_tags", [])),
                    str(metadata.get("pre_mortem_advice", "")),
                    log.original_content or "",
                ]
            ).lower()
            matched_tags = [tag for tag in search_tags if tag.lower() in searchable_text]
            if not matched_tags:
                continue

            ranked_matches.append(
                {
                    "room": log.category,
                    "stage": metadata.get("stage", "unknown"),
                    "context_tag": metadata.get("context_tag", ""),
                    "context_tags": metadata.get("context_tags", []),
                    "observation": metadata.get("observation", log.original_content),
                    "pre_mortem_advice": metadata.get("pre_mortem_advice", ""),
                    "matched_tags": matched_tags,
                    "timestamp": log.timestamp,
                    "score": len(set(matched_tags)),
                }
            )

        ranked_matches.sort(
            key=lambda item: (
                item["score"],
                item["timestamp"] or datetime.datetime.min,
            ),
            reverse=True,
        )
        return ranked_matches[:limit]

    @staticmethod
    def detect_patterns():
        """
        Scans recent business-friction logs and produces a dashboard-friendly
        alert block when one niche shows repeated failures.
        """
        db = SessionLocal()
        try:
            logs = (
                db.query(VerbatimLog)
                .filter(VerbatimLog.category == MemoryManager.ROOM_BUSINESS_FRICTION)
                .order_by(VerbatimLog.timestamp.desc())
                .limit(10)
                .all()
            )
        finally:
            db.close()

        if not logs:
            return MemoryManager._build_pattern_result(False, entries_analyzed=0)

        counts = {}
        example_entries = {}
        for log in logs:
            metadata = log.interaction_metadata or {}
            tags = metadata.get("context_tags") or MemoryManager._extract_context_tags(
                " ".join(
                    [
                        str(metadata.get("context_tag", "")),
                        str(metadata.get("observation", "")),
                        log.original_content or "",
                    ]
                )
            )
            niche_tags = [tag for tag in tags if tag in MemoryManager._PATTERN_NICHE_TAGS]
            if not niche_tags:
                niche_tags = ["general"]

            for niche in set(niche_tags):
                counts[niche] = counts.get(niche, 0) + 1
                example_entries.setdefault(niche, []).append(
                    {
                        "timestamp": log.timestamp,
                        "observation": metadata.get("observation", log.original_content),
                        "pre_mortem_advice": metadata.get("pre_mortem_advice", ""),
                    }
                )

        niche, count = max(
            counts.items(),
            key=lambda item: (
                item[1],
                -MemoryManager._PATTERN_NICHE_PRIORITY.get(item[0], 50),
            ),
        )
        if count <= 3:
            return MemoryManager._build_pattern_result(
                False,
                niche=niche,
                count=count,
                entries_analyzed=len(logs),
            )

        alert_block = MemoryManager._build_alert_block(
            niche=niche,
            count=count,
            entries=example_entries.get(niche, []),
        )
        return MemoryManager._build_pattern_result(
            True,
            niche=niche,
            count=count,
            entries_analyzed=len(logs),
            alert_block=alert_block,
        )

    @staticmethod
    def _distill_pre_mortem_advice(stage, observation, advice):
        prompt = (
            "You are maintaining a blameless engineering memory system.\n"
            "Rewrite the failure below as one objective, action-oriented sentence "
            "that can be used as pre-mortem advice.\n"
            f"Stage: {stage}\n"
            f"Observation: {observation}\n"
            f"Optional prior advice: {advice or 'None'}\n"
            "Rules: keep it to one sentence, stay factual, avoid blame, and focus on prevention only."
        )

        bridge = OllamaBridge(model="mistral")
        response = MemoryManager._normalize_text(bridge.generate_code(prompt))
        if not response or response.lower().startswith("error:"):
            return MemoryManager._fallback_pre_mortem_advice(stage, observation, advice)
        return MemoryManager._clean_single_sentence(response)

    @staticmethod
    def _fallback_pre_mortem_advice(stage, observation, advice):
        if advice:
            return MemoryManager._clean_single_sentence(advice)

        condensed = MemoryManager._clean_single_sentence(observation)
        return (
            f"Before the {stage} phase, verify the assumptions behind this risk and "
            f"add a mitigation for: {condensed.lower()}"
        )

    @staticmethod
    def _build_alert_block(niche, count, entries):
        latest_advice = ""
        for entry in entries:
            if entry.get("pre_mortem_advice"):
                latest_advice = entry["pre_mortem_advice"]
                break

        niche_label = niche.replace("-", " ").title()
        lines = [
            f"Alert: {count} recent business-friction failures involve the '{niche_label}' niche.",
            "Action: tighten qualification, pricing, and scope controls before pursuing similar leads.",
        ]
        if latest_advice:
            lines.append(f"Guardrail: {latest_advice}")
        return "\n".join(lines)

    @staticmethod
    def _build_pattern_result(should_alert, niche="", count=0, entries_analyzed=0, alert_block=""):
        return {
            "should_alert": should_alert,
            "room": MemoryManager.ROOM_BUSINESS_FRICTION,
            "niche": niche,
            "count": count,
            "entries_analyzed": entries_analyzed,
            "alert_block": alert_block,
        }

    @staticmethod
    def _select_failure_room(stage, observation, context_tags):
        lowered = observation.lower()
        market_keywords = (
            "competitor",
            "pricing",
            "rate",
            "benchmark",
            "market",
            "hiring history",
        )
        business_keywords = (
            "ghost",
            "budget",
            "scope",
            "client",
            "payment",
            "proposal",
            "reject",
            "rejection",
            "timeline",
        )
        client_tags = {
            "startup",
            "founder-led",
            "agency",
            "enterprise",
            "ecommerce",
            "saas",
            "healthcare",
            "fintech",
        }

        if any(keyword in lowered for keyword in market_keywords):
            return MemoryManager.ROOM_MARKET_INTEL
        if any(keyword in lowered for keyword in business_keywords):
            return MemoryManager.ROOM_BUSINESS_FRICTION
        if any(tag in client_tags for tag in context_tags) and stage == "strategist":
            return MemoryManager.ROOM_BUSINESS_FRICTION
        return MemoryManager.ROOM_TECH_BLOCKED

    @staticmethod
    def _extract_context_tags(text):
        lowered = MemoryManager._normalize_text(text).lower()
        return [
            tag
            for tag, pattern in MemoryManager._CONTEXT_PATTERNS.items()
            if re.search(pattern, lowered)
        ]

    @staticmethod
    def _normalize_stage(stage):
        normalized = MemoryManager._normalize_text(stage).lower()
        aliases = {
            "scout": "scout",
            "scouting": "scout",
            "strategist": "strategist",
            "strategy": "strategist",
            "builder": "builder",
            "build": "builder",
            "execution": "builder",
        }
        return aliases.get(normalized, normalized or "unknown")

    @staticmethod
    def _normalize_text(value):
        return " ".join(str(value or "").strip().split())

    @staticmethod
    def _clean_single_sentence(text):
        cleaned = MemoryManager._normalize_text(text)
        if not cleaned:
            return ""

        cleaned = re.sub(r"^```(?:\w+)?", "", cleaned).strip("` ").strip()
        cleaned = re.sub(r"^\d+[.)]\s*", "", cleaned)
        sentence = re.split(r"(?<=[.!?])\s+", cleaned, maxsplit=1)[0].strip()
        if sentence and sentence[-1] not in ".!?":
            sentence += "."
        return sentence

from enum import Enum

class EngagementType(str, Enum):
    ONE_TIME = "One-time"
    CONTRACT = "Contract"
    HOURLY = "Hourly"

class ValuationLabel(str, Enum):
    HIGH = "High"
    LOW = "Low"

class LeadScorer:
    @staticmethod
    def calculate_priority(engagement_type: str, duration: str, budget: float) -> tuple[int, str]:
        """
        Calculates priority (1-10) and valuation label based on lead characteristics.
        """
        score = 0
        
        # Engagement Type weighting
        if engagement_type == EngagementType.ONE_TIME:
            score += 5
        elif engagement_type == EngagementType.CONTRACT:
            score += 2
        else: # Hourly
            score -= 2
            
        # Duration weighting (Duration assumed to be in months or string representation)
        if "month" in duration.lower() or "long-term" in duration.lower():
            score -= 3
        else:
            score += 1 # Short-term/project based

        # Budget weighting (Assuming budget is passed as a float)
        if budget > 5000:
            score += 3
            valuation = ValuationLabel.HIGH
        else:
            valuation = ValuationLabel.LOW
            
        # Clamp score between 1 and 10
        final_priority = max(1, min(10, score + 5)) # Base 5 to keep positive
        
        return final_priority, valuation

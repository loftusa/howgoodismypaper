from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class RatingValue(Enum):
    POOR = "1: poor"
    FAIR = "2: fair"
    GOOD = "3: good"
    EXCELLENT = "4: excellent"


class ConfidenceValue(Enum):
    VERY_LOW = "1: You are unable to assess this paper and have alerted the ACs to seek an opinion from different reviewers."
    LOW = "2: You are willing to defend your assessment, but it is quite likely that you did not understand the central parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked."
    MEDIUM = "3: You are fairly confident in your assessment. It is possible that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work. Math/other details were not carefully checked."
    HIGH = "4: You are confident in your assessment, but not absolutely certain. It is unlikely, but not impossible, that you did not understand some parts of the submission or that you are unfamiliar with some pieces of related work."
    VERY_HIGH = "5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully."


class RecommendationValue(Enum):
    STRONG_REJECT = "1: strong reject"
    REJECT = "3: reject, not good enough"
    MARGINALLY_BELOW = "5: marginally below the acceptance threshold"
    MARGINALLY_ABOVE = "6: marginally above the acceptance threshold"
    ACCEPT = "8: accept, good paper"
    STRONG_ACCEPT = "10: strong accept"


class EthicsFlag(Enum):
    NO = "No ethics review needed."
    YES = "Yes, ethics review needed."


class ReviewSchema(BaseModel):
    summary: str
    soundness: RatingValue
    presentation: RatingValue
    contribution: RatingValue
    strengths: str
    weaknesses: str
    questions: str
    ethics_flag: EthicsFlag
    ethics_concerns: Optional[str] = None
    rating: RecommendationValue
    confidence: ConfidenceValue
    code_of_conduct: bool = Field(..., description="Whether the reviewer agrees to the code of conduct")
    
    class Config:
        use_enum_values = True


class PaperMetadata(BaseModel):
    openreview_url: HttpUrl
    pdf_url: HttpUrl
    submission_date: datetime
    
    @property
    def json_filename(self) -> str:
        """Generate a filename for storing review data."""
        return f"{self.paper_id}.json"

    @property
    def paper_id(self) -> str:
        """Extract the paper ID from the openreview URL."""
        # The format of the openreview URL is https://openreview.net/forum?id=...
        return str(self.openreview_url).split("?id=")[-1]

    @classmethod
    def from_json(cls, json_path: Path | str) -> "PaperMetadata":
        json_data = Path(json_path).read_text()
        return cls.model_validate_json(json_data)


class PaperReviewData(BaseModel):
    metadata: PaperMetadata
    human_reviews: Dict[str, ReviewSchema] = Field(default_factory=dict)
    claude_review: Optional[ReviewSchema] = None 
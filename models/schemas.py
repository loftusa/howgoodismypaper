from enum import Enum
from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class RatingValue(Enum):
    POOR = "1: poor"
    FAIR = "2: fair"
    GOOD = "3: good"
    EXCELLENT = "4: excellent"


class ConfidenceValue(Enum):
    VERY_LOW = "1: You are not familiar with the relevant literature and are guessing."
    LOW = "2: You are not confident in your assessment, but have read the relevant literature."
    MEDIUM = "3: You are fairly confident in your assessment."
    HIGH = "4: You are confident in your assessment and very familiar with the relevant literature."
    VERY_HIGH = "5: You are absolutely certain about your assessment. You are very familiar with the related work and checked the math/other details carefully."


class RecommendationValue(Enum):
    STRONG_REJECT = "1: strong reject"
    REJECT = "2: reject"
    WEAK_REJECT = "3: reject, not good enough"
    WEAK_ACCEPT = "4: accept, good enough"
    ACCEPT = "5: accept"
    STRONG_ACCEPT = "6: strong accept"


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
        return self.openreview_url.path.split('?id=')[-1]


class PaperReviewData(BaseModel):
    metadata: PaperMetadata
    human_reviews: Dict[str, ReviewSchema] = Field(default_factory=dict)
    claude_review: Optional[ReviewSchema] = None 
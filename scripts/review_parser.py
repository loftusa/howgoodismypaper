import os
import json
import re
import sys
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

# Add the parent directory to sys.path to allow importing from models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.schemas import ReviewSchema, PaperMetadata, PaperReviewData


def create_paper_directory(paper_id: str, base_dir: str = "data") -> str:
    """Create directory structure for a paper."""
    paper_dir = os.path.join(base_dir, paper_id)
    os.makedirs(paper_dir, exist_ok=True)
    os.makedirs(os.path.join(paper_dir, "human_reviews"), exist_ok=True)
    os.makedirs(os.path.join(paper_dir, "claude_reviews"), exist_ok=True)
    os.makedirs(os.path.join(paper_dir, "raw_reviews"), exist_ok=True)
    return paper_dir


def create_paper_metadata(openreview_url: str, pdf_url: str, date_str: str) -> PaperMetadata:
    """Create paper metadata from command line arguments."""
    # Parse the date
    submission_date = datetime.strptime(date_str, "%d-%m-%Y")
    
    # Extract paper_id from openreview_url
    paper_id = openreview_url.split('?id=')[-1]
    
    # Create metadata
    metadata = PaperMetadata(
        openreview_url=openreview_url,
        pdf_url=pdf_url,
        submission_date=submission_date
    )
    
    # Create directory structure
    paper_dir = create_paper_directory(paper_id)
    
    # Save metadata to file
    with open(os.path.join(paper_dir, "metadata.json"), "w") as f:
        f.write(metadata.json())
    
    return metadata


def parse_review_text(review_text: str) -> dict:
    """Parse a review text into a dictionary for creating a ReviewSchema."""
    result = {}
    
    # Extract summary
    summary_match = re.search(r"Summary:(.*?)(?:Soundness:|$)", review_text, re.DOTALL)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()
    
    # Extract ratings
    soundness_match = re.search(r"Soundness:\s*([\d]+:\s*\w+)", review_text)
    if soundness_match:
        result["soundness"] = soundness_match.group(1).strip()
    
    presentation_match = re.search(r"Presentation:\s*([\d]+:\s*\w+)", review_text)
    if presentation_match:
        result["presentation"] = presentation_match.group(1).strip()
    
    contribution_match = re.search(r"Contribution:\s*([\d]+:\s*\w+)", review_text)
    if contribution_match:
        result["contribution"] = contribution_match.group(1).strip()
    
    # Extract strengths and weaknesses
    strengths_match = re.search(r"Strengths:(.*?)(?:Weaknesses:|$)", review_text, re.DOTALL)
    if strengths_match:
        result["strengths"] = strengths_match.group(1).strip()
    
    weaknesses_match = re.search(r"Weaknesses:(.*?)(?:Questions:|$)", review_text, re.DOTALL)
    if weaknesses_match:
        result["weaknesses"] = weaknesses_match.group(1).strip()
    
    # Extract questions/comments
    questions_match = re.search(r"Questions:(.*?)(?:Flag For Ethics Review:|$)", review_text, re.DOTALL)
    if questions_match:
        result["questions"] = questions_match.group(1).strip()
    
    # Extract ethics flag
    ethics_flag_match = re.search(r"Flag For Ethics Review:\s*(.*?)(?:\n|$)", review_text)
    if ethics_flag_match:
        result["ethics_flag"] = ethics_flag_match.group(1).strip()
    
    # Extract ethics concerns
    ethics_concerns_match = re.search(r"Details Of Ethics Concerns:(.*?)(?:Rating:|$)", review_text, re.DOTALL)
    if ethics_concerns_match:
        concerns = ethics_concerns_match.group(1).strip()
        if concerns and concerns.lower() not in ["na", "n/a", "none"]:
            result["ethics_concerns"] = concerns
    
    # Extract rating
    rating_match = re.search(r"Rating:\s*([\d]+:.*?)(?:\n|$)", review_text)
    if rating_match:
        result["rating"] = rating_match.group(1).strip()
    
    # Extract confidence
    confidence_match = re.search(r"Confidence:\s*([\d]+:.*?)(?:\n|$)", review_text)
    if confidence_match:
        result["confidence"] = confidence_match.group(1).strip()
    
    # Extract code of conduct
    coc_match = re.search(r"Code Of Conduct:\s*(Yes|No)", review_text)
    if coc_match:
        result["code_of_conduct"] = coc_match.group(1).strip() == "Yes"
    
    return result


def load_metadata(paper_id: str, base_dir: str = "data") -> Optional[PaperMetadata]:
    """Load paper metadata from file."""
    metadata_path = os.path.join(base_dir, paper_id, "metadata.json")
    if not os.path.exists(metadata_path):
        return None
    
    with open(metadata_path, "r") as f:
        metadata_json = json.load(f)
    
    return PaperMetadata.parse_obj(metadata_json)


def add_human_review(paper_id: str, review_text: str, reviewer_id: str = None) -> ReviewSchema:
    """Add a human review for a paper."""
    # Check if paper metadata exists
    metadata = load_metadata(paper_id)
    if not metadata:
        raise ValueError(f"Paper with ID {paper_id} not found. Create metadata first.")
    
    # Generate reviewer ID if not provided
    if reviewer_id is None:
        reviewer_id = str(uuid.uuid4())
    
    # Parse the review
    parsed_data = parse_review_text(review_text)
    review = ReviewSchema(**parsed_data)
    
    # Save the raw review text
    paper_dir = os.path.join("data", paper_id)
    raw_dir = os.path.join(paper_dir, "raw_reviews")
    with open(os.path.join(raw_dir, f"{reviewer_id}.txt"), "w") as f:
        f.write(review_text)
    
    # Save the parsed review
    review_dir = os.path.join(paper_dir, "human_reviews")
    with open(os.path.join(review_dir, f"{reviewer_id}.json"), "w") as f:
        f.write(review.json())
    
    return review


def add_claude_review(paper_id: str, review_text: str, model_name: str = "claude") -> ReviewSchema:
    """Add a Claude (or other model) review for a paper."""
    # Check if paper metadata exists
    metadata = load_metadata(paper_id)
    if not metadata:
        raise ValueError(f"Paper with ID {paper_id} not found. Create metadata first.")
    
    # Parse the review
    parsed_data = parse_review_text(review_text)
    review = ReviewSchema(**parsed_data)
    
    # Save the raw review text
    paper_dir = os.path.join("data", paper_id)
    raw_dir = os.path.join(paper_dir, "raw_reviews")
    with open(os.path.join(raw_dir, f"{model_name}.txt"), "w") as f:
        f.write(review_text)
    
    # Save the parsed review
    review_dir = os.path.join(paper_dir, "claude_reviews")
    with open(os.path.join(review_dir, f"{model_name}.json"), "w") as f:
        f.write(review.json())
    
    return review


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Process paper metadata and reviews")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create paper metadata command
    paper_parser = subparsers.add_parser("create-paper", help="Create paper metadata")
    paper_parser.add_argument("--openreview", required=True, help="OpenReview URL")
    paper_parser.add_argument("--pdf", required=True, help="PDF URL")
    paper_parser.add_argument("--date", required=True, help="Submission date (DD-MM-YYYY)")
    
    # Add human review command
    human_parser = subparsers.add_parser("add-human-review", help="Add a human review")
    human_parser.add_argument("--paper-id", required=True, help="Paper ID")
    human_parser.add_argument("--reviewer-id", help="Reviewer ID (optional)")
    human_parser.add_argument("--file", required=True, help="File containing review text")
    
    # Add Claude review command
    claude_parser = subparsers.add_parser("add-claude-review", help="Add a Claude review")
    claude_parser.add_argument("--paper-id", required=True, help="Paper ID")
    claude_parser.add_argument("--model", default="claude", help="Model name")
    claude_parser.add_argument("--file", required=True, help="File containing review text")
    
    args = parser.parse_args()
    
    if args.command == "create-paper":
        metadata = create_paper_metadata(args.openreview, args.pdf, args.date)
        print(f"Created metadata for paper: {metadata.paper_id}")
    
    elif args.command == "add-human-review":
        with open(args.file, "r") as f:
            review_text = f.read()
        
        review = add_human_review(args.paper_id, review_text, args.reviewer_id)
        reviewer_id = args.reviewer_id or "auto-generated ID"
        print(f"Added human review for paper {args.paper_id} from reviewer {reviewer_id}")
    
    elif args.command == "add-claude-review":
        with open(args.file, "r") as f:
            review_text = f.read()
        
        review = add_claude_review(args.paper_id, review_text, args.model)
        print(f"Added {args.model} review for paper {args.paper_id}") 
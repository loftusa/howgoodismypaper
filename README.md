# plan

Start with n=25 papers that we sample randomly from OpenReview on page 1 of the submissions (they were all submitted on sept 28)


## Part 1: scraping
For each paper, we want:
    1. the pdf of the original submission (not the updated version)
    2. a `ReviewSchema` (json object) containing the official reviews of the paper, which contains each **initial** review, before any updates, and then each reviewer's scores for soundness, presentation, contribution, rating, and confidence, as well as all the text.
    3. use (for now) anthropic's claude API. Give the API the original submission pdf and have it generate a `ReviewSchema` using the ICLR reviewer template as context.
        - nice-to-have: run these through notebookLM as a proof-of-concept

## Part 2: analysis



TODOs
- get a good scraper going
    - initially just get it manually
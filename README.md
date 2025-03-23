# plan

Start with n=25 papers that we sample randomly from OpenReview on page 1 of the submissions (they were all submitted on sept 28)


## Part 1: scraping
For each paper, we want:
    1. the pdf of the original submission (not the updated version)
    2. a `ReviewSchema` (json object) containing the official reviews of the paper, which contains each **initial** review, before any updates, and then each reviewer's scores for soundness, presentation, contribution, rating, and confidence, as well as all the text.
    3. use (for now) anthropic's claude API. Give the API the original submission pdf and have it generate a `ReviewSchema` using the ICLR reviewer template as context.
        - nice-to-have: run these through notebookLM as a proof-of-concept

## Part 2: analysis

questions:
    - how good is claude at predicting review scores?
    - how much does claude's predictions vary across papers compared to reviewers?
    - can claude predict one metric more less better than another?
    - to what extent can we change review scores with prompt engineering / prompt tuning?

things we're not doing:
    - how does the probability of a paper getting accepted change based on the review process
    - not doing a cross-model comparison, only using claude
    - we're not giving guidance on how to make a good paper review model
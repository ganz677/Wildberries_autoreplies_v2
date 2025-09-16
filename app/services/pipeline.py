from app.core.logger import logger
from . import (
    FetchNewReviewsService,
    PublishRepliesService,
    GenerateRepliesService,
)


class ReviewsPipeline:
    """
    Full cycle of work:
    1. Get fresh reviews from WB
    2. Generate responses
    3. Publish responses
    """

    def __init__(self) -> None:
        self.fetcher = FetchNewReviewsService()
        self.publisher = PublishRepliesService()
        self.replier = GenerateRepliesService()

    def run(self) -> dict[str, int]:
        logger.info("🚀 Starting reviews pipeline")

        created_reviews = self.fetcher.execute()
        logger.info("Step 1 finished: fetched %s new reviews", created_reviews)

        drafted_responses = self.replier.execute()
        logger.info("Step 2 finished: drafted %s responses", drafted_responses)

        published_responses = self.publisher.execute()
        logger.info("Step 3 finished: published %s responses", published_responses)

        summary = {
            "fetched_reviews": created_reviews,
            "drafted_responses": drafted_responses,
            "published_responses": published_responses,
        }

        logger.info("Pipeline finished: %s", summary)
        return summary

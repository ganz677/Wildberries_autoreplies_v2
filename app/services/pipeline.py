from . import (
    FetchNewReviewsService,
    PublishRepliesService,
    GenerateRepliesService
)


class ReviewsPipline:
    '''
    Full cycle of work:
    1. Get fresh reviews from WB
    2. Generate responses
    3. Publish responses
    '''
    def __init__(self) -> None:
        self.fetcher = FetchNewReviewsService()
        self.publisher = PublishRepliesService()
        self.replier = GenerateRepliesService()

    def run(self) -> dict[str, int]:
        created_reviews = self.fetcher.execute()
        drafted_responses = self.replier.execute()
        published_responses = self.publisher.execute()

        return {
            'fetched_reviews': created_reviews,
            'drafted_responses': drafted_responses,
            'published_responses': published_responses
        }
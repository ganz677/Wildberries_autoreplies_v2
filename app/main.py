from .services import ReviewsPipeline

if __name__ == '__main__':
    pipeline = ReviewsPipeline()
    result = pipeline.run()
    print(f'Pipeline finished: {result}')

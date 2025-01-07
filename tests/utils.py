import requests

# Mock Kinesis input
class AsyncIterator:
    def __init__(self, seq):
        self.iter = iter(seq)
    def __aiter__(self):
        return self
    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration
    async def close(self):
        return None

def list_index_contents(index):
    url = f"http://localhost:9200/{index}/_search"
    query = '{"query": {"match_all": {}},  "size": "25"}'
    print(requests.get(requestURL,
                 json=query,
                 headers={'content-type': 'application/json'}).text)

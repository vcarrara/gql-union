from promise import Promise
from promise.dataloader import DataLoader
from requests import retrieve_multiple_news, retrieve_multiple_tags


class NewsLoader(DataLoader):
    def batch_load_fn(self, keys):
        return Promise.resolve(retrieve_multiple_news(keys))


class TagLoader(DataLoader):
    def batch_load_fn(self, keys):
        return Promise.resolve(retrieve_multiple_tags(keys))

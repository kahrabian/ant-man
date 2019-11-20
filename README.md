# ant-man

This projects aims to provide toolkits for crawling data from [GitHub API v3](https://developer.github.com/v3/).

## Crawlers

Currently there are two crawlers available in this toolkit, namely for `topic` and `issues` APIs. Each crawler needs a configuration file which is located at `resources/config/crawler`. Finally, an example usage of the toolkit is available in `main.py`.

In the following subsections we will provide examples of using each crawler.

### Topic Crawler

```python
from src.crawler.topic import TopicCrawler
TopicCrawler().run()
```

### Issue Crawler

```python
from src.crawler.issue import IssueCrawler
IssueCrawler().run()
```

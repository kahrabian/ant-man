# ant-man

This projects aims to provide toolkits for crawling data from [GitHub API v3](https://developer.github.com/v3/).

## Crawlers

Currently the following API crawlers are available:

- [x] [Topic](https://developer.github.com/v3/search/#search-topics)
- [x] [Issues](https://developer.github.com/v3/issues/)
- [x] [Issues Comments](https://developer.github.com/v3/issues/comments/)

Each crawler only works with the outputs of other crawlers from this toolkit. Thus, you should consider building a pipeline of tasks while using this toolkit!

### How to use

```python
import sys
from src.crawler import TopicCrawler

sys.setrecursionlimit(10000)
TopicCrawler().run()
```

#### From the command line

```bash
python main.py
```

#### Configuration

Each crawler needs a configuration file named `{crawler_api}.ini` located at `./resources/config/crawler`. For each cralwer, sample configurations has been provided in this directory. Note that the `root` section will be always ignored during runtime.

```ini
[root]
name = query name
q = search query
sort = sort attribute
order = desc or asc

[java]
name = java
q = language:java+stars:>=1000+is:public
sort = stars
order = desc

[python]
name = python
q = language:python+stars:>=100+is:public
sort = stars
order = desc
```


### Dependecies

```bash
pip install requests
```

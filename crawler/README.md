# The crawler application

## Structure

This is the main part of this project and it consist of a django project with multiple modules:
- `crawler.archiving`, part of the crawler responsible of archiving article on external services as well as detecting 404 on notfound_only tagged articles.
- `crawler.core`, the core component of the crawler. It holds central models like Article and Feed. 
- `crawler.scraping`, part responsible of parsing feeds & detecting article URLs & parse article preservation tags.
- `crawler.storing`, app responsible of downloading, process and store article resources.


## How to run tests
Tests relies on django testing framework, to run them simply run:
```sh
$ ./manage.sh test
```

## Check which part are covered or not
The project is parametered to use `coverage` to check how tests cover our code base. To check which part are covered or not check `.coveragerc`.
To see which lines are actually covered you need to generate an HTML coverage package then consult it:
```
$ ./manage.sh test --cover-html
> test output
$ firefox cover/index.html
```



# vertx-eventbus-python
[![Join the chat at https://gitter.im/vertx-eventbus-python/community](https://badges.gitter.im/vertx-eventbus-python/community.svg)](https://gitter.im/vertx-eventbus-python/community?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
[![Travis (.org)](https://img.shields.io/travis/rc-dukes/vertx-eventbus-python.svg)](https://travis-ci.org/rc-dukes/vertx-eventbus-python)
[![GitHub issues](https://img.shields.io/github/issues/rc-dukes/vertx-eventbus-python.svg)](https://github.com/rc-dukes/vertx-eventbus-python/issues)
[![GitHub issues](https://img.shields.io/github/issues-closed/rc-dukes/vertx-eventbus-python.svg)](https://github.com/rc-dukes/vertx-eventbus-python/issues/?q=is%3Aissue+is%3Aclosed)
[![GitHub](https://img.shields.io/github/license/rc-dukes/vertx-eventbus-python.svg)](https://en.wikipedia.org/wiki/MIT_License)
[![BITPlan](http://wiki.bitplan.com/images/wiki/thumb/3/38/BITPlanLogoFontLessTransparent.png/198px-BITPlanLogoFontLessTransparent.png)](http://www.bitplan.com)

Python vertx eventbus bridge

## State of project
This project was not forked but copied to make it self-contained on 2020-01-30.
At this time the code is not stable yet and tests fail - please stay tuned ...

## Documentation
[Wiki](http://wiki.bitplan.com/index.php/Vertx-eventbus-python)

## Test

### Java
```
./test --java

...
Results :

Tests run: 3, Failures: 0, Errors: 0, Skipped: 0
```

### Python
```
./test --python
...
Ran 3 tests in 0.004s

FAILED (failures=1, errors=1)
```

## History
The code originally resided in [vert-x3/vertx-eventbus-bridge-clients](https://github.com/vert-x3/vertx-eventbus-bridge-clients) repository. Unfortunately it was not very self-contained and testable there

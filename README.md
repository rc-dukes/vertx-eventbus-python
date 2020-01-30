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

### TestEnviroment
The tests below have been run succesfully in the following environments:
#### MacOS
```
mvn -version
Apache Maven 3.6.3 (cecedd343002696d0abb50b32b541b8a6ba2883f)
Maven home: /opt/local/share/java/maven3
Java version: 1.8.0_152, vendor: Oracle Corporation, runtime: /Library/Java/JavaVirtualMachines/jdk1.8.0_152.jdk/Contents/Home/jre
Default locale: de_DE, platform encoding: UTF-8
OS name: "mac os x", version: "10.13.6", arch: "x86_64", family: "mac"

python3 --version
Python 3.7.6
```

### Java
```
./test --java

...
Results :

Tests run: 4, Failures: 0, Errors: 0, Skipped: 0
```

### Python
For the python tests to be succesful you might want to start the echoVerticle manually first with
```
java/run
```
and then start the tests in another terminal window:
```
./test --python
...
Ran 3 tests in 0.004s

FAILED (failures=1, errors=1)
```

### all
```
./test --all
```

this test will try to run the steps
1. java tests
2. start echoVerticle
3. python tests

automatically in sequence


## History
The code originally resided in [vert-x3/vertx-eventbus-bridge-clients](https://github.com/vert-x3/vertx-eventbus-bridge-clients) repository. Unfortunately it was not very self-contained and testable there

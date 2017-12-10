# Tests

Functional tests and load/performance tests can be found inside this directory. For each test you have to start Flask server before running them.

## Functional Tests

Functional tests implemented with Katalon IDE, you can use standard Java (>= 8) and WebDriver library to start tests. Functional tests checks every button, page and link on pages of channelx.

## Performance/Load Tests

This tests implemented with Apache JMeter program. Open load_test.jmx file with JMeter after you start Flask server. It will create 100 users on different threads. There are two load tests, first for non-logged in pages (index, terms, signup etc.) and second for logging-in, panel pages. Logging-in page also cover SQL load test. 100 users sends request for 10 seconds for every page and this operation done for 20 times for each test.

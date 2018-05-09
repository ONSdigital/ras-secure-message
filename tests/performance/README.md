## Performance testing usage guide


### Locust

- Install locust, `make build` should do it, but if it's not in the pipfile then `pipenv install locustio`
- `pipenv run locust -f /path/to/locustfile.py` - this will start a server on `http://localhost:8089` that uses the specified locustfile
-  Go to the above url, specify the number of users and the spawn rate

#### create-messages script guide
To create a number of messages quickly, there is a create-messages.py script.
The problem with this script is that it needs correct ids for it to work.  To get these ids,
follow the steps below.

- Run acceptance tests to get test data into response-operations-ui
- Add logging to response-operations-ui to log out the jwt (inside `get_thread_list`)
 and the message payload in order to get required data (inside `_post_new_message`)
- Send a message to a respondent using the reporting units functionality.  The acceptance tests
ran previously should have some reporting units set up for this.  After sending the message, you will need to copy the following details from it into the create-messages.py file:
  - msg_from
  - msg_to
  - ru_id
  - survey
- Finally, run the script.

### Function testing guide

As well as testing how many concurrent users can use the service, it can also be useful
to put timers around functions to see how long they take.  This way, we can identify where the
bottlenecks in the code are.

```python
import time
start = time.time()
# Your function here
end = time.time()
logger.info("Time taken to complete <function name>", time=end-start)```

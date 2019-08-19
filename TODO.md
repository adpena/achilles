Improve documentation w/ installation instructions, how to use, etc. Update with instructions on how to use map API and imap API.

Improve inline documentation.

Fix imap implementation:
1) doesn't work if first result received doesn't include "ARGS_COUNTER": 0
* Weird behavior if this follows after an imap_unordered loop, especially with large chunk size.

Change how OBJECT response mode's final response is calculated; do it using Queues in the achilles_controller instead of in the achilles_server.

Change yield function so generators are not expected to yield args_counter..at least consider...

---

Ability for multiple achilles_controllers to connect to the achilles_server and run multiple jobs at the same time.

Add unit tests.

Examples folder:
1) Add example that performs word count on arbitrary text.

Encryption/authentication/security concerns (create SSH implementation using TwistedConch).

Cythonize - how to automate for each platform in setup.py.

Rustify/Gopherize any remaining bottlenecks.

Implement fault tolerance.

Implement error_callback to give the developer more insight into what's happening in the nodes without having to check their terminals.

How to implement modules and other ideas from pp?

Identify blocks of duplicate code and pull them into functions (multiple response modes, proceedWithJob/lineReceiver).

Implement and test SQLITE response mode - is this still relevant?

Delete unnecessary comments.

Resolve naming conflicts between node/worker/etc. for clarity of mental model.

Resolve syntax issues (snake_case where it should be camelCase, vice versa)
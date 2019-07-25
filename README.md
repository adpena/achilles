# achilles
Extremely accessible distributed/parallel computing (B.Y.O.B. - Build Your Own Beowulf) in modern Python based on:
* `Twisted`;
* `dill`;
* `multiprocess` (a fork of `multiprocessing` that uses `dill` as its serializer); and, 
* lessons learned from studying `Hadoop`, `Apache Spark`, `Kubernetes`, `Apache Arrow`, `Parallel Python`, `Ray`, `Jug`, `Pathos`, `Disco`, `SCOOP`, `Cluster-Workers` and the questions asked regarding these projects on StackOverflow.

The goal of the `achilles project` is to drastically reduce the barriers to entry for developers to use all of the computational power available on their networks by providing an accessible, highly flexible framework for building distributed/parallel computing applications with as little configuration and prior knowledge as possible.

As `achilles` continues to be actively developed, the project will be designed in alignment with our FOUR DEMANDS:
 * `achilles` must be simple to use;
 * `achilles` must 'just work' at all scales, from running all of the components on an individual's laptop to deployment across thousands of `achilles_node`s;
 * `achilles` must be scalable and accommodate 'big data' workloads (i.e. files too large to open in memory on a single machine);
 * `achilles` should be fast as hell and regularly benchmarked against alternative solutions; and,
 * `achilles` must be SECURE. Currently, `achilles` is not suitable for deployment outside of `localhost`. We are currently working on an SSH implementation using `TwistedConch`.

Consists of:
 * `achilles_server.py`
     * Runs a Twisted TCP server (`lineReceiver` so that large packets aren't truncated) listening at the endpoint described in the `.env` configuration file. Establishes and maintains persistent connections with `achilles_node`(s), distributes computations among them at the instruction of the `achilles_controller`, and sends the result(s) to the `achilles_controller` in the `response_mode` specified by the developer.
 * `achilles_node.py`
     * Connect to the `achilles_server` and receive ID assignment. Wait for a job to be started, receive a function over the wire, receive an argument over the wire, perform the function on the argument, return the result to the server and then wait for more arguments - keep feeding the server results/receiving new arguments until all arguments have been exhausted (hungry consumer, forceful feeder).
 * `achilles_controller.py`
     * Connect to the `achilles_server` and instruct it which function should be performed against which arguments in the specified `response_mode`. Verify the job and wait for the results to be returned - `achilles_server` and its `achilles_node`(s) will do the rest.
     * Available commands in `achilles_controller` command interface (`map` API also exposed - see below for details/examples):
        * `achilles_compute`, `cluster_status`, `kill_cluster`, `help`
 
Configuration files:
 * `achilles_config.yaml`
     * Use `pyYaml` to load the configuration file for a job into the `achilles_controller` if you decide to use the `command_interface()` CLI. See below for additional information on how to structure this file.
     * Args may be defined in this file.
 * `achilles_function.py`
     * `achilles_function()` is serialized using `dill` and distributed to all connected clients as a part of the `startJob()` handshake initiated after the `achilles_controller` verifies the commencement of a job.
     * `achilles_args()` and `achilles_callback()` may also be defined in this file.
     * Can also be defined dynamically along with `achilles_args()` and `achilles_callback()`. See `Usage` for details/examples.
 * `.env`
     * Use `python-dotenv` to load the local file into the system's environmental variables for configuration and authentication.
     * Basic security precaution. To-do: explore encryption.
 
### Installation
`pip install --upgrade achilles`

### Usage
Deploy `achilles_server`:
1) `from achilles.lineReceiver.achilles_server import runAchillesServer`
2) `runAchillesServer()` -> run an `achilles_server` using the specified HOST and PORT in the package's `.env` file (generate one if it does not exist).

Deploy `achilles_node`(s):
1) `from achilles.lineReceiver.achilles_node import runAchillesNode`
2) `runAchillesNode()` -> run an `achilles_node` that connects to the specified HOST and PORT in the package's `.env` file (generate one if it does not exist).                          

Either deploy `achilles_controller` or use `map` API in your own scripts:
1) `from achilles.lineReceiver.achilles_node import runAchillesNode`
2) `runAchillesNode()` -> run an `achilles_controller` that connects to the specified HOST and PORT in the package's `.env` file (generate one if it does not exist).
3) `runAchillesNode()` automatically calls `command_interface()` and presents the user with an easy-to-use CLI.

OR...

1) XXXX

`achilles` is in the early stages of active development and your suggestions/contributions are kindly welcomed. `achilles` is written and maintained by Alejandro Peña. Email me at adpena<3gmail.com.

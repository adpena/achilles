# cortex
Extremely accessible distributed/parallel computing (BYOB - Build Your Own Beowulf) in modern Python based on:
* Twisted;
* cloudpickle;
* multiprocessing; and, 
* lessons learned from studying Hadoop, Apache Spark, Apache Arrow, Parallel Python, Ray, Jug, Pathos, Disco, SCOOP, Cluster-Workers and the questions asked regarding these projects on StackOverflow.

The goal of the cortex framework is to drastically reduce the barriers to entry for developers to use all of the computational power available on their networks and provide engingeers with an accessible, highly flexible framework for building distributed/parallel computing into their applications applications.

As cortex continues to be actively developed, the project will continue to be designed in alignment with our four demands for the project:
 * `cortex` must be simple to use;
 * `cortex` must 'just work' at all scales, from running all of the components on an individual's laptop to running on powerful clusters in distributed systems;
 * `cortex` must be scalable and accommodate 'big data' workloads (i.e. files too large to open in memory on a single machine);
 * `cortex` should be fast as hell and regularly benchmarked against alternative solutions; and,
 * `cortex` must be SECURE. Currently, cortex is not suitable for deployment outside of `localhost`. We are currently working on an SSH implementation.

Consists of:
 * `cortex_server.py`
     * Runs a Twisted TCP server listening at the endpoint described in the `.env` configuration file. Establishes and maintains persistent connections with multiple `cortex_nodes` (potentially running across numerous machines), distributes computations among them at the instruction of the `cortex`, and sends the result(s) to the `cortex` in the `response_mode` specified in `cortex_compute()`.
 * `cortex_node.py`
     * Connect to the `cortex_server` and receive ID assignment. Wait for a job to be started, receive a function over the wire, receive an argument over the wire and then keep feeding the server results/receiving new arguments until all arguments are exhausted.
 * `cortex.py`
     * Connect to the `cortex_server` and instruct it which function to perform against which arguments with which `response_mode`. Verify the job and wait for the results to be returned - `cortex_server` will do the rest.
     * Available commands in `cortex` command interface:
        * `cortex_compute`, `cluster_status`, `kill_cluster`, `help`
 
 Configuration files:
 * `cortex_config.yaml`
     * Use `pyYaml` to load the configuration file for a job into `cortex.py`. See below for additional information on how to structure this file.
 * `cortex_function.py`
     * `cortex_function()` is cloudpickled and distributed to all connected clients as a part of the `self.startJob()` handshake initiated after `cortex.py` verifies the commencement of a job.
 * `.env`
     * Use `python-dotenv` to load the local file into the system's environmental variables for configuration and authentication.
     * Basic security precaution. To-do: explore encryption.
 
Cortex is in active development and your suggestions are kindly welcomed. Cortex is written and maintained by Alejandro Peña. Email me at adpena<3gmail.com.

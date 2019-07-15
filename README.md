# cortex
Extremely accessible distributed computing (BYOB - Build Your Own Beowulf) in modern Python based on:
* Twisted;
* cloudpickle;
* multiprocessing; and, 
* lessons learned from studying Hadoop, Apache Spark, Apache Arrow, Parallel Python, Ray, Jug, Disco, Cluster-Workers and more.

The goal of this project is to eliminate the barriers to entry for developers to use all of the computational power available on their networks.

Consists of:
 * `cortex_server.py`
     * Runs a Twisted TCP server listening at the endpoint described in the `.env` configuration file. Establishes and maintains persistent connections with multiple `cortex_nodes` running across numerous machines, distributes computations among them at the instruction of the `cortex`.
 * `cortex_node.py`
     * Connect to the `cortex_server` and receive ID assignment. Wait for a job to be started, receive a function over the wire, receive an argument over the wire and then keep feeding cycle until arguments are exhausted.
 * `cortex.py`
     * Connect to the `cortex_server` and instruct it which function to perform against which arguments. Verify the job and wait for the results to be returned - `cortex_server` will do the rest.
 
 Configuration files:
 * `cortex_config.yaml`
     * Use `pyYaml` to load the configuration file for a job into `cortex.py`. See below for additional information on how to structure this file.
 * `cortex_function.py`
     * `cortex_function()` is cloudpickled and distributed to all connected clients as a part of the `self.startJob()` handshake initiated after `cortex.py` verifies the commencement of a job.
 * `.env`
     * Use `python-dotenv` to load the local file into the system's environmental variables for configuration and authentication.
     * Basic security precaution. To-do: explore encryption.
 
 This project is made available under the MIT license. Cortex is in active development and your suggestions are kindly welcomed.
# `achilles`
Distributed/parallel computing in modern Python based on the `multiprocessing.Pool` API (`map`, `imap`, `imap_unordered`).

## What is it?
The purpose of `achilles` is to make distributed/parallel computing as easy as possible by limiting the required configuration, hiding the details (server/node/controller architecture) and exposing a simple interface based on the popular `multiprocessing.Pool` API.

> `achilles` provides developers with entry-level capabilities for concurrency across a network of machines (see PEP 372 on the intent behind adding `multiprocessing` to the standard library -> https://www.python.org/dev/peps/pep-0371/) using a server/node/controller architecture.

The `achilles_server`, `achilles_node` and `achilles_controller` are designed to run cross-platform/cross-architecture. The server/node/controller may be hosted on a single machine (for development) or deployed across heterogeneous resources.

`achilles` is comparable to excellent Python packages like `pathos/pyina`, `Parallel Python` and `SCOOP`, but different in certain ways:
- Designed for developers familiar with the `multiprocessing` module in the standard library with simplicity and ease of use in mind.
- In addition to the blocking `map` API which requires that developers wait for all computation to be finished before accessing results (common in such packages), `imap`/`imap_unordered` allow developers to process results as they are returned to the `achilles_controller` by the `achilles_server`.
- `achilles` allows for composable scalability and novel design patterns as:
    - Lists (including list comprehensions), lists of lists and generator functions (as first-class object - generator expressions will not work as generators cannot be serialized by `pickle`/`dill`) are accepted as arguments.
        - TIP: Use generator functions together with `imap` or `imap_unordered` to perform distributed computation on arbitrarily large data.
    - The `dill` serializer is used to transfer data between the server/node/controller and `multiprocess` (fork of `multiprocessing` that uses the `dill` serializer instead of `pickle`) is used to perform `Pool.map` on the `achilles_nodes`, so developers are freed from some of the constraints of the `pickle` serializer.
    <br/>

### Install
`pip install achilles`

### Quick Start
Start an `achilles_server` listening for connections from `achilles_nodes` at a certain endpoint specified as arguments or in an `.env` file in the `achilles` package's directory.

Then simply import `map`, `imap`, and/or `imap_unordered` from `achilles_main` and use them dynamically in your own code (under the hood they create and close `achilles_controller`s).

`map`, `imap` and `imap_unordered` will distribute your function to each `achilles_node` connected to the `achilles_server`. Then, the `achilles_server` will distribute arguments to each `achilles_node` (load balanced and made into a list of arguments if the arguments' type is not already a list) which will then perform your function on the arguments using `multiprocess.Pool.map`.

Each `achilles_node` finishes its work, returns the results to the `achilles_server` and waits to receive another argument. This process is repeated until all of the arguments have been exhausted.

1) `runAchillesServer(host=None, port=None, username=None, secret_key=None)` -> run on your local machine or on another machine connected to your network

    `in:`
    ```python
    from achilles.lineReceiver.achilles_server import runAchillesServer
    
   # host = IP address of the achilles_server
   # port = port to listen on for connections from achilles_nodes (must be an int)
   # username, secret_key used for authentication with achilles_controller
    
   runAchillesServer(host='127.0.0.1', port=9999, username='foo', secret_key='bar')
   ```
   
   ```python
      
   # OR generate an .env file with a default configuration so that
   # arguments are no longer required to runAchillesServer()
   
   # use genConfig() to overwrite

   from achilles.lineReceiver.achilles_server import runAchillesServer, genConfig
   
   genConfig(host='127.0.0.1', port=9999, username='foo', secret_key='bar')
   runAchillesServer()
    ```
    <br/>
    
    `out:`
    ```
    ALERT: achilles_server initiated at 127.0.0.1:9999
    Listening for connections...
    ```

2) `runAchillesNode(host=None, port=None)` -> run on your local machine or on another machine connected to your network
    
    `in:`
    ```python
    from achilles.lineReceiver.achilles_node import runAchillesNode
   
   # genConfig() is also available in achilles_node, but only expects host and port arguments
    
    runAchillesNode(host='127.0.0.1', port=9999)
    ```
    <br/>   
    
    `out:`
    ```
    GREETING: Welcome! There are currently 1 open connections.
    
    Connected to achilles_server running at 127.0.0.1:9999
    CLIENT_ID: 0
    ```
        
3) Examples of how to use the 3 most commonly used `multiprocessing.Pool` methods in `achilles`:
    <br/>
    >> Note: `map`, `imap` and `imap_unordered` currently accept lists, lists of lists, and generator functions as `achilles_args`.
                                                         
    >> Also note:  if there isn't already a `.env` configuration file in the `achilles` package directory, must use `genConfig(host, port, username, secret_key)` before using or include `host`, `port`, `username` and `secret_key` as arguments when using `map`, `imap`, `imap_unordered`.
    
    1) `map(func, args, callback=None, chunksize=1, host=None, port=None, username=None, secret_key=None)`<br/><br/>
        `in:`
        ```python
       from achilles.lineReceiver.achilles_main import map
       
       def achilles_function(arg):
           return arg ** 2
       
       def achilles_callback(result):
           return result ** 2
       
       if __name__ == "__main__":
           results = map(achilles_function, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], achilles_callback, chunksize=1)
           print(results)
       ```
       <br/>
       
       `out:`
       ```
       ALERT: Connection to achilles_server at 127.0.0.1:9999 and authentication successful.
       
       [[1, 16, 81, 256, 625, 1296, 2401, 4096], [6561, 10000]]
       ```
       
   2) `imap(func, args, callback=None, chunksize=1, host=None, port=None, username=None, secret_key=None)`<br/><br/>
        `in:`
        ```python
        from achilles.lineReceiver.achilles_main import imap
      
      def achilles_function(arg):
          return arg ** 2 
      
      def achilles_callback(result):
          return result ** 2
      
      if __name__ == "__main__":
          for result in imap(achilles_function, [1,2,3,4,5,6,7,8,9,10], achilles_callback, chunksize=1):
              print(result)
        ```
      <br/>
      
      `out:`
      ``` 
      ALERT: Connection to achilles_server at 127.0.0.1:9999 and authentication successful.

      {'ARGS_COUNTER': 0, 'RESULT': [1, 16, 81, 256, 625, 1296, 2401, 4096]}
      {'ARGS_COUNTER': 8, 'RESULT': [6561, 10000]}
      ```

     3) `imap_unordered(func, args, callback=None, chunksize=1, host=None, port=None, username=None, secret_key=None)`<br/><br/>
     `in:`
        ```python
        from achilles.lineReceiver.achilles_main import imap_unordered
        
        def achilles_function(arg):
            return arg ** 2
        
        def achilles_callback(result):
            return result ** 2
      
        if __name__ == "__main__":
            for result in imap_unordered(achilles_function, [1,2,3,4,5,6,7,8,9,10], achilles_callback, chunksize=1):
                print(result)
        ```
        <br/>
        
        `out:`
        ``` 
        ALERT: Connection to achilles_server at 127.0.0.1:9999 and authentication successful.

        {'ARGS_COUNTER': 8, 'RESULT': [6561, 10000]}
        {'ARGS_COUNTER': 0, 'RESULT': [1, 16, 81, 256, 625, 1296, 2401, 4096]}
        ```

## How `achilles` works 

### Under the hood
- `Twisted`
    - An event-driven networking engine written in Python and MIT licensed.
- `dill`
    - `dill` extends Python’s `pickle` module for serializing and de-serializing Python objects to the majority of the built-in Python types.
- `multiprocess`
    - multiprocess is a fork of multiprocessing that uses `dill` instead of `pickle` for serialization. `multiprocessing` is a package for the Python language which supports the spawning of processes using the API of the standard library’s threading module.

### Examples
See the `examples` directory for tutorials on various use cases, including:
- Square numbers/run multiple jobs sequentially
- Word count (TO DO)

### How to kill cluster
```python
from achilles.lineReceiver.achilles_main import killCluster

# simply use the killCluster() command and verify your intent at the prompt
# killCluster() will search for an .env configuration file in the achilles package's directory

# if it does not exist, specify host, port, username and secret_key as arguments
# a command is sent to all connected achilles_nodes to stop the Twisted reactor and exit() the process

# optionally, you can pass command_verified=True to proceed directly with killing the cluster

killCluster(command_verified=True)
```

### Caveats/Things to know
- `achilles_node`s use all of the CPU cores available on the host machine to perform `multiprocess.Pool.map` (`pool = multiprocess.Pool(multiprocess.cpu_count())`).
- `achilles` leaves it up to the developer to ensure that the correct packages are installed on `achilles_node`s to perform the function distributed by the `achilles_server` on behalf of the `achilles_controller`. Current recommended solution is to SSH into each machine and `pip install` a `requirements.txt` file.
- All import statements required by the developer's function, arguments and callback must be included in the definition of the function.
- The `achilles_server` is currently designed to handle one job at a time. For more complicated projects, I highly recommend checking out `Dask` (especially `dask.distributed`) and learning more about directed acyclic graphs (DAGs).
- `callback_error` argument has yet to be implemented, so detailed information regarding errors can only be gleaned from the interpreter used to launch the `achilles_server`, `achilles_node` or `achilles_controller`. Deploying the server/node/controller on a single machine is recommended for development.
- `achilles` performs load balancing at runtime and assigns `achilles_node`s arguments by `cpu_count` * `chunksize`.
    - Default `chunksize` is 1.
    - Increasing the `chunksize` is an easy way to speed up computation and reduce the amount of time spent transferring data between the server/node/controller.
- If your arguments are already lists, the `chunksize` argument is not used.
    - Instead, one argument/list will be distributed to the connected `achilles_node`s at a time.
- If your arguments are load balanced, the results returned are contained in lists of length `achilles_node's cpu_count` *  `chunksize`.
    - `map`:
        - Final result of `map` is an ordered list of load balanced lists (the final result is not flattened).
    - `imap`:
        - Results are returned as computation is finished in dictionaries that include the following keys:
            - `RESULT`: load balanced list of results.
            - `ARGS_COUNTER`: index of first argument (0-indexed).
         - Results are ordered.
             - The first result will correspond to the next result after the last result in the preceding results packet's list of results.
             - Likely to be slower than `immap_unordered` due to `achilles_controller` yielding ordered results. `imap_unordered` (see below) yields results as they are received, while `imap` yields results as they are received only if the argument's `ARGS_COUNTER` is expected based on the length of the `RESULT` list in the preceding results packet. Otherwise, a `result_buffer` is checked for the results packet with the expected `ARGS_COUNTER` and the current results packet is added to the `result_buffer`. If it is not found, `achilles_controller` will not yield results until a results packet with the expected `ARGS_COUNTER` is received.
    - `imap_unordered`:
        - Results are returned as computation is finished in dictionaries that include the following keys:
            - `RESULT`: load balanced list of results.
            - `ARGS_COUNTER`: index of first argument (0-indexed).
         - Results are not ordered.
             - Results packets are yielded as they are received (after any `achilles_callback` has been performed on it).
             - Fastest way of consuming results received from the `achilles_server`.
             

<hr/>

`achilles` is in the early stages of active development and your suggestions/contributions are kindly welcomed.

`achilles` is written and maintained by Alejandro Peña. Email me at adpena at gmail dot com.

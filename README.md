# `achilles`
Distributed/parallel computing in modern Python based on the `multiprocessing.Pool` API (`map`, `imap`, `imap_unordered`).

### What is it?
`achilles` is built using a server/node/controller architecture. The `achilles_server`, `achilles_node` and `achilles_controller` are designed to run cross-platform/cross-architecture and may be hosted on a single machine (for development) or deployed across heterogeneous resources.

`achilles` is comparable to excellent Python packages like `pathos/pyina`, `Parallel Python` and `SCOOP`. Similar in some ways, different in others:
- Designed for developers familiar with the `multiprocessing` module in the standard library with simplicity and ease of use in mind.
- In addition to the blocking `map` API that requires  developers to wait for all computation to be finished before accessing results (common in such packages), `imap`/`imap_unordered` allow developers to process results as they are returned to the `achilles_controller` by the `achilles_server`.
- `achilles` allows for composable scalability and novel design patterns as:
    - Lists, lists of lists and generator functions are accepted as arguments.
        - TIP: Use generator functions together with `imap` or `imap_unordered` to perform distributed computation on arbitrarily large data.
    - The `dill` serializer is used to transfer data between the server/node/controller and `multiprocess` (fork of `multiprocessing` that uses the `dill` serializer instead of `pickle`) is used to perform `Pool.map` on the `achilles_nodes`, so developers are  freed from some of the constraints of the `pickle` serializer.
    <br/>

#### Install
`pip install achilles`

#### Quick Start
Start an `achilles_server` listening for connections from `achilles_nodes` at a certain endpoint specified as arguments or in an `.env` file in the `achilles` package's directory.

Then simply import `map`, `imap`, and/or `imap_unordered` from `achilles_main` and use them dynamically in your own code.

`map`, `imap` and `imap_unordered` will distribute your function to each `achilles_node` connected to the `achilles_server`. Then, the `achilles_server` will distribute arguments to each `achilles_node` (load balanced if the arguments' type is not already a list) which will then perform your function on the arguments using `multiprocess.Pool.map`.

Each `achilles_node` finishes its work, returns the results to the `achilles_server` and waits to receive another argument from it. This process is repeated until all of the arguments have been exhausted.

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
    <br/>

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
    <br/>       
        
3) Examples of how to use the 3 most commonly used `multiprocessing.Pool` methods in `achilles`:
    <br/>
    >> Note: `map`, `imap` and `imap_unordered` currently accept lists, lists of lists, and generator functions as `achilles_args`.
    
    >> Generator functions must yield an `args_counter` with each `arg` (i.e. `yield args_counter, arg` -> see `examples\square_nums` directory for an example of how to use).
                                                         
    >> Also note:  if there isn't already a `.env` configuration file in the `achilles` package directory, must use `genConfig(host, port, username, secret_key)` before using or include `host`, `port`, `username` and `secret_key` as arguments when using `map`, `imap`, `imap_unordered`.
    
    1) `map(achilles_function, achilles_args, achilles_callback=None, chunk_size=1, host=None, port=None, username=None, secret_key=None)`<br/><br/>
        `in:`
        ```python
       from achilles.lineReceiver.achilles_main import map
       
       def achilles_function(arg):
           return arg ** 2
       
       def achilles_callback(result):
           result_data = result["RESULT"]
           for i in range(len(result_data)):
               result_data[i] = result_data[i] ** 2
           return result
       
       if __name__ == "__main__":
           results = map(achilles_function, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10], achilles_callback, chunk_size=1)
           print(results)
       ```
       <br/>
       
       `out:`
       ```
       ALERT: Connection to achilles_server at 127.0.0.1:9999 and authentication successful.
       
       [[1, 16, 81, 256, 625, 1296, 2401, 4096], [6561, 10000]]
       ```
        <br/>
   2) `imap(achilles_function, achilles_args, achilles_callback=None, chunk_size=1, host=None, port=None, username=None, secret_key=None)`<br/><br/>
        `in:`
        ```python
        from achilles.lineReceiver.achilles_main import imap
      
      def achilles_function(arg):
          return arg ** 2 
      
      def achilles_callback(result):
          result_data = result["RESULT"]
          for i in range(len(result_data)):
              result_data[i] = result_data[i] ** 2
          return result
      
      if __name__ == "__main__":
          for result in imap(achilles_function, [1,2,3,4,5,6,7,8,9,10], achilles_callback, chunk_size=1):
              print(result)
        ```
      <br/>
      
      `out:`
      ``` 
      ALERT: Connection to achilles_server at 127.0.0.1:9999 and authentication successful.

      {'ARGS_COUNTER': 0, 'RESULT': [1, 16, 81, 256, 625, 1296, 2401, 4096]}
      {'ARGS_COUNTER': 8, 'RESULT': [6561, 10000]}
      ```
      <br/>

     3) `imap_unordered(achilles_function, achilles_args, achilles_callback=None, chunk_size=1, host=None, port=None, username=None, secret_key=None)`<br/><br/>
     `in:`
        ```python
        from achilles.lineReceiver.achilles_main import imap_unordered
        
        def achilles_function(arg):
            return arg ** 2
        
        def achilles_callback(result):
            result_data = result["RESULT"]
            for i in range(len(result_data)):
                result_data[i] = result_data[i] ** 2
            return result
      
        if __name__ == "__main__":
            for result in imap_unordered(achilles_function, [1,2,3,4,5,6,7,8,9,10], achilles_callback, chunk_size=1):
                print(result)
        ```
        <br/>
        
        `out:`
        ``` 
        ALERT: Connection to achilles_server at 127.0.0.1:9999 and authentication successful.

        {'ARGS_COUNTER': 8, 'RESULT': [6561, 10000]}
        {'ARGS_COUNTER': 0, 'RESULT': [1, 16, 81, 256, 625, 1296, 2401, 4096]}
        ```
        <br/>

### How `achilles` works

#### Under the hood
- `Twisted`
    - An event-driven networking engine written in Python and MIT licensed.
- `dill`
    - `dill` extends Python’s `pickle` module for serializing and de-serializing Python objects to the majority of the built-in Python types.
- `multiprocess`
    - multiprocess is a fork of multiprocessing that uses `dill` instead of `pickle` for serialization. `multiprocessing` is a package for the Python language which supports the spawning of processes using the API of the standard library’s threading module.

#### Examples
See the `examples` directory for tutorials on various use cases, including:
- Square numbers/run multiple jobs sequentially
- Word count (TO DO)

#### How to kill cluster
```python
from achilles.lineReceiver.achilles_main import killCluster

# simply use the killCluster() command and verify your intent at the prompt
# killCluster() will search for an .env configuration file in the achilles package's directory
# if it does not exist, specify host, port, username and secret_key as arguments

killCluster()
```

#### Caveats/Things to know
- `achilles_node`s use all of the CPU cores available on the host machine to perform `multiprocess.Pool.map` (`pool = multiprocess.Pool(multiprocess.cpu_count()`).
- The `achilles_server` is designed to handle one job at a time for now (TO DO: add fault tolerance and ability to handle multiple jobs).
- `achilles_callback_error` has yet to be implemented, so detailed information regarding errors can only be gleaned from the interpreter used to launch the `achilles_server`, `achilles_node` or `achilles_controller`. Deploying the server/node/controller on a single machine is recommended for development.
- Generator functions used to define args must yield an `args_counter` along with the `arg` (i.e. `yield args_counter, arg` -> see `examples\square_nums`) in the current version of `achilles`.
- `achilles` performs load balancing at runtime and assigns `achilles_node`s arguments by `cpu_count` * `chunk_size`.
    - Default `chunk_size` is 1.
    - Increasing the `chunk_size` is an easy way to speed up computation and reduce the amount of time spent transferring data between the server/node/controller.
- If your arguments are already lists, the `chunk_size` argument is not used.
    - Instead, one argument/list will be distributed to the connected `achilles_node`s at a time.
- If your arguments are load balanced, the results returned are contained in lists of length `achilles_node's cpu_count` *  `chunk_size`.
    - `map`:
        - Final result of `map` is an ordered list of load balanced lists (the final result is not flattened).
    - `imap`:
        - Results are returned as computation is finished in dictionaries that include the following keys:
            - `RESULT`: load balanced list of results.
            - `ARGS_COUNTER`: index of first argument (0-indexed).
         - Results are ordered.
             - The first result will correspond to the next result after the last result in the preceeding results packet's list of results.
             - Likely to be slower than `immap_unordered` due to `achilles_controller` yielding ordered results. `imap_unordered` (see below) yields results as they are received, while `imap` yields results as they are received only if the argument's `ARGS_COUNTER` is expected based on the length of the `RESULT` list in the preceeding results packet. Otherwise, the results packet is added to a `result_buffer` and the `result_buffer` is checked for the results packet with the expected `ARGS_COUNTER`. If it is not found, `achilles_controller` will not yield results until a results packet with the expected `ARGS_COUNTER` is received.
    - `imap_unordered`:
        - Results are returned as computation is finished in dictionaries that include the following keys:
            - `RESULT`: load balanced list of results.
            - `ARGS_COUNTER`: index of first argument (0-indexed).
         - Results are not ordered.
             - Results packets are yielded as they are received (after any `achilles_callback` has been performed on it).
             - Fastest way of consuming results received from the `achilles_server`.
             


<br/>
<hr/>

`achilles` is in the early stages of active development and your suggestions/contributions are kindly welcomed.

`achilles` is written and maintained by Alejandro Peña. Email me at adpena at gmail dot com.

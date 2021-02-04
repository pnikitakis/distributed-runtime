# distributed-runtime
University project for Distributed Systems (Spring 2018). 

## Description
- Stage A: Execute programs written in a custom programming language called SimpleScript (see SimpleScript_syntax.png).  
- Stage B: Make the runtime distributed where machines discover each other and run the programs remotely if they are in another machine.  
- Stage C: Dynamic code migration. Migrate running programs to a new machine and continue execution from the same line.  

## How to run
`Configuraton.py` file defines whether the execution will be distributed (True) or not (False).

- For stage A: Set false the Configuraton file.  Use the commands run for implementing the code, list for listing the existings programs and kill for terminating a specific program.

- For stage B: Set true the Configuraton file. Use the same commands as stage A. 

- For stage C: First run the `dir.py` to get directory's ip and port. Run the `runtime.py` and `<join> <runtime_file>` and connect to directory.Use `migrate <id> <ip> <port>` for sending code to other hosts or the same commands (run , list, kill) as previous stages.

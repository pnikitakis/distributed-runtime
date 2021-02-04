# distributed-runtime
Runtime that executes SimpleScript programs in a distrubuted system. University project for Distributed Systems (Spring 2018).

## Description
- Stage A: Execute programs written in a custom programming language called SimpleScript.  
- Stage B: Make the runtime distributed where machines discover each other and run the programs remotely if they are in another machine.  
- Stage C: Dynamic code migration. Migrate running programs to a new machine and continue execution from the same line.  

A visual representation of the system can be found [here](https://github.com/pnikitakis/distributed-runtime/blob/main/Visual%20representation.pdf).

## SimpleScript syntax
![SimpleScript syntax](https://github.com/pnikitakis/distributed-runtime/blob/main/SimpleScript_syntax.png)

## Prerequisites
Python 3.6+

## How to run
Execute script `runtime.py`.

The `configuraton.py` file defines whether the execution will be distributed (True) or not (False).

- For stage A: Set false the Configuraton file.  Use the commands run for implementing the code, list for listing the existings programs and kill for terminating a specific program.

- For stage B: Set true the Configuraton file. Use the same commands as stage A. 

- For stage C: First run the `dir.py` to get directory's ip and port. Run the `runtime.py` and `<join> <runtime_file>` and connect to directory.Use `migrate <id> <ip> <port>` for sending code to other hosts or the same commands (run , list, kill) as previous stages.

## Authors
- [Panagiotis Nikitakis](https://www.linkedin.com/in/panagiotis-nikitakis/)
- [Kalliopi Rantou](https://www.linkedin.com/in/kalliopi-rantou-6564981b4/)

## Course website
[ECE348 Distributed Systems](https://www.e-ce.uth.gr/studies/undergraduate/courses/ece348/?lang=en)

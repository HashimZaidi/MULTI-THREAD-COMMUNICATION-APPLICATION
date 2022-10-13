# Messaging Application
This is a simple messaging application, based on client-server architecture. Multiple clients send and receive messages via a single server using sockets.

## Installation
To install locally, do the following:

1. Ensure that the following things have been installed:

    a. python (Installed based on your distro)

    b. pip (curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py)

    c. virtualenv

2. Open up a terminal.

3. Create a directory somewhere `mkdir messaging-app-env` and `cd` into it.

4. Create a python virtual environment `python -m virtualenv .`

5. Activate the virtual environment `source bin/activate`

6. Navigate to the project's root directory where `setup.py` file is located.

7. Do a ```pip install .``` 

## How to run the Server?:

Once the installation is complete, you can run the server by running the command: `server` . The server would start listening for clients at port 8000. You can change the port by adding the flag `--port` to the command. Eg. `server --port 8888`

For more information, run `server --help`

## How to run a Client?:

Once the server is up, you may run a client using the following command:

```
$ client --name client1 --port 8001 --server-ip 127.0.0.1 --server-port 8000
2022-02-20 10:36:07,305 — client1 is now connected to the server
Enter 1 to send message
Enter 2 to view who's online/offline
Enter 3 to exit
```

Similarly, using the above command, you can run more clients with different names and ports.

Follow the instructions to send messages or see who's online.

For more information, run `client --help`

## Docker

Build the Dockerfile using the following commands:

```
docker build --file docker/Dockerfile -t messaging-app .
```

To run a server using docker, run the following command:

```
docker run --rm -it -e PORT=8000 messaging-app
```

To run a client using docker, run the following command:

```
docker run --rm -it -e NAME=client1 -e PORT=8001 -e SERVER_IP=<ip-of-server-container> -e SERVER_PORT=8000 messaging-app client
```

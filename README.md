# Gravity

## Overview

This application serves to track time spent working on projects, with a focus on making interruptions visible. It offers
a set of standard, database-backed tables which can be used to define custom projects and actions.

Overall, this project also serves as a testbed for some alternative ways for connecting a frontend and backend via
something other than REST, by sending JSON messages via various sockets (TCP/UNIX/WebSocket) in order to communicate
time tracking events to the underlying server, which in turn saves them to a database.

This repository also holds an example frontend for the application, which provides a curses-based interface to quickly
input event data from the console. It additionally provides a rich set of command-line options to influence client,
server, and database configuration/behaviour.

The name `gravity` stems from my personal frustration with the state of time tracking in my consulting job, where I
regularly work on multiple projects (let alone multiple tickets) on a daily basis, and where I often have to switch
contexts, without having a robust way of keeping track of concrete times spent on individual tickets, tasks, etc. It is
this lack of tooling that sometimes kept me from transitioning between tasks more smoothly, and since gravity is what
holds every one of us down and weighs on us, it seemed like an apt name.

NB: This application is a work in progress, and while I have been using this in my daily job for the past two years,
there is still functionality missing, and there are also some edge-cases that are not handled well quite yet.

## Installation

This application is written in `python3`.

It uses `git` for distributed version control, `pipenv` for dependency management, `oslo-config` for configuration, and
`pytest` for testing.

### Python environment

To retrieve the full source code and initialise a local virtual environment including required packages, run:

```
# Git
git clone git@github.com:rmk2/gravity.git

# Pipenv
# NB: with the switch -d, pipenv also installs development packages, such as pytest
pipenv install -d

# Activate environment
pipenv shell

# Optional: generate a requirements.txt via pipenv, which pbr uses to check dependencies
pipenv lock --requirements > requirements.txt

# Install locally checked out package
pip install -e .
```

### Configuration

This application is configured via a central config file, and/or via command-line switches. Command-line arguments take
precedence over config options, which in turn overwrite hardcoded defaults (where applicable).

A sample configuration can be generated via `oslo-config`, which is used for configuration parsing, command-line
handling, argument defaults etc:

```
# Generate default sample config
oslo-config-generator --config-file config-generator.conf

# Output config to stdout
oslo-config-generator --namespace gravity

# Output config to default config file
oslo-config-generator --namespace gravity > gravity.default.conf
```

## Running the application

### Usage

The application is broken down into a number of sub-commands which range from running the application server or running
the client, to administrative tools that allow users to initialise the backend database, to administer project setup and
so on.

By using `oslo-config`, all configuration can also be done via command-line arguments, which bloats the available help
text somewhat. An abbreviated overview of existing sub-commands is shown below, while the full list of commands and/or
configuration options can be queried via `gravity --help`:

```
usage: gravity [-h] [--config-dir DIR] [--config-file PATH] ...
               {project,annotate,server,client,action,database,worklog,test} ...

optional arguments:
  -h, --help            show this help message and exit
  --config-dir DIR      Path to a config directory to pull `*.conf` files from.
  --config-file PATH    Path to a config file to use.

  {project,annotate,server,client,action,database,worklog,test}
    project             Administrate project data
    annotate            Annotate a given project
    server              Start a gravity server instance
    client              Run a gravity client instance
    action              Administrate event action data
    database            Configure the backend database
    worklog             Manipulate worklog entries
```

Additionally, each sub-command has its own set of options, which can be queried via `gravity <sub-command> --help`, e.g. 

```
# Project options
usage: gravity project [-h] (-a ... | -e | -i FILE | -l | -r ...)

optional arguments:
  -h, --help            show this help message and exit
  -a ..., --add ...     Add project(s)
  -e, --export          Export projects)
  -i FILE, --ingest FILE, --import FILE
                        Import projects
  -l, --list            List projects
  -r ..., --remove ...  Remove project(s)
```

### Running the server

The project requires a running server instance, which serves as a central sender/receiver for any event messages, which
saves events to the configured storage backend, and which reads stored data in order to return it to the client.

The server normally communicates via either TCP or UNIX socket, and can be started manually via:

```
# Start the server, keep it in the foreground
gravity server

# Start the server, keep it in the background
gravity --main-daemon server
```

Alternatively, a systemd service file is included in `contrib/systemd/gravity.service`, which can be installed as a
user or system service, making sure that the gravity server gets started in the background whenever the user logs in or 
when the system starts.

Personally, I use (and prefer) the systemd user service route, which means that the service file should be copied to
`~/.config/systemd/user/`. After reloading systemd (or logging out and in again), the server can then be started,
stopped, or enabled upon login via `systemctl`:

```
# Enable gravity user service on user login
systemctl --user enable gravity

# Start gravity server
systemctl --user start gravity

# Stop gravity server
systemctl --user stop gravity
```

### Running the client

Once the server has been started via any of the above methods, the client can simply be run via `gravity client`.
Depending on the configured frontend (`curses` by default), this will allow users to actually track worklog events.

### Initialising the database

If `gravity` is configured to use either SQLite or PostgreSQL as storage backend, a standard set of tables is defined
in `models.py` which are enough to get the database up and running. Via the command-line, this means initialising all
database tables, and then defining at least two (2) actions and one (1) project:

```
# Initialise database tables
gravity database --initialise

# Create a project
gravity project --add "My First Project"

# Create actions
gravity action --add "Start" "Stop"
```

The database should now be initialised, and a list of projects/actions can be queried via `gravity project --list` or
`gravity action --list`, respectively:

```
# gravity project --list
aea14166-d22e-44c1-a30e-adc595a9d689    My First Project

# gravity action --list 
72c2a9a8-7f3e-470a-b033-5fb0cf00bec1    Start
a9dccfe5-800d-4af7-a3ab-fa09eca87bfc    Stop
```

NB: UUIDs, as listed above, are generated randomly, and will differ each time projects/actions are created.

## Concepts

### Database

The database is normalised, which means that project/action data lives in its own tables while event data only
references their respective IDs. In the case of projects/actions, identifiers are randomly generated as UUID4. Since the
client(s) read this basic information each time they generate new events, these identifiers need to remain static to
ensure that foreign key relations between tables remain intact.

Events are simply sequentially numbered, whereas the numeric identifier itself does not serve as a foreign key for any
other table. 
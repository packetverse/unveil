# Todo

- [ ] Add option to check if a blacklist/provider is online and working
- [ ] Add support for multiple output formats
- [ ] Add threading to allow for faster scans/requests
- [ ] In `ip` command allow for raw which just prints out the raw json response nicely
- [ ] Add validation for IPv6 and for recogninzing different type of IPs e.g. APIPA address, private address, and so on.
- [ ] Write tests together with pytest library
- [ ] Add support for env vars to specify stuff like `CACHE_DIR` and so on.
- [ ] Add custom config and file could be in toml, yaml or json format
- [ ] Fix performance and concurrency issues in `ip` command
- [ ] Add more global options:
  - [ ] `--quiet`
  - [ ] `--verbose`: needs to be improved
  - [ ] `--version`
  - [ ] `--config`: should be implemented for default options and a little more customization in output and so on

# In progress

- [ ] Add mac subcommand and more related commands

# Done

- [x] Implement caching for downloading files
- [x] Add custom providers/blacklists option for `check` command
- [x] Split up files for better readability, e.g. make a commands folder to store all Typer commands.
- [x] Add docstrings for functions instead of using the help parameter for everything (`app.command` decorator)
- [x] Add metavar parameters to some of the `typer.Argument`
- [x] Add logging and handle it correctly and well for debugging and other purposes because it's currently fucking shit
- [x] Add some more output and logs and verbose messages currently only a couple
- [x] Add more sources to fetch from automatically for `ip` command since it only currently has 2 different API calls

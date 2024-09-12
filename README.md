# paperless-ngx-cli

Paperless-ngx Command-Line Interface

I've recently started a project to collect scripts around Paperless-ngx ([paperless.sh](https://paperless.sh)). It turned out - surprise - to be very tedious to write a separate [script](https://github.com/marcelbrueckner/paperless.sh/blob/6cc85b20482e0281d9e26ab82fcaccf34e27a276/scripts/post-consumption/content-matching/pngx-update-document.py) [each](https://github.com/marcelbrueckner/paperless.sh/blob/6cc85b20482e0281d9e26ab82fcaccf34e27a276/scripts/api/custom-field-sum/custom-field-sum.py) [time](https://github.com/marcelbrueckner/paperless.sh/blob/6cc85b20482e0281d9e26ab82fcaccf34e27a276/scripts/api/custom-field-sum/custom-field-sum-of-differences.py) I need to work with Paperless-ngx's API.
I was looking for a way to easily update certain fields of my documents but without the overhead of "manually" calling API endpoints each time.
I wrapped things in simple python scripts which eventually became this tool which essentially ~~is~~ will become Paperless-ngx at your command-line.

## Usage

This very first public release currently only allows you to retrieve information or update certain fields of your existing documents (with more to come in the future).

```bash
# Run pngx -h for help
$ pngx [ command ] [ subcommand ] [ arguments and parameters ]
```

Log in to your Paperless-ngx instance which will be used in subsequent commands.

```bash
# Log in to the given host and save account credentials as default
$ pngx auth login https://paperless.example.com --ask-token
# Delete saved credentials from disk
$ pngx auth logout
```

Show details of a document with specific ID

```bash
# Run pngx document show -h for help
$ pngx document show <ID>
Title                      2024-01-10_RE12345678                                                                      
ID                         400                                                                                        
ASN                        None                                                                                       
Created                    2024-01-10
...
```

Update a document's title and correspondent.

```bash
# Set document title to "My new document title" and set specific correspondent
$ pngx document edit <ID> --title "My new document title" --correspondent <CORRESPONDENT_ID>
```

Assign or unassign a document's tags.

Tags can be specified by ID or the *exact* name. If your tag name contains spaces, wrap it in quotes.

You can add and remove multiple tags at once, separated by space.

```bash
# Add or remove one or multiple tags to/from a document given the ID or _exact_ name
$ pngx document edit <ID> --add-tags <ID|EXACT_NAME> [ID|EXACT_NAME]
$ pngx document edit <ID> --remove-tags <ID|EXACT_NAME> [ID|EXACT_NAME]
```

Add, update or remove custom fields.

Similar to tags, custom fields can be specified by ID or the *exact* name, which must be quoted if it contains spaces.
In addition, custom fields can have a value that can be passed in a KEY=VALUE style. Make sure your value adheres to the custom field's type. If your custom field name contains an equal sign, refer to it by its ID.

You can add and remove multiple custom fields at once, separated by space.

```bash
# Add/Update or remove custom field given the ID or _exact_ name
$ pngx document edit <ID> --add-custom-fields <ID|EXACT_NAME>[=VALUE] [<ID|EXACT_NAME>[=VALUE]]
$ pngx document edit <ID> --remove-custom-fields <ID|EXACT_NAME> [<ID|EXACT_NAME>]
```

## Configuration

The Paperless-ngx CLI client can be configured in a variety of ways.
In order of precedence from lowest (most easily overridden) to highest (overrides all others), it offers the following configuration sources:

* applications defaults
* configuration file
* environment variables
* command-line parameters

### Application defaults

There's only one application default:

* the CLI client configuration file (which defaults to `$XDG_CONFIG_HOME/pngx/pngx.toml`[^1])

[^1]: In case you don't know about the *XDG Base Directory Specification*, check out [their docs](https://specifications.freedesktop.org/basedir-spec/basedir-spec-latest.html).

### Configuration file

The Paperless-ngx CLI client can read all basic configuration (the Paperless-ngx server's authentication information) from its configuration file (`pngx.toml`). A custom file path can be specified via:

* command-line parameter (`--config`)
* environment variable (`$PNGX_CONFIG`)

If both are specified, the command-line parameter takes precedence. Otherwise, it uses the first `pngx.toml` file found at these locations in order:

* `$PWD/pngx.toml`
* `$XDG_CONFIG_HOME/pngx/pngx.toml` (application default)

If no configuration file can be found, it will be created at the application default location.

Run `pngx --show-config` to get the configuration file path in use.

```bash
# Default configuration path if no pngx.toml exists in current working directory
$ pngx --show-config
/Users/marcelbrueckner/.config/pngx/pngx.toml
```

Obviously, you can't specify a configuration path within the configuration file itself.

### Environment variables

If you don't want your credentials to be stored on disk, you can use environment variables or ad-hoc session parameters (see command-line below)

Environment variables have a higher precedence than entries in `pngx.toml`. Existing environment variables override corresponding values in your configuration file. If you can't connect to your Paperless-ngx instance, make sure you don't have accidentially mixed values from your configuration file and environment.

* `PNGX_HOST`
* `PNGX_USER`
* `PNGX_TOKEN`

* `PNGX_CONFIG`

### Command-line parameters

You can use the command-line to log in to your Paperless-ngx instance. The credentials provided will be saved to your configuration file.

```bash
# Store your credentials for subsequent usage
# Your credentials might end up in your shell history, so be cautious! 

# Don't do that
$ pngx auth login --host=https://paperless.example.com --user=username --password=password
# Use this instead
$ pngx auth login --host=https://paperless.example.com --user=username --ask-password|--ask-token
```

If you don't want your credentials saved to file, use them as ad-hoc session parameters.

```bash
$ pngx --host=https://paperless.example.com --user=username --ask-password|--ask-token auth show
```

## Caveats

Paperless-ngx CLI allows you to add servers whose API can be accessed without authentication. However, the underlying `pypaperless` library this CLI is using doesn't look like it supports anything else than token authentication. I guess that you will likely run into errors if you don't use token authentication on your Paperless-ngx server instance. Maybe a token can be generated while using remote user auth, but it's untested at this point.

I'm currently running Paperless-ngx v2.5.3 against which I test the features of this CLI, thus it might be incompatible with newer version.

# paperless-ngx-cli

Paperless-ngx Command-Line Interface

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

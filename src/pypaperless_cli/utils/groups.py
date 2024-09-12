"""CLI command and parameter groups."""

from cyclopts import Group, validators

from pypaperless_cli.utils.validators import adhoc_xor_specific

#
# Visible groups
#

# Meta app
meta_parameters_adhoc = Group("Ad-hoc Session Parameters", sort_key=0, help="")
meta_parameters_specific = Group("Specific Session Parameters", sort_key=meta_parameters_adhoc.sort_key+1, help="")

# "Regular" commands group
# Basically cyclopt's default, but with an explicit sort_key to keep the group in upper position in the CLI's help
commands = Group(name = "Commands", sort_key=meta_parameters_specific.sort_key+1)

# Parameter groups
arguments = Group(name = "Arguments", sort_key=0)
standard_fields = Group(name = "Standard fields parameters", sort_key=arguments.sort_key+1)


#
# Functional groups
#

# Mutually exclusive session parameters
password_xor_token = Group(
    "Password/API Token",
    show = False,
    validator=validators.LimitedChoice()
)

meta_parameters = Group(
    "Session Parameters",
    show = False,
    validator = adhoc_xor_specific
)
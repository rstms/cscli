import click

from cscli.cli import pass_environment


@click.group(name="vlan")
@click.argument("name", metavar="VLAN", type=str)
@pass_environment
def cli(ctx, name):
    """VLAN actions: create list show modify destroy"""
    ctx.vlan_name = name


@cli.command()
@click.option("-d", "--duration", type=int, default=1)
@click.option(
    "-u", "--units", type=click.Choice(["hour", "day", "month", "year"]), default="day"
)
@click.option("-a", "--auto-renew", is_flag=True)
@pass_environment
def create(ctx, duration, units, auto_renew):
    """create a VLAN subscription"""
    if duration > 1:
        units += "s"
    ctx.output(ctx.api.create_vlan(ctx.vlan_name, f"{duration} {units}", auto_renew))


@cli.command()
@pass_environment
def show(ctx):
    """display VLAN by name or uuid"""
    ctx.output(ctx.api.find_vlan(ctx.vlan_name))


@cli.command()
@click.option("-r", "--rename", type=str)
@click.option("-D", "--description", type=str)
# @click.option('-d', '--duration', type=int, default=1)
# @click.option('-u', '--units', type=click.Choice(['hour', 'day', 'month', 'year']), default='day')
# @click.option('-a', '--auto-renew', is_flag=True)
@pass_environment
def modify(ctx, rename, description):
    """modify VLAN attributes"""
    vlan = ctx.api.find_vlan(ctx.vlan_name)
    if rename:
        vlan["meta"]["name"] = rename
    if description:
        vlan["meta"]["description"] = description
    # if auto_renew:
    #    ctx.error('unimplemented')
    # if duration:
    #    ctx.error('unimplemented')
    # if units:
    #    ctx.error('unimplemented')
    ctx.output(ctx.api.vlan.update(vlan["uuid"], vlan))


@cli.command()
@click.option("-f", "--force", is_flag=True, help="suppress confirmation prompt")
@pass_environment
def destroy(ctx, force):
    """delete VLAN by name or uuid"""
    name = ctx.vlan_name
    vlan = ctx.api.find_vlan(name)
    ctx.confirm(vlan, "destruction", "VLAN", force)
    ctx.error(
        f"VLAN {name} cannot be deleted while subscribed (verify autorenew status)"
    )

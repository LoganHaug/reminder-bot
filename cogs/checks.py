import database


def is_administrator(ctx):
    return ctx.message.author.id == 322158695184203777


def is_operator(ctx):
    """Returns whether the user of the context is an operator of the bot"""
    return bool(
        database.DB[str(ctx.message.guild.id)].find_one(
            {"user_id": ctx.message.author.id, "type": "user"}
        )
    )

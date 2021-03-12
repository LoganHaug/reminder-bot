"""Holds some utility functions for reminder_bot"""

import discord
import pygal


def generate_embed(title: str, desc: str):
    return discord.Embed(
        **{
            "title": title,
            "description": desc,
            "color": discord.Color(0).dark_magenta(),
        }
    )


def split_date(date: str):
    """Splits a string date into year, month, day, and hour"""
    if "-" in date:
        split_date = date.strip().split("-")
    elif "/" in date:
        split_date = date.strip().split("/")
    return {
        "month": int(split_date[0]),
        "day": int(split_date[1]),
        "year": int(split_date[2]),
    }


def split_time(time: str):
    """Splits a string time into hour and minute"""
    time = time.strip().split(":")
    return {"hour": int(time[0]), "minute": int(time[1])}


def generate_graph():
    """Generates "the graph" """
    xy_chart = pygal.XY(
        style=pygal.style.DarkColorizedStyle, x_title="gay", y_title="dumb"
    )
    xy_chart.title = "Mckenna"
    xy_chart.add("heh", [(x, x) for x in range(0, 2)])
    xy_chart.render_to_file("image.svg")

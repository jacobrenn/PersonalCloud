#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = ["click", "requests"]
# ///
"""PyAgent external tool: searxng.

This script allows the agent to perform web searches using a SearXNG instance.
"""

from __future__ import annotations

import json
import sys

import click
import requests

TOOL_NAME = "searxng"
TOOL_DESCRIPTION = (
    "Perform a web search using SearXNG to get real-time information from the internet."
)
TOOL_PARAMETERS = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query to look up on the web.",
        },
    },
    "required": ["query"],
}
TOOL_VERSION = "1"

SEARXNG_URL = "http://searxng:8080/search"


def run_tool(*, query: str) -> str:
    """Calls the SearXNG API and formats the output for the agent."""
    try:
        params = {
            "q": query,
            "format": "json",
        }
        response = requests.get(SEARXNG_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        if not results:
            return "No results found for the given query."

        formatted_results = []
        for idx, res in enumerate(results[:10], 1):
            title = res.get("title", "No Title")
            url = res.get("url", "No URL")
            content = res.get("content", "No content available.")
            formatted_results.append(
                f"[{idx}] {title}\nURL: {url}\nSnippet: {content}\n")

        return "\n---\n".join(formatted_results)

    except requests.exceptions.RequestException as e:
        return f"Error connecting to SearXNG: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


@click.group()
def cli() -> None:
    """PyAgent external tool entry point."""


@cli.command()
def describe() -> None:
    """Print the JSON manifest used by PyAgent to register this tool."""
    click.echo(
        json.dumps(
            {
                "name": TOOL_NAME,
                "description": TOOL_DESCRIPTION,
                "parameters": TOOL_PARAMETERS,
                "version": TOOL_VERSION,
            },
            ensure_ascii=False,
        )
    )


@cli.command()
@click.option(
    "--args",
    "args_json",
    required=True,
    help="Stringified JSON object with the tool arguments (not a file path).",
)
def invoke(args_json: str) -> None:
    """Run the tool with arguments from a JSON string passed via ``--args``.

    ``--args`` takes a single stringified JSON object (not a file path),
    for example ``--args '{"query": "value"}'``.
    """
    try:
        arguments = json.loads(args_json)
    except json.JSONDecodeError as exc:
        click.echo(f"Failed to parse --args: {exc}", err=True)
        sys.exit(2)

    if not isinstance(arguments, dict):
        click.echo("--args must contain a JSON object.", err=True)
        sys.exit(2)

    try:
        result = run_tool(**arguments)
    except TypeError as exc:
        click.echo(f"Invalid tool arguments: {exc}", err=True)
        sys.exit(2)
    except Exception as exc:
        click.echo(f"Tool error: {exc}", err=True)
        sys.exit(1)

    click.echo(result if result is not None else "")


if __name__ == "__main__":
    cli()

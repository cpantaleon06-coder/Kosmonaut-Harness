import sandbox


def execute_tool(name: str, args: dict, container_id: str) -> str:
    # Errors are returned as text (not raised) so the model can read them and try again.
    try:
        if name == "run_command":
            result = sandbox.run(container_id, args["command"])
            return f"exit code: {result['exit_code']}\n{result['output']}"
        if name == "write_file":
            sandbox.write_file(container_id, args["path"], args["content"])
            return f"Wrote {args['path']}"
        if name == "read_file":
            return sandbox.read_file(container_id, args["path"])
        return f"Error: unknown tool {name}"
    except Exception as error:
        return f"Error: {error}"

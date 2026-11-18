import brain

result = brain.handle_message("Create hello.py that prints hello, and run it.")
print(result)
print("archive size:", len(brain.get_archive(result["project_id"])), "bytes")
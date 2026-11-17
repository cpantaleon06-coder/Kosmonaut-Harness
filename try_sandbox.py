import sandbox

cid = sandbox.create()
print("container:", cid[:12])
try:
    sandbox.write_file(cid, "hello.py", "print('hello from the sandbox')")
    print(sandbox.run(cid, "python hello.py"))
    print(sandbox.read_file(cid, "hello.py"))
    print("tar size:", len(sandbox.export_workspace(cid)), "bytes")
finally:
    sandbox.destroy(cid)
    print("container destroyed")

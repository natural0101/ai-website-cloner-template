import argparse
import json
import os
import socket
import sys


def recv_json(sock: socket.socket) -> dict:
    chunks: list[bytes] = []
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        chunks.append(chunk)
        try:
            return json.loads(b"".join(chunks).decode("utf-8"))
        except json.JSONDecodeError:
            continue
    if not chunks:
        raise RuntimeError("No response from Blender socket")
    return json.loads(b"".join(chunks).decode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Call a running Blender MCP socket server.")
    parser.add_argument("--host", default=os.environ.get("BLENDER_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("BLENDER_PORT", "9876")))
    parser.add_argument("--type", default="get_scene_info", dest="command_type")
    parser.add_argument("--params-json", default="{}")
    parser.add_argument("--code-file")
    args = parser.parse_args()

    params = json.loads(args.params_json)
    if args.code_file:
        with open(args.code_file, "r", encoding="utf-8") as handle:
            params["code"] = handle.read()

    payload = {"type": args.command_type, "params": params}

    with socket.create_connection((args.host, args.port), timeout=10) as sock:
        sock.settimeout(180)
        sock.sendall(json.dumps(payload).encode("utf-8"))
        response = recv_json(sock)

    json.dump(response, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

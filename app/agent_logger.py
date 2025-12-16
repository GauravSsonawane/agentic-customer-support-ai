def log_step(node_name: str, state: dict):
    print("\n" + "=" * 50)
    print(f"NODE: {node_name}")
    print("STATE:")
    for k, v in state.items():
        print(f"  {k}: {v}")
    print("=" * 50)


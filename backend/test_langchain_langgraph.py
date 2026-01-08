import langgraph_sdk

# Inspect available classes in langgraph_sdk
print("langgraph_sdk classes:")
for name in dir(langgraph_sdk):
    obj = getattr(langgraph_sdk, name)
    if isinstance(obj, type):
        print("-", name)

# If there's a Client-like class, we can create a dummy instance safely
ClientClass = getattr(langgraph_sdk, "Client", None)
if ClientClass:
    try:
        dummy_client = ClientClass(api_key="dummy_key")  # won't connect
        print("\nDummy client created:", dummy_client)
    except Exception as e:
        print("\nDummy client instantiation raised:", e)
else:
    print("\nNo 'Client' class found in langgraph_sdk. Try checking langgraph_prebuilt or langgraph_checkpoint for the right class.")

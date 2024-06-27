import os
import ray

def setup_env():
    print("setting up environment")
    working_dir = "downloaded_docs"

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    os.environ["RAY_memory_usage_threshold"] = "1"
    # Setting up our Ray environment
    ray.init(runtime_env={
        "env_vars": {
            # "GOOGLE_API_KEY": os.environ["GOOGLE_API_KEY"],
            # "LANGCHAIN_API_KEY":os.environ["LANGCHAIN_API_KEY"]
        },
        "working_dir": str(working_dir)
    })
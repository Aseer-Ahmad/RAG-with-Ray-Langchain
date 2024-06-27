import os
import ray

def setup_env():
    working_dir = "downloaded_docs"

    # Setting up our Ray environment
    ray.init(runtime_env={
        "env_vars": {
            "GOOGLE_API_KEY": os.environ["GOOGLE_API_KEY"],
            "LANGCHAIN_API_KEY":os.environ["LANGCHAIN_API_KEY"]
        },
        "working_dir": str(working_dir)
    })
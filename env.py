import os
import ray

def setup_env():
    
    working_dir = "downloaded_docs"

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    # Setting up our Ray environment
    ray.init(runtime_env={
        "env_vars": {
            "OPENAI_API_KEY": os.environ["OPENAI_API_KEY"],
            "GOOGLE_API_KEY": os.environ["GOOGLE_API_KEY"]
        },
        "working_dir": str(working_dir)
    })
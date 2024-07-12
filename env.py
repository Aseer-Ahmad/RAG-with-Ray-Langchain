import os
import ray
import vertexai


def setup_env():
    print("setting up environment")
    working_dir = "downloaded_docs"

    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    os.environ["RAY_memory_usage_threshold"] = "1"
    os.environ['CPU_OR_GPU'] = 'cpu'
    os.environ["GOOGLE_API_KEY"] = open("/home/cepheus/Documents/API keys/googleai.txt", 'r').read()
    # vertexai.init(project=PROJECT_ID)
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/cepheus/Documents/API keys/gap_cred.json"

    # Setting up our Ray environment
    ray.init(runtime_env={
        "env_vars": {
            
            "GOOGLE_API_KEY": open("/home/cepheus/Documents/API keys/googleai.txt", 'r').read(),
            "LANGCHAIN_API_KEY": open("/home/cepheus/Documents/API keys/langchain.txt", 'r').read()
        },
        "working_dir": str(working_dir),
        "num_cpus" : 1,
        "num_gpus" : 0
    })

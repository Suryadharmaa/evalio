import os

# Local developer credentials must never affect deterministic test configuration.
os.environ["EVALIO_DISABLE_DOTENV"] = "1"

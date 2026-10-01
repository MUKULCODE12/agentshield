from setuptools import setup, find_packages

setup(
    name="agentshield-sdk",
    version="1.0.0",
    description="Official Python SDK for AgentShield AI Security Gateway",
    author="AgentShield Security Team",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0"
    ],
    python_requires=">=3.8",
)

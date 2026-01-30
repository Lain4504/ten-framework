"""
Self-hosted Turn Detection Server using vLLM

This server provides an OpenAI-compatible API endpoint for the TEN Turn Detection model.
It can be deployed locally or on your own infrastructure, eliminating dependency on Cerebrium.
"""

from vllm.entrypoints.openai.api_server import run_server
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Self-hosted Turn Detection Server"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="TEN-framework/TEN_Turn_Detection",
        help="Hugging Face model ID",
    )
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="Server host"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Server port"
    )
    parser.add_argument(
        "--gpu-memory-utilization",
        type=float,
        default=0.9,
        help="GPU memory utilization (0.0-1.0)",
    )
    args = parser.parse_args()

    print(f"Starting Turn Detection Server...")
    print(f"Model: {args.model}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"GPU Memory Utilization: {args.gpu_memory_utilization}")

    # Run vLLM's OpenAI-compatible server
    # This provides the same API interface that the existing code expects
    run_server(
        model=args.model,
        host=args.host,
        port=args.port,
        trust_remote_code=True,
        dtype="auto",
        gpu_memory_utilization=args.gpu_memory_utilization,
    )


if __name__ == "__main__":
    main()

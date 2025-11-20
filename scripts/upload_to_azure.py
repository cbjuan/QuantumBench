#!/usr/bin/env python3
"""
Upload benchmark results to Azure Blob Storage (Private Container)

This script is used by GitHub Actions to upload results to a private Azure container.
Can also be run manually for local uploads.

Usage:
    # From GitHub Actions (uses connection string from env)
    python scripts/upload_to_azure.py ./outputs/ my-container

    # Manual with explicit connection string
    AZURE_STORAGE_CONNECTION_STRING="..." python scripts/upload_to_azure.py ./outputs/ my-container
"""

import os
import sys
from pathlib import Path
from azure.storage.blob import BlobServiceClient, ContentSettings


def upload_directory_to_blob(local_path, container_name, connection_string):
    """Upload a directory to Azure Blob Storage"""

    print(f"Connecting to Azure Blob Storage...")
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Get or create container
    try:
        container_client = blob_service_client.get_container_client(container_name)
        container_client.get_container_properties()
        print(f"Using existing container: {container_name}")
    except Exception:
        print(f"Creating new container: {container_name}")
        container_client = blob_service_client.create_container(
            container_name,
            public_access=None  # Private container
        )

    # Upload files
    local_path = Path(local_path)
    uploaded_count = 0

    print(f"Uploading files from {local_path}...")

    for file_path in local_path.rglob('*'):
        if file_path.is_file():
            # Calculate relative path for blob name
            blob_name = str(file_path.relative_to(local_path))

            # Determine content type
            content_type = "application/octet-stream"
            if file_path.suffix == '.csv':
                content_type = "text/csv"
            elif file_path.suffix == '.txt':
                content_type = "text/plain"
            elif file_path.suffix == '.json':
                content_type = "application/json"

            # Upload
            blob_client = blob_service_client.get_blob_client(
                container=container_name,
                blob=blob_name
            )

            with open(file_path, 'rb') as data:
                blob_client.upload_blob(
                    data,
                    overwrite=True,
                    content_settings=ContentSettings(content_type=content_type)
                )

            uploaded_count += 1
            print(f"  ✓ Uploaded: {blob_name}")

    print(f"\nSuccessfully uploaded {uploaded_count} files to Azure Blob Storage")
    print(f"Container: {container_name}")
    print(f"Access: Private (authentication required)")


def main():
    if len(sys.argv) != 3:
        print("Usage: python upload_to_azure.py <local_directory> <container_name>")
        print("\nExample:")
        print("  python scripts/upload_to_azure.py ./outputs/ benchmark-results")
        sys.exit(1)

    local_path = sys.argv[1]
    container_name = sys.argv[2]

    # Get connection string from environment
    connection_string = os.environ.get('AZURE_STORAGE_CONNECTION_STRING')

    if not connection_string:
        print("Error: AZURE_STORAGE_CONNECTION_STRING environment variable not set")
        print("\nSet it with:")
        print("  export AZURE_STORAGE_CONNECTION_STRING='your-connection-string'")
        sys.exit(1)

    if not Path(local_path).exists():
        print(f"Error: Local path does not exist: {local_path}")
        sys.exit(1)

    try:
        upload_directory_to_blob(local_path, container_name, connection_string)
    except Exception as e:
        print(f"\nError uploading to Azure: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

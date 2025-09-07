import argparse
import sys
from pathlib import Path
import requests
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
)

# --- Configuration ---
# The API endpoint you want to hit
API_ENDPOINT = "http://localhost:8000/rag/ingest"
# Request timeout in seconds
REQUEST_TIMEOUT = 30 

# Initialize Rich Console for pretty printing
console = Console()

def ingest_file(file_path: Path):
    """
    Reads a file and sends its content to the ingestion API endpoint.

    Args:
        file_path: The Path object of the file to ingest.

    Returns:
        A tuple containing a boolean for success and a status message.
    """
    try:
        # Read the file content. Using utf-8 encoding is a safe default.
        content = file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False, f"Skipping non-UTF-8 file: {file_path.name}"
    except Exception as e:
        return False, f"Error reading file {file_path.name}: {e}"

    # The request body must match the API's expected format
    payload = {
        "documents": [content]
    }
    
    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            API_ENDPOINT, 
            json=payload, 
            headers=headers, 
            timeout=REQUEST_TIMEOUT
        )
        # Raise an exception for bad status codes (4xx or 5xx)
        response.raise_for_status()
        
        # If we reach here, the request was successful (2xx status code)
        return True, f"Successfully ingested {file_path.name} (Status: {response.status_code})"

    except requests.exceptions.HTTPError as e:
        # Handle HTTP errors (e.g., 404, 500)
        error_details = e.response.text if e.response else "No response body"
        return False, f"API Error for {file_path.name}. Status: {e.response.status_code}. Details: {error_details}"
    except requests.exceptions.RequestException as e:
        # Handle network-related errors (e.g., connection refused, timeout)
        return False, f"Network Error for {file_path.name}: {e}"


def main():
    """Main function to parse arguments and process the folder."""
    parser = argparse.ArgumentParser(
        description="Load files from a folder and send their content to an API endpoint.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("folder_path", type=str, help="The path to the folder containing files to ingest.")
    args = parser.parse_args()

    # Convert the string path to a Path object
    folder = Path(args.folder_path)

    # Validate that the provided path is a directory
    if not folder.is_dir():
        console.print(f"[bold red]Error:[/] The path '{folder}' is not a valid directory.")
        sys.exit(1)
        
    # Get a list of all files in the directory (and not subdirectories)
    files_to_process = [f for f in folder.iterdir() if f.is_file()]
    
    if not files_to_process:
        console.print(f"[bold yellow]Warning:[/] No files found in the directory '{folder}'.")
        sys.exit(0)

    console.print(f"[bold green]Found {len(files_to_process)} files to process in '{folder}'.[/]")
    console.print(f"Hitting endpoint: [bold cyan]{API_ENDPOINT}[/]")

    # Set up the rich progress bar
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        transient=True,  # Hides the progress bar on completion
    ) as progress:
        
        task = progress.add_task("[green]Ingesting...", total=len(files_to_process))

        for file_path in files_to_process:
            progress.update(task, description=f"[cyan]Processing {file_path.name}")
            
            success, message = ingest_file(file_path)

            if success:
                console.log(f"[green]SUCCESS[/] - {message}")
            else:
                console.log(f"[bold red]FAILURE[/] - {message}")

            progress.advance(task)

    console.print("\n[bold green]✅ All files processed.[/]")


if __name__ == "__main__":
    main()

# saiblo-worker

A worker for Saiblo

## Usage

### Run with Docker

We provide a pre-built Docker image for the worker. You can run it with the following command:

```sh
docker run -d --env-file .env ghcr.io/thuasta/saiblo-worker
```

Or set environment variables directly:

```sh
docker run -dit -e GAME_HOST_IMAGE=<your-game-host-image> -e NAME=<worker-name> --rm --privileged ghcr.io/thuasta/saiblo-worker
```

The worker will automatically connect to the Saiblo server and start processing matches.

If you want to build the Docker image yourself, follow these steps:

1. Build the Docker image:

    ```sh
    docker build -t saiblo-worker .
    ```

2. Run the Docker container:

    ```sh
    docker run -d --env-file .env saiblo-worker
    ```

   You can also set environment variables directly:

    ```sh
    docker run -dit -e GAME_HOST_IMAGE=<your-game-host-image> -e NAME=<worker-name> --rm --privileged saiblo-worker
    ```

### Run Manually

1. Set up environment variables in a `.env` file:

    ```sh
    GAME_HOST_IMAGE=<your-game-host-image>  # Required: Docker image for the game host
    NAME=<worker-name>                      # Required: Unique name for this worker to set on Saiblo

    HTTP_BASE_URL=<url>                     # Optional: API base URL (default: https://api.dev.saiblo.net)
    WEBSOCKET_URL=<url>                     # Optional: WebSocket URL (default: wss://api.dev.saiblo.net/ws/)
    ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the worker:
   ```bash
   python main.py
   ```

The worker will:
- Connect to the Saiblo server
- Build Docker images for submitted code
- Run matches using the game host image
- Report results back to the server

## Environment Variables

The worker will pass the following environment variables to the game host Docker container:

- `TOKENS`: A comma-separated list of tokens for the players

And the following environment variables to the agent Docker container:

- `TOKEN`: The token for the player
- `GAME_HOST`: The address of the game host

## Match Result Retrieval

The worker will automatically retrieve match results from the Saiblo server after each match. For the game host Docker image, make sure after each match these files are created:

- `/app/data/result.json`: The match result in JSON format
- `/app/data/replay.dat`: The match replay in binary format

## Contributing

PRs are welcome!

## License

AGPL-3.0-or-later © ASTA

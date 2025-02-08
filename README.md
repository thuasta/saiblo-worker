# saiblo-worker

A worker for Saiblo

## Usage

### Run with Docker

We provide a pre-built Docker image for the worker. You can run it with the following command:

```sh
docker run -dit -e GAME_HOST_IMAGE=<your-game-host-image> -e NAME=<worker-name> --rm --privileged ghcr.io/thuasta/saiblo-worker
```

The worker will automatically connect to the Saiblo server and start processing matches.

If you want to build the Docker image yourself, you can run the following command:

```sh
docker build -t saiblo-worker .
```

### Run Manually

1. Set up environment variables in a `.env` file.

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the worker:
   ```bash
   python main.py
   ```

## Environment Variables

### For Saiblo Worker

The worker reads the following environment variables:

- `AGENT_CPUS`: CPU limit for agent containers (default: `0.5`)
- `AGENT_MEM_LIMIT`: Memory limit for agent containers (default: `1g`)
- `GAME_HOST_CPUS`: CPU limit for game host container (default: `1`)
- `GAME_HOST_IMAGE`: Docker image for game host container (**required**)
- `GAME_HOST_MEM_LIMIT`: Memory limit for game host container (default: `1g`)
- `HTTP_BASE_URL`: Base URL for HTTP requests (default: `https://api.dev.saiblo.net`)
- `JUDGE_TIMEOUT`: Maximum time for a match in seconds (default: `600`)
- `LOGGING_LEVEL`: Logging level (default: `INFO`)
- `NAME`: Name of the worker (**required**)
- `WEBSOCKET_URL`: WebSocket URL for connecting to Saiblo (default: `wss://api.dev.saiblo.net/ws/`)

### Passed to Internal Containers

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

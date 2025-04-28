# voice2txt

A simple Python CLI tool to transcribe audio files using OpenAI's Whisper API (or third-party compatible endpoints).

## Features

- Transcribe audio files (MP3, WAV, and more) to text✨
- Support for custom Whisper API base URLs
- Persistent configuration via `whisper_config.json`
- Save API credentials and endpoint for future runs
- Robust error handling for file I/O and API errors

## Requirements

- Python 3.7 or higher
- [OpenAI Python library](https://pypi.org/project/openai/) (`openai`)

## Installation

1. Clone this repository or download `voice2txt.py`.
2. Install dependencies:
   ```bash
   pip install openai
   ```

## Configuration

The tool looks for configuration in the following order:

1. Command-line arguments (`--api-key`, `--base-url`)
2. Saved configuration in `whisper_config.json`
3. Environment variable `OPENAI_API_KEY`

### Saving Configuration

To save your API key and/or custom base URL for next time, run with:
```bash
python voice2txt.py <audio_file> --api-key YOUR_KEY --base-url YOUR_URL --save
```
This writes to `whisper_config.json`:
```json
{
  "api_key": "YOUR_KEY",
  "base_url": "YOUR_URL"
}
```

## Usage

```bash
python voice2txt.py <audio_file> [--api-key YOUR_KEY] [--base-url URL] [--save]
```

- `<audio_file>`: Path to the audio file to transcribe.
- `--api-key`: Your OpenAI API key (overrides saved config and env var).
- `--base-url`: Custom Whisper API endpoint URL.
- `--save`: Save provided `--api-key` and/or `--base-url` to `whisper_config.json`.

### Examples

- **Using environment variable**:
  ```bash
  export OPENAI_API_KEY=your_api_key
  python voice2txt.py audio.mp3
  ```

- **Using CLI args and saving config**:
  ```bash
  python voice2txt.py audio.wav --api-key your_api_key --base-url https://api.example.com --save
  ```

- **Transcribing with saved config**:
  ```bash
  python voice2txt.py recording.flac
  ```

## Output

On success, the script prints:
```
Transcription complete.
<transcribed text here>
```

## Error Handling

- **File not found**: Prints an error if the specified audio file doesn’t exist.
- **API errors**: Catches `APIError` from the OpenAI client and displays details.
- **Unexpected errors**: Catches all other exceptions and shows an error message.

# CFE (Coding For Everyone)

A natural-language scripting language and agent gateway designed to make it easier to write structured prompts (so you can reduce LLM token usage vs ad-hoc free-form instructions). CFE (aka CFD) works to reduce token discussions by reducing agent to agent communications. Try it and see, have CFE talk to your agents.

python, llm, token-efficiency, natural-language, interpreter

## What this repo includes

- `cfd/`: The language (grammar, parser, interpreter) for writing programs as simple English sentences.
- `cfe/`: An agent gateway that routes `define agent` / `tell` / `hear` messages to model providers.

## Quick start

Run the example program from `cfd/examples/`:

```bash
python3 -m cfe cfd/examples/showcase.cfd
```

If you want the agent-enabled examples, set API keys as environment variables (no secrets are stored in the repo):

- `OPENAI_API_KEY` (OpenAI agents in `agents.yaml`)
- `ANTHROPIC_API_KEY` (Anthropic agents in `agents.yaml`)

## Docs

- Language overview: [`cfd/README.md`](cfd/README.md)
- Full language spec: [`cfd/SPEC.md`](cfd/SPEC.md)

## Security note

`agents.yaml` references API keys by environment variable name (for example `OPENAI_API_KEY`). The gateway resolves those values at runtime, so the repository should not contain literal API keys.

## License

MIT (see [`LICENSE`](LICENSE))


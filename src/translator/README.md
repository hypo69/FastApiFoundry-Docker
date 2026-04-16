# src/translator

Translation module — translates text before sending to AI model.

## Purpose

The main use case is **auto-translating non-English user input to English** before
passing it to a local AI model, which typically performs better on English prompts.

## Files

| File | Description |
|---|---|
| `translator.py` | `Translator` class + `translator` singleton |
| `__init__.py` | Re-exports `Translator`, `translator` |

## Providers

| ID | Description | Requires key |
|---|---|---|
| `llm` | Current Foundry model via prompt | No |
| `deepl` | DeepL API (free tier: 500K chars/month) | `DEEPL_API_KEY` in `.env` |
| `google` | Google Cloud Translation API | `GOOGLE_TRANSLATE_API_KEY` in `.env` |
| `helsinki` | Helsinki-NLP local NMT via HuggingFace | No (model must be loaded) |

## API

```python
from src.translator import translator

# Translate to any language
result = await translator.translate(
    "Привет мир",
    provider="llm",        # llm | deepl | google | helsinki
    source_lang="auto",    # ISO 639-1 or "auto"
    target_lang="en",
)
# result["translated"] == "Hello world"
# result["elapsed_ms"] == 1240

# Translate to EN for model (skips if already English)
result = await translator.translate_for_model("Как дела?")
# result["was_translated"] == True
# result["translated"] == "How are you?"

# Detect language
result = await translator.detect_language("Bonjour le monde")
# result["language"] == "fr"
# result["language_name"] == "French"

# Batch
result = await translator.batch_translate(
    ["Привет", "Пока"],
    target_lang="en",
)
# result["results"][0]["translated"] == "Hello"
```

## REST API

Mounted at `/api/v1/translation/*` by `src/api/endpoints/translation.py`.

| Method | Path | Body |
|---|---|---|
| POST | `/translation/translate` | `{text, provider?, source_lang?, target_lang?, api_key?}` |
| POST | `/translation/translate-for-model` | `{text, provider?, source_lang?, api_key?}` |
| POST | `/translation/detect` | `{text}` |
| POST | `/translation/batch` | `{texts: [...], provider?, source_lang?, target_lang?}` |
| GET  | `/translation/providers` | — |

## Environment variables

```env
DEEPL_API_KEY=your_deepl_key
GOOGLE_TRANSLATE_API_KEY=your_google_key
```

# Wake Word Speaker Verification, Speaker Identification, and STT Gateway

By [DaVoice.io](https://davoice.io)

## Overview

This repository includes end-to-end examples for:

- **Wake word detection with speaker verification**
- **Speaker identification onboarding**
- **Speaker verification from microphone audio**
- **Speaker verification gateway before STT / ASR**

These examples are useful for Python voice assistants, embedded voice interfaces, shared microphones, and any workflow where a **wake word** should be tied to a specific speaker or where **speech-to-text** should receive audio only after a target speaker is confirmed.

## Why combine wake word detection with speaker verification?

A normal **wake word detection** pipeline answers the question: "Was the wake phrase spoken?"

A **speaker verification** pipeline answers the question: "Was it spoken by the enrolled speaker?"

Combining them is valuable when a device is shared, when a workflow is privacy-sensitive, or when you want a stronger gate before downstream actions. This can reduce unwanted activations and can help keep **speech to intent** or **speech-to-text** focused on the right user.

Common examples:

- A smart device should respond to **"Hey Assistant"** only for the enrolled user.
- A healthcare workflow should accept a **custom wake word** from an enrolled clinician while ignoring nearby voices.
- A vehicle, bridge, cabin, or industrial system should wake only for the authorized operator.
- A kiosk or room device should block random bystanders from opening the voice pipeline.

## Why place a speaker verification gateway before STT?

The **speaker verification gateway** example is designed to sit before **STT**, **ASR**, or another downstream audio consumer.

The pattern is simple:

1. Incoming microphone audio is blocked by default.
2. The gateway evaluates whether the audio matches the enrolled speaker.
3. When the target speaker is identified, the gateway opens.
4. A small **pre-buffer** is flushed so the beginning of the utterance is preserved.
5. Downstream STT continues receiving audio while the gate remains open.

This is useful because it can:

- Reduce unwanted transcriptions from background speakers.
- Improve privacy by forwarding less irrelevant audio to downstream systems.
- Lower compute costs when STT is expensive or remote.
- Improve user isolation in shared environments.

In other words, a **speaker verification gateway before STT** helps isolate the intended user voice before transcription begins.

## Example flows in this repository

### 1. Speaker onboarding

Use [example/speaker_id_onboarding.py](../example/speaker_id_onboarding.py) or [example_windows/speaker_id_onboarding.py](../example_windows/speaker_id_onboarding.py).

This flow:

- Records multiple short microphone samples
- Creates speaker embeddings
- Saves an `sv_enrollment.json` file

That enrollment JSON can then be reused for live speaker verification, wake word speaker gating, or a gateway before STT.

Typical usage:

```bash
cd example
python speaker_id_onboarding.py
```

### 2. Speaker verification from microphone audio

Use [example/speaker_id_verification.py](../example/speaker_id_verification.py) or [example_windows/speaker_id_verification.py](../example_windows/speaker_id_verification.py).

This flow:

- Loads the saved enrollment JSON
- Continuously verifies live microphone audio
- Prints a score and match status

Typical usage:

```bash
cd example
python speaker_id_verification.py --enrollment sv_enrollment.json
```

### 3. Wake word with speaker verification

Use [example/wakeword_with_speaker_id.py](../example/wakeword_with_speaker_id.py) or [example_windows/wakeword_with_speaker_id.py](../example_windows/wakeword_with_speaker_id.py).

This flow combines:

- **Wake word detection**
- **Speaker verification**
- **External audio feeding**

The example passes speaker-related settings directly in the `KeywordDetection` model configuration:

```python
{
    "model_path": str(keyword_model_path),
    "callback_function": wakeword_callback,
    "threshold": args.keyword_threshold,
    "buffer_cnt": args.keyword_buffer_cnt,
    "wait_time": args.keyword_wait_ms,
    "speaker_id_enrollment_path": enrollment_path,
    "speaker_id_hop_seconds": args.speaker_hop_seconds,
}
```

This is the main example to use when a **wake word should only trigger for the enrolled speaker**.

Typical usage:

```bash
cd example
python wakeword_with_speaker_id.py --enrollment sv_enrollment.json
```

### 4. Speaker verification gateway before STT

Use [example/speaker_id_gateway.py](../example/speaker_id_gateway.py) or [example_windows/speaker_id_gateway.py](../example_windows/speaker_id_gateway.py).

This example shows how to put a **speaker verification gateway** in front of a downstream sink that represents **speech-to-text**, **ASR**, or another consumer.

Typical usage:

```bash
cd example
python speaker_id_gateway.py --enrollment sv_enrollment.json
```

Important gateway parameters:

- `pre_ms`: how much audio to buffer before the gate opens
- `gate_hangover_ms`: how long to keep forwarding audio after the last positive match

## Recommended architecture

For many applications, the most practical pipeline is:

1. **Onboard the speaker** and save `sv_enrollment.json`.
2. Run **wake word detection with speaker verification** if the wake phrase itself should be speaker-aware.
3. After wake-up, place a **speaker verification gateway before STT** so only the target user voice is forwarded into speech recognition.
4. Send the resulting transcript into **speech to intent** or a conversational assistant.

This pattern works well for:

- Smart home wake words
- Automotive or marine voice controls
- Clinical or hospital voice tools
- Industrial control panels
- Shared tablets, kiosks, and room devices

## SEO-relevant terms covered by this repo

This repository now includes practical examples for:

- Python wake word
- Custom wake word
- Wake word detection Python
- Wake word with speaker verification
- Wake word speaker identification
- Wake word speaker ID
- Speaker verification onboarding
- Speaker enrollment in Python
- Speaker verification before STT
- Speaker isolation before speech-to-text
- Voice isolation for STT
- Speech to intent after wake word

## Related docs

- [Main README](../README.md)
- [Python Wake Word API Reference](python_wake_word.md)

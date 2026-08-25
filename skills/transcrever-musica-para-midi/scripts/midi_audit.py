#!/usr/bin/env python3
"""Audit Standard MIDI Files without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import defaultdict, deque
from pathlib import Path


class MidiError(ValueError):
    pass


def read_vlq(data: bytes, pos: int) -> tuple[int, int]:
    value = 0
    for _ in range(4):
        if pos >= len(data):
            raise MidiError("VLQ truncado")
        byte = data[pos]
        pos += 1
        value = (value << 7) | (byte & 0x7F)
        if not byte & 0x80:
            return value, pos
    raise MidiError("VLQ excede quatro bytes")


def require(data: bytes, pos: int, size: int, label: str) -> bytes:
    end = pos + size
    if end > len(data):
        raise MidiError(f"evento truncado: {label}")
    return data[pos:end]


def parse_track(data: bytes, index: int) -> dict:
    pos = 0
    tick = 0
    running_status = None
    active: dict[tuple[int, int], deque[int]] = defaultdict(deque)
    stats = {
        "index": index,
        "name": None,
        "end_tick": 0,
        "notes": 0,
        "channels": set(),
        "programs": {},
        "tempos": [],
        "time_signatures": [],
        "orphan_note_offs": [],
        "stuck_notes": [],
        "zero_duration_notes": [],
        "end_of_track": False,
    }

    while pos < len(data):
        delta, pos = read_vlq(data, pos)
        tick += delta
        if pos >= len(data):
            raise MidiError(f"faixa {index}: status ausente")

        status = data[pos]
        if status < 0x80:
            if running_status is None:
                raise MidiError(f"faixa {index}: running status sem status anterior")
            status = running_status
        else:
            pos += 1

        if status == 0xFF:
            running_status = None
            meta_type = require(data, pos, 1, "tipo meta")[0]
            pos += 1
            length, pos = read_vlq(data, pos)
            payload = require(data, pos, length, "payload meta")
            pos += length
            if meta_type == 0x03:
                stats["name"] = payload.decode("utf-8", errors="replace")
            elif meta_type == 0x2F:
                stats["end_of_track"] = True
                if length != 0:
                    raise MidiError(f"faixa {index}: End of Track inválido")
            elif meta_type == 0x51 and length == 3:
                micros = int.from_bytes(payload, "big")
                stats["tempos"].append({"tick": tick, "microseconds_per_quarter": micros})
            elif meta_type == 0x58 and length >= 4:
                stats["time_signatures"].append(
                    {"tick": tick, "numerator": payload[0], "denominator": 2 ** payload[1]}
                )
            continue

        if status in (0xF0, 0xF7):
            running_status = None
            length, pos = read_vlq(data, pos)
            require(data, pos, length, "SysEx")
            pos += length
            continue

        if status >= 0xF0:
            raise MidiError(f"faixa {index}: status de sistema 0x{status:02X} não suportado")

        running_status = status
        kind = status & 0xF0
        channel = status & 0x0F
        width = 1 if kind in (0xC0, 0xD0) else 2
        payload = require(data, pos, width, "evento de canal")
        pos += width
        stats["channels"].add(channel + 1)

        if kind == 0xC0:
            stats["programs"][str(channel + 1)] = payload[0]
        elif kind == 0x90 and payload[1] > 0:
            active[(channel, payload[0])].append(tick)
            stats["notes"] += 1
        elif kind == 0x80 or (kind == 0x90 and payload[1] == 0):
            key = (channel, payload[0])
            if not active[key]:
                stats["orphan_note_offs"].append(
                    {"tick": tick, "channel": channel + 1, "pitch": payload[0]}
                )
            else:
                start = active[key].popleft()
                if start == tick:
                    stats["zero_duration_notes"].append(
                        {"tick": tick, "channel": channel + 1, "pitch": payload[0]}
                    )

    for (channel, pitch), starts in active.items():
        for start in starts:
            stats["stuck_notes"].append(
                {"start_tick": start, "channel": channel + 1, "pitch": pitch}
            )
    stats["end_tick"] = tick
    stats["channels"] = sorted(stats["channels"])
    return stats


def audit(path: Path) -> dict:
    data = path.read_bytes()
    if require(data, 0, 4, "cabeçalho") != b"MThd":
        raise MidiError("assinatura MThd ausente")
    header_length = struct.unpack(">I", require(data, 4, 4, "tamanho do cabeçalho"))[0]
    if header_length < 6:
        raise MidiError("cabeçalho MIDI curto")
    fmt, declared_tracks, division = struct.unpack(
        ">HHH", require(data, 8, 6, "cabeçalho MIDI")
    )
    if fmt not in (0, 1, 2):
        raise MidiError(f"formato SMF inválido: {fmt}")
    pos = 8 + header_length
    tracks = []
    for index in range(declared_tracks):
        if require(data, pos, 4, "MTrk") != b"MTrk":
            raise MidiError(f"faixa {index}: assinatura MTrk ausente")
        length = struct.unpack(">I", require(data, pos + 4, 4, "tamanho MTrk"))[0]
        payload = require(data, pos + 8, length, "dados MTrk")
        tracks.append(parse_track(payload, index))
        pos += 8 + length

    errors = []
    warnings = []
    if pos != len(data):
        warnings.append(f"{len(data) - pos} bytes extras após a última faixa")
    if fmt == 0 and declared_tracks != 1:
        errors.append("SMF tipo 0 deve conter exatamente uma faixa")
    if fmt == 1 and declared_tracks < 2:
        warnings.append("SMF tipo 1 com menos de duas faixas")
    if division & 0x8000:
        timing = {"mode": "smpte", "raw": division}
        warnings.append("divisão SMPTE: confirmar compatibilidade com o destino")
    else:
        timing = {"mode": "ppq", "ticks_per_quarter": division}
        if division < 96:
            warnings.append("PPQ baixa; microtiming e tuplets podem perder precisão")

    for track in tracks:
        if track["orphan_note_offs"]:
            errors.append(f"faixa {track['index']}: note-offs órfãos")
        if track["stuck_notes"]:
            errors.append(f"faixa {track['index']}: notas presas")
        if track["zero_duration_notes"]:
            warnings.append(f"faixa {track['index']}: notas de duração zero")
        if track["notes"] and not track["name"]:
            warnings.append(f"faixa {track['index']}: faixa musical sem nome")
        if not track["end_of_track"]:
            warnings.append(f"faixa {track['index']}: metaevento End of Track ausente")

    has_tempo = any(track["tempos"] for track in tracks)
    has_meter = any(track["time_signatures"] for track in tracks)
    if not has_tempo:
        warnings.append("nenhum metaevento de tempo; reprodução assumirá 120 BPM")
    if not has_meter:
        warnings.append("nenhum metaevento de compasso")

    return {
        "file": str(path),
        "format": fmt,
        "declared_tracks": declared_tracks,
        "timing": timing,
        "tracks": tracks,
        "errors": errors,
        "warnings": warnings,
        "passed": not errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("midi", type=Path)
    parser.add_argument("--json", type=Path, dest="json_path")
    args = parser.parse_args()
    try:
        report = audit(args.midi)
    except (OSError, MidiError, struct.error) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json_path:
        args.json_path.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

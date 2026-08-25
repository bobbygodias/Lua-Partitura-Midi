from __future__ import annotations

import importlib.util
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


MIDI_AUDIT = load_module(
    "midi_audit",
    ROOT / "skills/transcrever-musica-para-midi/scripts/midi_audit.py",
)
SCORE_AUDIT = load_module(
    "musicxml_audit",
    ROOT / "skills/escrever-partituras-corretamente/scripts/musicxml_audit.py",
)


def midi_track(payload: bytes) -> bytes:
    return b"MTrk" + struct.pack(">I", len(payload)) + payload


def good_midi() -> bytes:
    header = b"MThd" + struct.pack(">IHHH", 6, 1, 2, 480)
    conductor = (
        b"\x00\xff\x03\x09Conductor"
        b"\x00\xff\x51\x03\x07\xa1\x20"
        b"\x00\xff\x58\x04\x04\x02\x18\x08"
        b"\x00\xff\x2f\x00"
    )
    piano = (
        b"\x00\xff\x03\x05Piano"
        b"\x00\xc0\x00"
        b"\x00\x90\x3c\x64"
        b"\x83\x60\x80\x3c\x40"
        b"\x00\xff\x2f\x00"
    )
    return header + midi_track(conductor) + midi_track(piano)


GOOD_XML = """<?xml version="1.0" encoding="UTF-8"?>
<score-partwise version="4.0">
  <work><work-title>Teste Lua</work-title></work>
  <identification><creator type="composer">Lua</creator></identification>
  <part-list>
    <score-part id="P1"><part-name>Piano</part-name></score-part>
  </part-list>
  <part id="P1">
    <measure number="1">
      <attributes>
        <divisions>1</divisions>
        <time><beats>4</beats><beat-type>4</beat-type></time>
      </attributes>
      <note>
        <pitch><step>C</step><octave>4</octave></pitch>
        <duration>4</duration><voice>1</voice><type>whole</type>
      </note>
    </measure>
  </part>
</score-partwise>
"""


class MidiAuditTests(unittest.TestCase):
    def test_valid_multitrack_midi_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "good.mid"
            path.write_bytes(good_midi())
            report = MIDI_AUDIT.audit(path)
        self.assertTrue(report["passed"])
        self.assertEqual(report["declared_tracks"], 2)
        self.assertEqual(report["tracks"][1]["notes"], 1)

    def test_stuck_note_fails(self):
        data = good_midi()
        first_track_length = struct.unpack(">I", data[18:22])[0]
        second_track_offset = 14 + 8 + first_track_length
        bad_piano = (
            b"\x00\xff\x03\x05Piano"
            b"\x00\xc0\x00"
            b"\x00\x90\x3c\x64"
            b"\x00\xff\x2f\x00"
        )
        data = data[:second_track_offset] + midi_track(bad_piano)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.mid"
            path.write_bytes(data)
            report = MIDI_AUDIT.audit(path)
        self.assertFalse(report["passed"])
        self.assertTrue(report["tracks"][1]["stuck_notes"])


class MusicXmlAuditTests(unittest.TestCase):
    def test_valid_musicxml_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "good.musicxml"
            path.write_text(GOOD_XML, encoding="utf-8")
            report = SCORE_AUDIT.audit(path)
        self.assertTrue(report["passed"])
        self.assertEqual(report["parts"][0]["measure_count"], 1)

    def test_overfull_measure_and_open_tie_fail(self):
        bad = GOOD_XML.replace(
            "<duration>4</duration>",
            '<tie type="start"/><duration>5</duration>',
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bad.musicxml"
            path.write_text(bad, encoding="utf-8")
            report = SCORE_AUDIT.audit(path)
        self.assertFalse(report["passed"])
        self.assertTrue(any("excede compasso" in item for item in report["errors"]))
        self.assertTrue(any("tie(s) sem encerramento" in item for item in report["errors"]))

    def test_mxl_container_passes(self):
        container = """<?xml version="1.0"?>
<container version="1.0"
 xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
 <rootfiles>
  <rootfile full-path="score.musicxml"
   media-type="application/vnd.recordare.musicxml+xml"/>
 </rootfiles>
</container>"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "good.mxl"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("META-INF/container.xml", container)
                archive.writestr("score.musicxml", GOOD_XML)
            report = SCORE_AUDIT.audit(path)
        self.assertTrue(report["passed"])
        self.assertEqual(report["mxl_rootfile"], "score.musicxml")


if __name__ == "__main__":
    unittest.main()

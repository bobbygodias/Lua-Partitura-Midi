# Lua — Partitura e MIDI

<p align="center">
  <img src="assets/lua-banner.png"
       alt="Lua apresentando interfaces de partitura, piano roll, velocity e arquivo MIDI em um cenário cósmico"
       width="100%">
</p>

Projeto aberto para transformar música gravada em representação simbólica útil e produzir partituras musicalmente corretas, legíveis e verificáveis.

Lua não trata áudio → MIDI como conversão de formato nem MIDI → partitura como importação automática. O projeto divide o problema em duas habilidades independentes e encadeáveis:

| Habilidade | Entrada | Saída principal | Controle de qualidade |
|---|---|---|---|
| **Transcrever música para MIDI** | WAV, FLAC, MP3, M4A, MP4 ou stems | MIDI de performance e MIDI preparado para score | separação, múltiplos candidatos, reconstrução por instrumento, A/B re-sintetizado e auditoria SMF |
| **Escrever partituras corretamente** | MIDI, MusicXML/MXL, LilyPond, áudio, cifra, tablatura ou instrução | MusicXML, LilyPond, PDF, playback MIDI e partes | validação estrutural, musical, idiomática e gráfica |

## Baixar e instalar

### [⬇️ Baixar as duas Skills em um único ZIP](https://github.com/bobbygodias/Lua-Partitura-Midi/raw/refs/heads/main/dist/Lua-Partitura-Midi-Skills.zip)

O pacote contém as duas pastas completas, um guia de instalação e a licença de domínio público. O checksum está em [`dist/Lua-Partitura-Midi-Skills.zip.sha256`](dist/Lua-Partitura-Midi-Skills.zip.sha256).

No ChatGPT Work com Skills habilitadas, anexe o ZIP a uma conversa normal e peça:

```text
@skill-creator Instale e valide as duas habilidades contidas neste arquivo.
```

No Codex, descompacte as duas pastas em `$HOME/.agents/skills/` para uso pessoal ou em `.agents/skills/` na raiz de um repositório para uso somente naquele projeto.

Veja o passo a passo completo, incluindo outras plataformas compatíveis com Agent Skills, em **[INSTALACAO.md](INSTALACAO.md)**. A estrutura e a ativação de Skills no ChatGPT e Codex também estão descritas na [documentação oficial da OpenAI](https://learn.chatgpt.com/docs/build-skills).

## Princípio central

Uma rede neural produz evidência candidata. A entrega final exige reconciliação musical e testes. O projeto nunca considera uma saída automática “correta” apenas porque um programa conseguiu abri-la.

## Estrutura

```text
skills/
  transcrever-musica-para-midi/
    SKILL.md
    scripts/midi_audit.py
    references/
  escrever-partituras-corretamente/
    SKILL.md
    scripts/musicxml_audit.py
    references/
tests/
  test_auditors.py
dist/
  Lua-Partitura-Midi-Skills.zip
  Lua-Partitura-Midi-Skills.zip.sha256
```

## Auditores portáteis

Os dois auditores principais usam somente a biblioteca-padrão do Python. A validação XSD de MusicXML é opcional e usa `lxml` quando fornecido um schema.

```bash
python3 skills/transcrever-musica-para-midi/scripts/midi_audit.py musica.mid
python3 skills/escrever-partituras-corretamente/scripts/musicxml_audit.py partitura.musicxml
python3 -m unittest discover -s tests -v
```

## Ferramentas recomendadas

O pipeline admite backends substituíveis. As referências atuais incluem:

- [Basic Pitch](https://github.com/spotify/basic-pitch) para transcrição polifônica de fonte isolada;
- [Demucs](https://github.com/facebookresearch/demucs) para separação de fontes;
- [MT3](https://github.com/magenta/mt3) e [YourMT3](https://github.com/mimbres/yourmt3) para candidatos multi-instrumento;
- [Omnizart](https://github.com/Music-and-Culture-Technology-Lab/omnizart) para instrumentos, voz, acordes, beat e bateria;
- [Beat This](https://github.com/CPJKU/beat_this) para beats e downbeats;
- [MusicXML 4.0](https://www.w3.org/2021/06/musicxml40/) como formato canônico de intercâmbio;
- [LilyPond](https://lilypond.org/) e [MuseScore Studio](https://musescore.org/) para gravação, interoperabilidade e renderização.

Os modelos não são incorporados ao repositório. Cada execução deve registrar backend, versão, parâmetros e testes realmente realizados.

## Domínio público

As ideias, instruções e o código original deste projeto são livres e sem
embaraços, dedicados ao domínio público por meio de
[The Unlicense](https://unlicense.org/). Qualquer pessoa pode copiar, modificar,
publicar, usar, compilar, vender ou distribuir o material, para qualquer
finalidade, sem pedir autorização e sem obrigação de atribuição.

Dependências externas não são incorporadas ao projeto e mantêm suas próprias
licenças.

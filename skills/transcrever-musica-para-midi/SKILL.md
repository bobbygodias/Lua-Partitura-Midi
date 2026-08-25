---
name: transcrever-musica-para-midi
description: Transcrever áudio musical para MIDI multifaixa fiel, editável e auditado. Usar quando o usuário fornecer ou indicar WAV, FLAC, MP3, M4A, MP4, stems ou gravações e pedir áudio para MIDI, identificação de notas por instrumento, reconstrução simbólica, MIDI para uma IA compreender a música, extração de bateria/melodia/harmonia, ou preparação de MIDI para partitura. Aplicar separação de fontes, estimativa de andamento e compasso, transcrição especializada por instrumento, reconciliação musical e comparação auditiva; evitar conversão monolítica e não revisada.
---

# Transcrever música para MIDI

Produzir uma reconstrução musical verificável, não uma nuvem de notas. Tratar a transcrição automática como geração de candidatos; decidir e corrigir com base no áudio, na estrutura musical e na re-síntese.

## Princípios obrigatórios

- Preservar o áudio original sem alteração.
- Preferir stems originais. Separar o mix somente quando stems não existirem.
- Não tratar quantização, detecção de acordes ou uma única rede neural como verdade.
- Manter separadas evidência, inferência e correção musical.
- Não inventar instrumentos, notas, compassos, tonalidade ou articulações ocultas pelo mix.
- Representar incerteza no relatório e, quando necessário, entregar alternativas curtas para o trecho ambíguo.
- Gerar dois MIDIs quando a finalidade exigir simultaneamente expressão e notação:
  - `*.performance.mid`: microtiming, dinâmica, sustain e pitch bends relevantes;
  - `*.score-prep.mid`: grade musical limpa, vozes separáveis e durações adequadas à notação.

## Fluxo

### 1. Definir a finalidade

Confirmar ou inferir com prudência:

- instrumento isolado, stems ou mix estéreo;
- MIDI de performance, MIDI para partitura ou ambos;
- instrumentos prioritários;
- necessidade de voz cantada como linha melódica, letra ou nenhuma das duas;
- preservação de rubato, swing, compassos alternados e mudanças de andamento.

Não bloquear o trabalho por metadados dispensáveis. Adotar ambos os MIDIs como padrão quando o usuário apenas pedir uma transcrição boa.

### 2. Inspecionar e normalizar

Usar `ffprobe` para registrar codec, canais, sample rate, duração e picos. Criar uma cópia de trabalho WAV PCM, sem sobrescrever o original. Não normalizar loudness antes da análise de dinâmica; criar uma versão auxiliar somente se necessário.

Detectar silêncio inicial, contagem, anacruse e final sustentado. Manter o deslocamento temporal documentado.

### 3. Mapear a estrutura rítmica

Estimar beats e downbeats com pelo menos um rastreador moderno e conferir contra transientes, frases e harmonia. Ler [references/pipeline.md](references/pipeline.md) para seleção de ferramentas.

Construir uma tempo map quando houver drift, rubato ou mudança deliberada. Não forçar uma faixa viva a BPM constante. Registrar compasso, anacruse e mudanças de métrica como hipóteses até a revisão musical.

### 4. Produzir candidatos complementares

Para mix completo:

1. Gerar uma transcrição multi-instrumento direta quando houver backend compatível.
2. Separar fontes e gerar candidatos por stem.
3. Usar transcritor especializado para bateria e, quando necessário, para voz.
4. Comparar os candidatos; nunca concatená-los cegamente.

Para stems ou instrumento solo, pular a separação. Basic Pitch funciona melhor com um instrumento por vez; usar sua saída como candidato, não como produto final.

### 5. Reconstruir musicalmente

- Remover duplicatas, oitavas espúrias, notas de vazamento e ataques sem sustentação audível.
- Corrigir note-offs, durações e legato pelo envelope real.
- Separar vozes quando linhas simultâneas têm condução própria.
- Preservar notas de passagem e síncopes; não quantizar tudo à divisão mais próxima.
- Mapear instrumentos para programas coerentes e nomear todas as faixas.
- Usar canal MIDI 10 para percussão General MIDI, salvo exigência diferente.
- Preservar velocities como dinâmica relativa, evitando clones de velocidade.
- Manter pitch bend apenas quando expressivo e intencional; remover jitter de afinação.
- Conservar automações relevantes, como sustain, quando suportadas pela evidência.

### 6. Gerar e auditar

Executar:

```bash
python3 scripts/midi_audit.py caminho/arquivo.mid --json caminho/auditoria.json
```

Resolver todos os erros. Revisar cada aviso no contexto do áudio. O auditor verifica estrutura SMF, eventos truncados, notas órfãs ou presas, durações zero, canais, programas, metadados de tempo/compasso e organização multifaixa.

Re-sintetizar cada faixa e o conjunto. Fazer A/B por seções, começando por introdução, primeira mudança estrutural, trecho mais denso e final. Silenciar faixas alternadamente para localizar notas fantasmas e omissões.

Aplicar os critérios de [references/quality-gates.md](references/quality-gates.md). Se não houver ambiente para executar uma etapa, declarar precisamente a etapa pendente; nunca marcar como aprovada.

## Entrega

Entregar, conforme aplicável:

- `titulo.performance.mid`;
- `titulo.score-prep.mid`;
- `titulo.tempo-map.csv`;
- `titulo.transcription-report.md`;
- `titulo.midi-audit.json`;
- stems ou áudios de conferência apenas quando solicitados ou necessários ao diagnóstico.

No relatório, registrar fontes, ferramentas e versões, escolhas de instrumento, BPM/compassos, trechos ambíguos, correções manuais ou inferidas e quais testes realmente passaram.

Quando o objetivo seguinte for partitura, encaminhar o `score-prep.mid` e o relatório para `$escrever-partituras-corretamente`. MIDI é performance simbólica; não é, por si só, uma partitura correta.

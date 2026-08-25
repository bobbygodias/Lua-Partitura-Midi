# Pipeline de transcrição

## Seleção de ferramentas

Escolher ferramentas pela fonte e pelo instrumento. Confirmar versões e requisitos nas fontes oficiais antes de instalar.

| Etapa | Primeira opção | Alternativa | Observação |
|---|---|---|---|
| Inspeção/conversão | FFmpeg/ffprobe | SoX | Preservar original e offset |
| Separação | Demucs v4 | backend equivalente disponível | `htdemucs_ft` para quatro stems; `htdemucs_6s` pode ajudar com guitarra/piano, mas exige revisão de vazamento |
| Multi-instrumento | YourMT3+ ou MT3 | Omnizart | Usar como candidato estrutural |
| Instrumento harmônico isolado | Basic Pitch | Omnizart | Basic Pitch é polifônico e preserva bends, mas funciona melhor com uma fonte por vez |
| Voz | transcritor vocal dedicado | F0 + segmentação por notas | Não confundir vibrato com novas notas |
| Bateria | Omnizart Drum ou ADTOF compatível | detecção de onsets por classes | Mapear para General MIDI no canal 10 |
| Beat/downbeat | Beat This | madmom/Omnizart beat | Conferir métrica e anacruse musicalmente |
| Manipulação MIDI | mido/pretty_midi | miditoolkit | Manter PPQ suficiente para microtiming |
| Re-síntese | FluidSynth + SoundFont conhecido | sintetizador/DAW disponível | Guardar nome do SoundFont no relatório |

Fontes primárias:

- <https://github.com/spotify/basic-pitch>
- <https://github.com/facebookresearch/demucs>
- <https://github.com/magenta/mt3>
- <https://github.com/mimbres/yourmt3>
- <https://github.com/Music-and-Culture-Technology-Lab/omnizart>
- <https://github.com/CPJKU/beat_this>

## Sequência recomendada

1. Converter a cópia de trabalho para WAV PCM na frequência aceita pelo backend.
2. Obter tempo, downbeats e possíveis mudanças métricas.
3. Executar a transcrição multi-instrumento direta.
4. Separar stems e executar transcritores específicos.
5. Alinhar todas as saídas ao mesmo tempo absoluto e à mesma PPQ.
6. Para cada instrumento e seção, escolher a evidência mais convincente.
7. Corrigir ataques, durações, oitavas, vazamentos, bends e velocities.
8. Gerar `performance.mid` antes da quantização editorial.
9. Derivar `score-prep.mid` com quantização dependente do compasso e da frase.
10. Auditar, re-sintetizar e revisar por seções.

## Quantização musical

- Calcular a grade por trecho, não globalmente.
- Preservar swing como proporção ou indicação, evitando alternância caótica de tercinas.
- Tratar ornamentos como ornamentos quando a função musical justificar.
- Usar ties no estágio de partitura; em MIDI, preservar a nota sustentada sem reataque artificial.
- Não corrigir notas cromáticas apenas porque estão fora da tonalidade estimada.
- Em bateria, priorizar o onset; em pads e cordas, priorizar início e fim de envelope.

## Reconciliação de candidatos

Pontuar uma nota candidata por:

- energia ou saliência no stem correspondente;
- concordância entre modelos;
- alinhamento com onset audível;
- continuidade da voz;
- faixa e técnica plausíveis do instrumento;
- função harmônica, sem usá-la para apagar dissonâncias reais.

Conservar uma nota de baixa confiança somente quando houver evidência auditiva. Marcar passagens que dependam de inferência.

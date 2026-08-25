---
name: escrever-partituras-corretamente
description: Criar, transcrever, corrigir, editar e validar partituras com rigor musical e editorial a partir de MIDI, MusicXML, MXL, LilyPond, áudio, cifras, tablatura, letras ou instruções. Usar quando o usuário pedir partitura, score, arranjo notado, MusicXML, LilyPond, PDF musical, partes individuais, grade orquestral, notação de bateria, correção de compassos/vozes/ritmos/acidentes/ligaduras, ou verificação estrita de uma partitura. Produzir notação semanticamente correta, legível, tocável e renderizada; não confundir importação automática ou XML válido com partitura musicalmente correta.
---

# Escrever partituras corretamente

Tratar partitura como uma representação semântica destinada a músicos, não como impressão literal de eventos MIDI. Exigir quatro níveis de correção: estrutural, musical, idiomático e gráfico.

## Fontes e entregas

Aceitar:

- MIDI de performance ou preparado para score;
- MusicXML/MXL, LilyPond ou arquivos de editores;
- áudio com ou sem stems;
- melodia, cifras, tablatura, letra ou especificação textual.

Usar MusicXML 4.0 partwise como formato canônico de intercâmbio, salvo exigência diferente. Entregar, quando o ambiente permitir:

- `titulo.musicxml` ou `titulo.mxl`;
- `titulo.ly`;
- `titulo.pdf`;
- `titulo.playback.mid`;
- partes separadas quando houver conjunto;
- `titulo.score-audit.json`;
- `titulo.editorial-report.md`.

## Fluxo editorial

### 1. Fixar intenção e instrumentação

Determinar conjunto, instrumentos transpositores, nível dos intérpretes, finalidade da partitura, tamanho de página e convenção editorial. Se o usuário não especificar, adotar partitura de concerto, tamanho A4 e convenções modernas comuns, registrando as escolhas.

Não pedir confirmação para decisões reversíveis e evidentes. Perguntar quando a escolha alterar materialmente alturas escritas, dificuldade, número de partes ou idioma da letra.

### 2. Auditar a fonte

Para MIDI, distinguir performance de notação. Ler tempo map, compassos, canais, programas, sustain, bends e nomes de faixas. Não importar e exportar sem reconstruir vozes e durações.

Para áudio, usar `$transcrever-musica-para-midi` primeiro quando faltar uma representação simbólica confiável.

Para MusicXML/MXL, executar:

```bash
python3 scripts/musicxml_audit.py caminho/partitura.musicxml --json caminho/auditoria.json
```

Revisar erros e avisos; o auditor não substitui a revisão musical nem a renderização.

### 3. Construir o esqueleto

Definir antes das notas:

- título, autoria e créditos conhecidos;
- ordem, agrupamento e nomes das partes;
- clave, transposição, armadura e tessitura;
- compasso, anacruse, mudanças métricas e tempo;
- numeração de compassos, marcas de ensaio e forma;
- pauta e convenção de percussão.

Não deduzir autoria ou título ausentes.

### 4. Reconstruir ritmo e vozes

- Preencher exatamente cada compasso, incluindo pausas e vozes ocultas quando semanticamente necessárias.
- Separar vozes por continuidade musical, não apenas por altura.
- Usar ligaduras de prolongamento para atravessar tempos, grupos métricos ou barras; não rearticular uma nota sustentada.
- Preferir valores, pausas e agrupamentos que revelem o pulso.
- Notar síncopes, swing, quiálteras, anacruses e fermatas de modo explícito.
- Não quantizar rubato expressivo como ritmos impossíveis; representar a intenção e usar indicações de tempo quando apropriado.

Aplicar [references/notation-rules.md](references/notation-rules.md).

### 5. Escrever alturas e técnicas

- Escolher enarmonia pela tonalidade, função harmônica, condução de vozes e legibilidade.
- Manter acidentes consistentes dentro do compasso e da frase.
- Escrever instrumentos transpositores na altura correta para a parte e conservar score em concerto ou transposto conforme definido.
- Usar tablatura somente junto de afinação, corda e casa coerentes.
- Escrever oitavas, harmônicos, bends, slides e técnicas instrumentais apenas quando suportados pela fonte ou solicitados.

### 6. Articular frase e execução

Adicionar dinâmica, hairpins, acentos, staccato, tenuto, slurs, respirações, pedais, baquetas, arco, dedilhado e texto somente quando houver evidência ou intenção editorial. Diferenciar:

- tie: duração de uma mesma altura;
- slur: frase/articulação;
- lyric extender: duração silábica;
- ottava: convenção de leitura, não transposição permanente.

Para letra, alinhar sílabas, elisões, hífens e melismas nota a nota. Preservar ortografia fornecida e sinalizar palavras inaudíveis em vez de inventá-las.

### 7. Gravar bateria e percussão

Ler [references/percussion.md](references/percussion.md). Usar instrumento não afinado, notehead, posição de pauta, voz, stem e técnica compatíveis. Distinguir ao menos chimbal fechado/aberto/pedal, ride/crash, rimshot/cross-stick e peças de bateria quando presentes. Não inferir mão direita ou esquerda sem necessidade.

### 8. Gravar e diagramar

Usar MusicXML para semântica e interoperabilidade. Gerar LilyPond para gravação tipográfica quando conveniente, ou renderizar pelo MuseScore Studio. Corrigir colisões, viradas de página, quebras ruins, sistemas órfãos, espaçamento, letras, voltas e marcas de ensaio.

Não inserir quebras manuais antes de estabilizar o conteúdo musical.

### 9. Validar em quatro camadas

Aplicar [references/quality-gates.md](references/quality-gates.md):

1. **Estrutural:** parse, XSD quando disponível, referências, durações, ties/tuplets e consistência interna.
2. **Musical:** alturas, ritmo, métrica, vozes, harmonia, forma e correspondência com a fonte.
3. **Idiomática:** tessitura, técnica, respiração, dedilhado, percussão e tocabilidade.
4. **Gráfica:** renderização visual de todas as páginas e partes.

Importar o MusicXML em ao menos um gravador maduro. Quando possível, testar MuseScore e LilyPond independentemente. Ouvir o playback e comparar com a fonte. Para uma partitura destinada à execução, revisar também as partes extraídas.

Não declarar “estritamente correta” se alguma camada não foi executada. Dizer precisamente o que foi validado e o que permanece pendente.

## Critério de encerramento

Concluir somente quando:

- nenhum erro estrutural permanecer;
- todos os compassos e vozes estiverem explicáveis;
- nenhuma nota ou ritmo ambíguo estiver escondido como certeza;
- transposições e percussão estiverem corretas;
- PDF e partes tiverem sido inspecionados visualmente;
- playback e fonte tiverem sido comparados;
- relatório editorial registrar escolhas e ressalvas.

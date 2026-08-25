# Portões de qualidade da partitura

## 1. Estrutural

- Parse MusicXML/MXL sem erro.
- Validar contra o XSD MusicXML correspondente quando disponível.
- Conferir IDs de partes, referências, divisions, compassos e durações.
- Conferir pares de ties, tuplets, slurs, hairpins, ottavas e pedais.
- Importar sem perda material em um gravador maduro.
- Compilar LilyPond sem erro quando `.ly` fizer parte da entrega.

## 2. Musical

- Comparar alturas, ataques, durações, tempo map, métrica e forma com a fonte.
- Conferir vozes internas e notas sustentadas isoladamente.
- Conferir enarmonia e armadura em cada mudança tonal.
- Conferir anacruse, compassos irregulares, swing e quiálteras.
- Ouvir playback por parte e conjunto.

## 3. Idiomático

- Verificar tessituras, transposições e técnicas.
- Conferir respirações, saltos, posições, dedilhados e mudanças de instrumento.
- Conferir corda/casa na tablatura.
- Conferir mapa, vozes e técnicas de percussão.
- Marcar passagens deliberadamente difíceis; não deixar impossibilidades acidentais.

## 4. Gráfico

- Renderizar todas as páginas e partes.
- Inspecionar colisões, símbolos cortados, sobreposição de letras e texto.
- Conferir densidade por sistema, viradas de página e compassos isolados.
- Manter cabeçalhos, título, créditos, numeração e marcas de ensaio consistentes.
- Conferir tamanho real de impressão e margens.

## 5. Interoperabilidade

- Abrir MusicXML/MXL no editor-alvo.
- Fazer round-trip apenas como teste auxiliar; comparar significado musical, não o texto XML.
- Conferir se playback MIDI preserva forma, programas, canal de percussão, tempo e dinâmica essencial.
- Registrar quais aplicativos e versões foram usados.

## Estado final

- **Final validado:** todos os portões aplicáveis foram executados.
- **Final com ressalvas:** entrega utilizável, com ambiguidades musicais identificadas.
- **Rascunho editorial:** ainda falta reconstrução, renderização ou comparação auditiva.

Validade XML isolada nunca autoriza o estado “Final validado”.

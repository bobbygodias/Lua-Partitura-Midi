# Regras de notação

## Ritmo e métrica

- Fazer a grafia revelar a hierarquia do compasso.
- Em métricas simples, evitar atravessar o centro do compasso com um único valor quando a leitura rítmica ficar ambígua; usar ties.
- Em métricas compostas, agrupar pela unidade pontuada, salvo síncope intencional.
- Usar ponto de aumento quando ele simplificar a leitura dentro do grupo métrico; usar tie quando a duração atravessar uma fronteira estrutural.
- Notar anacruse como compasso incompleto/implícito e conferir sua relação com o compasso final quando aplicável.
- Especificar a razão de quiáltera e manter início/fim coerentes. Não usar quiáltera para mascarar drift de performance.
- Em swing, preferir indicação textual e colcheias regulares quando a convenção do gênero for inequívoca; grafar a divisão ternária quando ela for estrutural.
- Dividir pausas conforme os mesmos grupos métricos das notas. Não usar pausas que ocultem o pulso.

## Vozes

- Criar uma nova voz quando houver independência rítmica ou melódica real.
- Manter a identidade da voz por condução, stem e registro; não alternar números de voz arbitrariamente.
- Completar a duração de cada voz ativa com pausas explícitas ou ocultas justificadas.
- Em teclado, separar mão e voz musicalmente; cross-staff não muda a identidade sonora.
- Evitar acordes falsos produzidos pela fusão de notas com ataques diferentes.

## Altura e enarmonia

- Escrever a função tonal/harmônica provável sem corrigir cromatismos reais.
- Preferir movimento diatônico visualmente claro e intervalos legíveis.
- Conservar coerência entre voz, acorde, armadura e resolução.
- Usar acidentes de cortesia quando reduzirem ambiguidade; distingui-los dos acidentes obrigatórios.
- Conferir oitava científica, clave e transposição em conjunto.

## Ties, slurs e articulações

- Tie conecta a mesma altura e preserva um único ataque.
- Slur agrupa frase, legato ou técnica; não altera duração.
- Uma nota pode terminar um tie e iniciar outro; codificar ambos os eventos.
- Articulações não substituem dinâmica nem duração exata.
- Evitar slurs gigantes gerados automaticamente sem lógica de frase ou respiração.

## Dinâmica e texto

- Colocar dinâmica no ponto em que entra em vigor.
- Fechar hairpin em dinâmica, niente ou ponto musical inequívoco.
- Evitar duplicar a mesma informação com dinâmica, velocity e texto conflitantes.
- Usar andamento, expressão, técnica e direção em categorias semânticas adequadas.
- Manter idioma, capitalização e abreviações consistentes.

## Repetições e forma

- Conferir barras de repetição, casas, segno, coda, Fine e saltos pela ordem real de execução.
- Garantir que o playback e as partes interpretem a forma de modo coerente.
- Preferir marcas de ensaio em pontos estruturais e mantê-las idênticas em score e partes.

## Instrumentos transpositores

- Registrar transposição diatônica e cromática corretamente no MusicXML.
- Conferir armadura escrita, oitava e som resultante.
- Não misturar score em concerto e partes transpostas sem indicação explícita.
- Verificar trocas de instrumento e transposição no ponto exato.

## Guitar, baixo e tablatura

- Definir número de cordas e afinação.
- Validar corda/casa contra a altura escrita e a técnica.
- Não derivar fingering unicamente da menor casa; considerar posição, frase e tocabilidade.
- Representar bends com alvo, release, prebend e extensão quando audíveis.
- Distinguir slide, glissando, hammer-on, pull-off, let ring, palm mute e harmônicos.

## Teclado

- Distribuir entre pautas por gesto e mão, não por um ponto de corte fixo.
- Preservar vozes internas, sustain e rearticulações.
- Usar pedal com início, troca e liberação coerentes.
- Evitar arpejos impossíveis sem indicação de distribuição ou arpejamento.

## Voz e letra

- Uma sílaba por evento apropriado; usar `single`, `begin`, `middle` e `end` coerentemente.
- Usar extender para melisma e elisão quando aplicável.
- Posicionar respirações e pontuação conforme frase e texto.
- Manter tessitura e respiração plausíveis; não transportar automaticamente sem autorização.

## Formatos

- Preferir `.musicxml` para MusicXML não comprimido e `.mxl` para o contêiner comprimido.
- Manter semântica de som e notação: em MusicXML, `tie` e `tied` têm papéis relacionados, mas distintos.
- Tratar MIDI como playback, não como fonte suficiente de layout, stems, enarmonia ou vozes.

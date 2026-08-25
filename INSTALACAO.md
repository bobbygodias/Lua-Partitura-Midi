# Instalação das Skills Lua

Este pacote contém duas habilidades independentes e complementares:

- `transcrever-musica-para-midi`: transforma áudio musical em MIDI multifaixa auditado, com reconstrução por instrumento;
- `escrever-partituras-corretamente`: cria, corrige e valida partituras em MusicXML/MXL, LilyPond, MIDI e PDF.

Cada pasta é uma Skill completa. Preserve sua estrutura interna: o arquivo `SKILL.md` deve permanecer na raiz da respectiva pasta, ao lado de `agents/`, `assets/`, `references/` e `scripts/`.

## Download

Baixe o pacote único:

**[Lua-Partitura-Midi-Skills.zip](https://github.com/bobbygodias/Lua-Partitura-Midi/raw/refs/heads/main/dist/Lua-Partitura-Midi-Skills.zip)**

Para conferir a integridade do arquivo, compare o SHA-256 com `dist/Lua-Partitura-Midi-Skills.zip.sha256`.

## ChatGPT Work

Quando a área de Skills estiver habilitada para a conta ou workspace:

1. Baixe `Lua-Partitura-Midi-Skills.zip`.
2. Abra uma conversa normal no ChatGPT Work.
3. Anexe o ZIP sem descompactá-lo.
4. Escreva: `@skill-creator Instale e valide as duas habilidades contidas neste arquivo.`
5. Depois da confirmação, abra **Plugins → Skills** e atualize a lista, se necessário.
6. Para chamar uma habilidade diretamente, digite `@` e escolha seu nome. O ChatGPT também pode ativá-la automaticamente quando o pedido corresponder à descrição.

As Skills pessoais e sua forma de instalação podem depender do produto, da versão do aplicativo e das permissões do workspace. A documentação oficial explica a estrutura e o uso em [Build skills](https://learn.chatgpt.com/docs/build-skills).

## Codex CLI, aplicativo desktop ou extensão de IDE

### Instalação para o usuário

1. Descompacte o ZIP.
2. Copie estas duas pastas para `$HOME/.agents/skills/`:

```text
transcrever-musica-para-midi/
escrever-partituras-corretamente/
```

3. Confirme que os caminhos terminam assim:

```text
$HOME/.agents/skills/transcrever-musica-para-midi/SKILL.md
$HOME/.agents/skills/escrever-partituras-corretamente/SKILL.md
```

4. Reabra o seletor de Skills. No Codex CLI ou na extensão de IDE, use `/skills` ou digite `$` para selecionar uma habilidade.

### Instalação somente para um projeto

Copie as duas pastas para `.agents/skills/` na raiz do repositório:

```text
meu-projeto/
  .agents/
    skills/
      transcrever-musica-para-midi/
      escrever-partituras-corretamente/
```

Esse modo mantém as Skills ligadas ao projeto, em vez de instalá-las para todos os trabalhos do usuário.

## Outras plataformas de IA

Se a plataforma adota o padrão aberto de Agent Skills:

1. descompacte o arquivo;
2. importe cada pasta como uma habilidade separada;
3. preserve `SKILL.md` na raiz e todos os recursos relativos;
4. conceda acesso ao Python somente se desejar executar os auditores incluídos;
5. teste cada Skill com um arquivo pequeno antes de uma produção extensa.

Se a plataforma não implementa Agent Skills, use o conteúdo de `SKILL.md` como instrução de sistema ou manual operacional e disponibilize `references/`, `scripts/` e `assets/` no ambiente de arquivos do agente. Nesse modo, a adaptação depende do mecanismo de extensões da própria plataforma.

## Como usar

Pedidos diretos de exemplo:

```text
Use @transcrever-musica-para-midi para transcrever este WAV em um MIDI multifaixa de performance e outro preparado para partitura. Audite os dois arquivos.
```

```text
Use @escrever-partituras-corretamente para transformar este MIDI em MusicXML e PDF, revisar vozes, compassos, acidentes, articulações e tocabilidade, e executar a auditoria final.
```

No Codex, substitua `@` por `$` quando usar a menção explícita de Skills.

## Requisitos e limites

- Os auditores `midi_audit.py` e `musicxml_audit.py` funcionam com a biblioteca-padrão do Python.
- Ferramentas externas de separação, transcrição e renderização não estão incorporadas ao ZIP; a Skill escolhe e registra os backends disponíveis no ambiente.
- Uma Skill orienta o agente e fornece validações determinísticas, mas não transforma qualquer modelo em músico perfeito. A qualidade final continua exigindo reconciliação musical e controle auditivo.

## Liberdade de uso

O projeto é dedicado ao domínio público por meio de [The Unlicense](https://unlicense.org/). É livre para copiar, modificar, publicar, usar e distribuir, sem autorização ou atribuição obrigatória. Dependências externas mantêm suas próprias licenças.

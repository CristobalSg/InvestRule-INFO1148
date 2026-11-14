# InvestRule

InvestRule es un mini lenguaje educativo para **describir y validar** reglas de
inversión y reinversión. Esta primera versión contiene un lexer con posiciones,
un parser predictivo LL(1) propio por descenso recursivo y un AST serializable.

El proyecto no ejecuta inversiones, no consulta datos financieros y no predice
resultados. Tampoco admite decimales, números negativos, aritmética, `ELSE`,
acciones múltiples ni llamadas a servicios externos.

## Requisitos y ejecución

Solo se necesita Python 3.10 o posterior; no hay dependencias externas.

Analizar texto directamente:

```bash
python main.py "WHEN ganancias > 500000 THEN REINVERTIR ganancias;"
```

Analizar un archivo UTF-8:

```bash
python main.py --file reglas.ir
```

También se puede enviar el programa por entrada estándar:

```bash
printf '%s\n' 'WHEN riesgo > 4 THEN ALERTAR inversion;' | python main.py
```

El comando imprime el AST como JSON y retorna código `0`. Un error léxico,
sintáctico o de lectura se muestra por `stderr` y retorna código `1`.

## Forma del lenguaje

Los identificadores siguen `[A-Za-z_][A-Za-z0-9_]*` y los números son enteros
no negativos (`[0-9]+`). Las palabras reservadas no distinguen mayúsculas de
minúsculas, aunque el token conserva el lexema original. Los comparadores son
`>=`, `<=`, `==`, `!=`, `>` y `<`.

Cada programa tiene una o más reglas de esta forma:

```text
WHEN <expresión> THEN <acción> <identificador>;
```

Las acciones permitidas son `REINVERTIR`, `APROBAR` y `ALERTAR`. Las
comparaciones aceptan un `ID`, un comparador y `NUM`, `TRUE` o `FALSE`. La
precedencia es `NOT > AND > OR`; se admiten `NOT` repetidos y paréntesis
anidados.

## API

```python
from src.lexer import tokenize
from src.parser import parse_text, parse_tokens

tokens = tokenize("WHEN riesgo <= 3 THEN APROBAR proyecto;")
programa = parse_tokens(tokens)
print(programa.pretty())

# Atajo equivalente:
programa = parse_text("WHEN riesgo <= 3 THEN APROBAR proyecto;")
```

`tokenize()` devuelve objetos `Token` con tipo, lexema, índice, línea y columna.
`analizador_lexico()` conserva la salida de pares `(tipo, lexema)` del notebook
original como API de compatibilidad.

## Correspondencia con la GLC congelada

El parser no usa Lark, PLY, ANTLR, yacc ni otro generador. La correspondencia
entre las 21 producciones y sus métodos es directa:

| Producciones | Método de descenso recursivo |
|---|---|
| P01 | `Parser._programa()` |
| P02-P03 | `Parser._resto_programa()` |
| P04 | `Parser._regla()` |
| P05 | `Parser._expresion()` |
| P06-P07 | `Parser._cola_or()` |
| P08 | `Parser._conjuncion()` |
| P09-P10 | `Parser._cola_and()` |
| P11-P12 | `Parser._negacion()` |
| P13-P14 | `Parser._primario()` |
| P15 | `Parser._comparacion()` |
| P16-P18 | `Parser._valor()` |
| P19-P21 | `Parser._accion()` |

Las alternativas se eligen con un solo token de anticipación. Las producciones
epsilon se toman únicamente con los FOLLOW acordados: `$` para P03,
`THEN`/`PARENT_DER` para P07 y `OR`/`THEN`/`PARENT_DER` para P10. El marcador
`EOF` es interno y el parser exige consumir la entrada completa.

## Estructura

```text
main.py              CLI
src/lexer.py         tokenización y posiciones
src/parser.py        descenso recursivo P01-P21
src/ast_nodes.py     dataclasses y serialización del AST
src/errors.py        errores léxicos y sintácticos localizados
tests/               pruebas unitarias del lexer, parser y AST
```

## Pruebas

Ejecutar toda la suite sin acceso a red:

```bash
python -m unittest discover -s tests -v
```

La suite inicial cubre entradas válidas e inválidas, reglas múltiples, entrada
vacía, consumo total, precedencia, booleanos, cero, `NOT` repetido, paréntesis
anidados y los errores de aceptación exigidos. La rúbrica final requiere además
documentar 25 o más casos (10 válidos, 10 inválidos y 5 casos límite) con sus
resultados esperados y obtenidos.

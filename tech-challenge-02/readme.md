# Documentação do Código: Algoritmo Genético com Visualização em Pygame

Este documento fornece uma descrição detalhada sobre as funcionalidades, classes e métodos
presentes no código fornecido, que implementa um algoritmo genético para otimização de tarefas
com suporte à visualização em Pygame.

Link para o código: [Algoritmo Genético com Visualização em Pygame](https://github.com/carlos-rian/fiap-pos-tech/tree/catalito/tech-challenge-02)

## Objetivo do Código

O código visa resolver problemas de distribuição de tarefas entre recursos usando um algoritmo
genético, com o objetivo de minimizar o tempo total de execução (makespan), equilibrar a carga
entre os recursos e priorizar tarefas mais importantes. Inclui visualização em tempo real para
acompanhamento do progresso.

---
## Estrutura do Código

### 1. Classes Principais

#### **Task**

- Representa uma tarefa que deve ser atribuída a um recurso.
- **Atributos:**
 - `id` (int): Identificador único da tarefa.
 - `duration` (int): Duração da tarefa em unidades de tempo.
 - `priority` (int): Prioridade da tarefa (quanto maior o valor, mais prioritária a tarefa).
Documentação do Código: Algoritmo Genético com Visualização em Pygame
- **Métodos:**
 - `__repr__`: Retorna uma representação em string da tarefa no formato `Task(id, duration,
priority)`.
 - `name`: Retorna uma string formatada contendo o nome e atributos principais da tarefa.

#### **Resource**

- Representa um recurso onde tarefas podem ser alocadas.
- **Atributos:**
 - `id` (int): Identificador único do recurso.
 - `tasks` (list[Task]): Lista de tarefas atribuídas ao recurso.
- **Métodos:**
 - `__repr__`: Retorna uma representação em string no formato `Resource(id)`.

#### **Chromosome**
- Representa uma solução candidata no algoritmo genético, indicando como as tarefas são
atribuídas aos recursos.

- **Atributos:**
 - `gene` (list[int]): Lista que mapeia tarefas a recursos. Cada elemento indica qual recurso está
atribuindo a tarefa correspondente.
 - `fitness` (float): Valor de fitness que avalia a qualidade da solução.
- **Métodos:**
 - `__lt__`: Permite comparar cromossomos com base no fitness para ordenar populações.

#### **FitnessValue**
- Representa os componentes do valor de fitness que avaliam uma solução.
Documentação do Código: Algoritmo Genético com Visualização em Pygame

- **Atributos:**
 - `makespan` (int): Tempo total necessário para concluir todas as tarefas.
 - `load_balance` (float): Desvio padrão da utilização dos recursos, avaliando o balanceamento de
carga.
 - `priority_score` (int): Soma das prioridades das tarefas alocadas.
 - `fitness` (float): Valor calculado de fitness combinando os fatores anteriores.
- **Métodos:**
 - `__repr__`: Retorna uma representação textual detalhada dos valores de fitness.
 - `__eq__`: Compara dois objetos `FitnessValue` com base em seus atributos.

#### **SelectionType**
- Enumeração para definir o tipo de seleção usado no algoritmo genético.
- **Tipos:**
 - `TOURNAMENT`: Seleção por torneio entre indivíduos.
 - `BEST_INDIVIDUALS`: Seleção baseada nos melhores indivíduos da população.
---
### 2. Funções Principais

#### **create_schedule**

Cria um cronograma para alocação de tarefas aos recursos com base em um cromossomo.

- **Argumentos:**
 - `chromosome` (Chromosome): O cromossomo representando a alocação de tarefas aos
recursos.
Documentação do Código: Algoritmo Genético com Visualização em Pygame
 - `tasks` (list[Task]): Lista de tarefas a serem agendadas.
 - `resources` (list[Resource]): Lista de recursos disponíveis para a alocação.
- **Retorno:**
 - `ScheduleReturnType`: Um dicionário onde as chaves são os IDs dos recursos e os valores são
listas de tarefas com seus tempos de início e fim.

#### **genetic_algorithm**
Implementa o algoritmo genético para otimizar a distribuição de tarefas nos recursos.
- **Argumentos:**
 - `tasks` (list[Task]): Lista de tarefas a serem otimizadas.
 - `resources` (list[Resource]): Lista de recursos disponíveis.
 - `population_size` (int): Tamanho da população inicial.
 - `generations` (int): Número de gerações para evolução.
 - `selection_type` (SelectionType): Tipo de seleção usado no algoritmo.
 - `delay` (float): Tempo de atraso para visualização em Pygame (opcional).
- **Retorno:**
 - `Chromosome`: O melhor cromossomo encontrado após as gerações.

#### **fitness_value**

Calcula os componentes de fitness para avaliar um cromossomo.
- **Argumentos:**
 - `chromosome` (Chromosome): Cromossomo sendo avaliado.
 - `tasks` (list[Task]): Lista de tarefas relacionadas ao cromossomo.
 - `resources` (list[Resource]): Lista de recursos utilizados.
- **Retorno:**
Documentação do Código: Algoritmo Genético com Visualização em Pygame
 - `FitnessValue`: Objeto contendo os valores detalhados de fitness.

#### **selection_by_tournament**
Seleciona dois cromossomos da população usando o método de torneio.
- **Argumentos:**
 - `population` (list[Chromosome]): População de cromossomos.
- **Retorno:**
 - `tuple[Chromosome, Chromosome]`: Dois cromossomos selecionados para cruzamento.

#### **selection_best_chromosome_pair**
Seleciona os dois melhores cromossomos da população com base no fitness.
- **Argumentos:**
 - `population` (list[Chromosome]): Lista de cromossomos na população.
- **Retorno:**
 - `tuple[Chromosome, Chromosome]`: Dois melhores cromossomos.

#### **crossover**
Realiza cruzamento entre dois cromossomos para gerar um descendente.
- **Argumentos:**
 - `parent1` (Chromosome): Primeiro cromossomo pai.
 - `parent2` (Chromosome): Segundo cromossomo pai.
- **Retorno:**
 - `Chromosome`: Novo cromossomo descendente.

#### **mutation**
Documentação do Código: Algoritmo Genético com Visualização em Pygame
Aplica mutação a um cromossomo, alterando aleatoriamente alguns genes.
- **Argumentos:**
 - `chromosome` (Chromosome): Cromossomo a ser mutado.
 - `num_resources` (int): Número total de recursos disponíveis.
 - `mutation_rate` (float): Taxa de probabilidade de mutação.

## Condições de Parada

As condições de parada do algoritmo genético são definidas com base nos critérios de equilíbrio de carga (load_balance), calculados pela classe `FitnessValue`. O algoritmo será encerrado quando for atingida a seguinte condição:

O load_balance entre todos os recursos for igual, ou seja, quando o desvio padrão da utilização dos recursos atingir zero (ou um valor considerado suficientemente pequeno para fins práticos, dependendo da implementação). Isso indica que as tarefas foram distribuídas uniformemente entre os recursos.

Caso essa condição não seja satisfeita, o algoritmo continuará executando as operações de seleção, cruzamento e mutação para refinar as soluções até atingir o número máximo de gerações ou outra condição de parada complementar.

Outras condições de parada opcionais incluem:

Número máximo de gerações: O algoritmo será encerrado após um número predefinido de gerações, independentemente do equilíbrio de carga.

Fitness estável: Caso o valor de fitness não apresente melhora significativa após um determinado número de gerações consecutivas, o algoritmo será interrompido.

Essas condições permitem flexibilidade na execução do algoritmo, garantindo que ele possa ser ajustado para diferentes cenários e requisitos práticos.


## Comparativo: Força Bruta vs. Algoritmo Genético

Uma comparação entre o método de força bruta e o algoritmo genético demonstra a eficiência deste último para problemas complexos de distribuição de tarefas. Seguem os principais pontos:

### Força Bruta

O método de força bruta consiste em avaliar todas as combinações possíveis de distribuição de tarefas entre os recursos para identificar a solução ótima. Embora garantido para encontrar a melhor solução, possui as seguintes desvantagens:

- **Complexidade Computacional**: Cresce exponencialmente com o número de tarefas e recursos.
- **Tempo de Execução**: Tornar-se inviável para problemas com grande escala devido ao tempo necessário para processar todas as possibilidades.

### Algoritmo Genético

O algoritmo genético utiliza operações inspiradas na evolução natural, como seleção, cruzamento e mutação, para explorar o espaço de soluções de forma eficiente. Suas vantagens incluem:

- **Eficiência**: Encontra soluções de alta qualidade em um tempo significativamente menor.
- **Escalabilidade**: Pode lidar com problemas de grande escala de maneira prática.
- **Flexibilidade**: Adapta-se facilmente a diferentes funções objetivo e restrições.

### Desempenho Comparativo

| Método           | Tempo de Execução      | Qualidade da Solução | Escalabilidade |
|-------------------|-----------------------|-----------------------|----------------|
| Força Bruta       | Muito alto            | Ótima (Garantida)     | Baixa          |
| Algoritmo Genético | Baixo/Moderado        | Alta (Não Garantida)  | Alta           |

Em testes realizados, o algoritmo genético apresentou uma redução de **ordens de magnitude no tempo de execução** em relação ao método de força bruta, mantendo uma solução muito próxima do ótimo para a maioria dos casos práticos.

Essa eficiência torna o algoritmo genético uma escolha ideal para aplicações onde o tempo é um fator crítico, como na alocação dinâmica de recursos em sistemas reais.

# WebServiceRepo
Este reposítorio servirá para o WebService do Activity Provider.

# FRS Activity Provider – Inven!RA  
Fornecedor de Simulação Robótica (FRS)  
Projeto para a disciplina de Arquiteturas de Software  

# Descrição
O FRS (Fornecedor de Simulação Robótica) é um Activity Provider desenvolvido para integrar com a arquitetura Inven!RA, permitindo aos alunos realizar simulações remotas de missões robóticas.

Este servidor implementa os 5 serviços RESTful obrigatórios definidos no documento  
*“Activity Providers na Inven!RA”*, correspondentes ao ficheiro de registo de atividade:

- `config_url` → `/config`  
- `json_params_url` → `/json_params`  
- `user_url` → `/deploy`  
- `analytics_url` → `/analytics`  
- `analytics_list_url` → `/analytics_list`  

## Padrão de Criação Utilizado
Foi identificado um caso real no projeto onde era necessário criar dinamicamente diferentes tipos de missões robóticas, dependendo do campo `activity_id`.  
Para resolver este problema de forma extensível, foi aplicado o padrão Factory Method.

Classes principais:
- `RoboticMission` (interface base)
- `ClassificationMission` (produto concreto)
- `NavigationMission` (produto concreto)
- `MissionFactory` (Factory Method)
- `/deploy` usa o padrão para instanciar a missão correta

## Tecnologias
- Python 3.10+
- Flask (para Web services RESTful)

# Endpoints do Activity Provider

### 1. `GET /config`
Página HTML com os campos de configuração da atividade.

### 2. `GET /json_params`
Lista de parâmetros que a Inven!RA deve recolher da página `/config`.

### 3. `POST /deploy`
Cria uma instância da atividade e devolve um URL para acesso à mesma.

Exemplo de corpo:
```json
{
  "activityID": "RSP_MISSAO_CLASS_001",
  "json_params": {
    "robot_type": "Braço Manipulador de 6 Eixos",
    "target_objects": 8,
    "sorting_criteria": ["cor", "tamanho"],
    "max_execution_time_s": 150,
    "programming_language": "Python"
  }
}

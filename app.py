## from flask import Flask, jsonify
## app = Flask(__name__)
## @app.route('/')
## def hello_world():
##    return 'WebService: Online!'  
## @app.route('/status')
## def status_check():
##    return jsonify({
##       "status": "OK",
##        "service": "WebServiceRepo",
##        "version": "1.0"
##    })  
## if __name__ == '__main__':
##    app.run(debug=True, port=5000)


from flask import Flask, jsonify, request
from abc import ABC, abstractmethod

app = Flask(__name__)

ACTIVITY_CONFIGS = {}
ACTIVITY_ANALYTICS = {}

class RoboticMission(ABC):
    """Interface base para missões robóticas."""

    @abstractmethod
    def load_parameters(self, config: dict):
        pass

    @abstractmethod
    def start_simulation(self) -> dict:
        pass


class ClassificationMission(RoboticMission):
    def load_parameters(self, config: dict):
        mission = config.get("mission_constraints", {})
        self.robot_type = config.get("robot_type", "Braço Manipulador de 6 Eixos")
        self.target_objects = mission.get("target_objects", 8)
        self.criteria = mission.get("sorting_criteria", ["cor", "tamanho"])

    def start_simulation(self) -> dict:
        return {
            "description": (
                f"Missão de classificação de {self.target_objects} objetos "
                f"por critérios {self.criteria}"
            ),
            "initial_progress": 0.0,
        }


class NavigationMission(RoboticMission):
    def load_parameters(self, config: dict):
        mission = config.get("mission_constraints", {})
        self.robot_type = config.get("robot_type", "Plataforma móvel")
        self.max_time = mission.get("max_execution_time_s", 150)

    def start_simulation(self) -> dict:
        return {
            "description": (
                f"Missão de navegação com tempo máximo {self.max_time} segundos"
            ),
            "initial_progress": 0.0,
        }


class MissionFactory:
    """Factory Method para criar missões com base no activity_id."""

    def create_mission(self, activity_id: str) -> RoboticMission:
        if "CLASS" in activity_id:
            return ClassificationMission()
        elif "NAV" in activity_id:
            return NavigationMission()
        raise ValueError(f"Missão não reconhecida para activity_id: {activity_id}")

@app.route("/")
def root():
    return "WebService FRS: Online!"


@app.route("/status")
def status_check():
    return jsonify({
        "status": "OK",
        "service": "FRS Activity Provider",
        "version": "1.1"
    })

@app.route("/config", methods=["GET"])
def config_page():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Configuração - FRS</title>
        <meta charset="utf-8" />
    </head>
    <body>
        <h1>Configuração da Missão Robótica (FRS)</h1>
        <form>
            <label>Tipo de Robô (robot_type):</label><br/>
            <input type="text" name="robot_type" value="Braço Manipulador de 6 Eixos" /><br/><br/>

            <label>Número de objetos-alvo (target_objects):</label><br/>
            <input type="number" name="target_objects" value="8" /><br/><br/>

            <label>Critérios de classificação (sorting_criteria):</label><br/>
            <input type="text" name="sorting_criteria" value="cor,tamanho" /><br/><br/>

            <label>Tempo máximo de execução (max_execution_time_s):</label><br/>
            <input type="number" name="max_execution_time_s" value="150" /><br/><br/>

            <label>Linguagem de programação (programming_language):</label><br/>
            <input type="text" name="programming_language" value="Python (API RobotAPI 3.1)" /><br/><br/>

        </form>
    </body>
    </html>
    """
    return html

@app.route("/json_params", methods=["GET"])
def json_params():
    params = [
        {"name": "robot_type", "type": "text/plain"},
        {"name": "target_objects", "type": "integer"},
        {"name": "sorting_criteria", "type": "text/plain"},
        {"name": "max_execution_time_s", "type": "integer"},
        {"name": "programming_language", "type": "text/plain"}
    ]
    return jsonify(params)

@app.route("/deploy", methods=["GET"])
def deploy_activity():
    """
    A Inven!RA faz:
      GET /deploy?activityID=XXX

    O Activity Provider:
      - prepara-se para guardar analytics dessa instância
      - devolve o URL a ser usado pelos estudantes (Provide Activity - ainda não implementado)
    """
    activity_id = request.args.get("activityID")

    if not activity_id:
        return "Falta o parâmetro activityID na query string.", 400

    factory = MissionFactory()
    try:
        mission = factory.create_mission(activity_id)
    except ValueError:
        mission = ClassificationMission()  # default

    empty_config = {}
    mission.load_parameters(empty_config)
    initial_state = mission.start_simulation()

    ACTIVITY_CONFIGS[activity_id] = {
        "mission_type": mission.__class__.__name__,
        "initial_state": initial_state
    }

    ACTIVITY_ANALYTICS[activity_id] = [
        {
            "inveniraStdID": "1001",
            "quantAnalytics": [
                {"name": "Acedeu à atividade", "type": "boolean", "value": True},
                {"name": "Submissões de código", "type": "integer", "value": 0},
                {"name": "Evolução pela atividade (%)", "type": "float", "value": 0.0}
            ],
            "qualAnalytics": [
                {
                    "name": "Perfil de atividade do estudante",
                    "type": "URL",
                    "value": f"{request.host_url.rstrip('/')}/qualitative_profile?activityID={activity_id}&studentID=1001"
                }
            ]
        }
    ]

    base_url = request.host_url.rstrip("/")
    runtime_url = f"{base_url}/runtime/{activity_id}"
    return runtime_url, 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/analytics_list", methods=["GET"])
def analytics_list():
    data = {
        "qualAnalytics": [
            {"name": "Perfil de atividade do estudante", "type": "URL"}
        ],
        "quantAnalytics": [
            {"name": "Acedeu à atividade", "type": "boolean"},
            {"name": "Submissões de código", "type": "integer"},
            {"name": "Evolução pela atividade (%)", "type": "float"}
        ]
    }
    return jsonify(data)

@app.route("/analytics", methods=["POST"])
def analytics():
    """
    Pedido:
    {
      "activityID": "id_da_instancia_na_InvenIRA"
    }

    Resposta: lista com analytics de todos os estudantes dessa atividade.
    """
    data = request.get_json(force=True)
    activity_id = data.get("activityID")

    if not activity_id:
        return "Falta activityID no corpo do pedido.", 400

    analytics_data = ACTIVITY_ANALYTICS.get(activity_id)

    if analytics_data is None:
        analytics_data = [
            {
                "inveniraStdID": "1001",
                "quantAnalytics": [
                    {"name": "Acedeu à atividade", "type": "boolean", "value": False},
                    {"name": "Submissões de código", "type": "integer", "value": 0},
                    {"name": "Evolução pela atividade (%)", "type": "float", "value": 0.0}
                ],
                "qualAnalytics": [
                    {
                        "name": "Perfil de atividade do estudante",
                        "type": "URL",
                        "value": ""
                    }
                ]
            }
        ]

    return jsonify(analytics_data)

if __name__ == "__main__":
    app.run(debug=True, port=5000)

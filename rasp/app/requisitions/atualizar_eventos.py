import requests
import dateutil.parser

from app.models.eventos import Eventos, EventosSchema

from config import nome_sala_rasp, last_update_fake, API_URL

class AtualizarEventos:
    '''
    - rasp envia pro servidor o nome da sala desse rasp
    - servidor retorna a data do ultimo evento recebido (data coringa se nao houver registros)
    - rasp confere se existem novos eventos registrados depois da data em questao
    - rasp envia pro servidor todos os novos registros encontrados
    - servidor insere novos eventos
    '''
    
    def enviar():
        dados = {"sala": nome_sala_rasp}

    try:
        response = requests.post(API_URL + "/rasp/checkevento", json=dados)
        r = response.json()

        hora = dateutil.parser.parse(r["horario"])
        eventos = (
            Eventos.query
            .filter(Eventos.horario > hora)
            .all()
        )

        for e in eventos:
            adicionar = {
                "rfid": e.rfid,
                "evento": e.evento.name,
                "horario": str(e.horario),
                "sala": nome_sala_rasp
            }
            response2 = requests.post(API_URL + "/rasp/evento", json=adicionar)
            r2 = response2.json()

    except:
        pass
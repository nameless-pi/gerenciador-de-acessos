import requests
import dateutil.parser

from app.models.rfids_permitidos import RfidsPermitidos, RfidsPermitidosSchema

from config import nome_sala_rasp, last_update_fake, API_URL

class AtualizarRfid:
    '''
    - rasp busca a ultima data de um rfid cadastrado ou atualizado
    - rasp envia pro servidor o nome da sala desse rasp e a data do passo anterior (data coringa se nao houver registros)
    - servidor confere se existem novos rfids cadastrados ou modificados para essa sala depois da data em questao
    - servidor envia de volta uma lista de novos rfids, rfids modificados e rfids removidos
    - rasp insere novos rfids, modifica rfids existentes e remove rfids, se necessario
    '''

    def requisitar():
        last_update = (
            RfidsPermitidos.query
            .with_entities(RfidsPermitidos.last_update)
            .order_by(RfidsPermitidos.last_update.desc())
            .first()
        )

        # se bd vazio
        if not last_update:
            dados = {
                "last_update": last_update_fake,
                "sala": nome_sala_rasp
            }
        else:
            dados = {
                "last_update": str(last_update[0]),
                "sala": nome_sala_rasp
            }

        # post
        try:
            response = requests.post(API_URL + "/rasp/rfid", json=dados)
            r = response.json()

            # persiste
            for adicionar in r["novos"]:
                check_rfid = (
                    RfidsPermitidos.query
                    .filter(RfidsPermitidos.rfid == adicionar["rfid"])
                    .first()
                )
                if not check_rfid:
                    novo_rfid = RfidsPermitidos(
                        adicionar["rfid"],
                        adicionar["tipo"],
                        dateutil.parser.parse(adicionar["last_update"])
                    )
                    novo_rfid.add(novo_rfid)
                else:
                    if rfids_permitidos.tipo != adicionar["tipo"]:
                        rfids_permitidos.tipo = adicionar["tipo"]
                        rfids_permitidos.update()

            # remove
            for remover in r["removidos"]:
                check_rfid = (
                    RfidsPermitidos.query
                    .filter(RfidsPermitidos.rfid == remover["rfid"])
                    .first()
                )
                if check_rfid:
                    check_rfid.delete(check_rfid)

        except:
            pass
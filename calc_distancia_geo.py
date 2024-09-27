# Importa as bibliotecas necessárias
from geopy.geocoders import Nominatim
from geopy import distance
import pandas as pd
import requests

# Inicializa o geocoder Nominatim com um nome de usuário para identificação
geocoder = Nominatim(user_agent="Liga jovem app")

# Função para buscar o endereço completo a partir do CEP usando a API ViaCEP
def buscar_endereco_por_cep(cep):
    # Remove hifens e espaços do CEP para garantir que a consulta seja válida
    cep = cep.replace("-", "").replace(" ", "")
   
    # URL da API ViaCEP
    url = f"https://viacep.com.br/ws/{cep}/json/"

    # Requisição HTTP para obter os dados do endereço
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro ao consultar o CEP {cep}. Código de status HTTP: {response.status_code}")
        return None

    try:
        # Tenta converter a resposta da API para JSON
        endereco = response.json()
    except ValueError as e:  # Corrigido o erro de exceção para JSON
        print(f"Erro ao decodificar JSON para o CEP {cep}: {e}")
        print(f"Resposta recebida: {response.text}")
        return None

    # Verifica se o CEP é válido (não encontrado)
    if 'erro' in endereco:
        print(f"CEP {cep} não encontrado na API ViaCEP.")
        return None

    return endereco

# Função para obter as coordenadas (latitude e longitude) de um endereço
def obter_coordenadas(endereco):
    try:
        logradouro = endereco["logradouro"]
        cidade = endereco["localidade"]

        # Geocodificação do endereço completo para obter as coordenadas
        localizacao = geocoder.geocode(f"{logradouro}, {cidade}, Sergipe, Brazil")
        if localizacao:
            return (localizacao.latitude, localizacao.longitude)
        else:
            print(f"Não foi possível encontrar as coordenadas para o endereço: {logradouro}, {cidade}")
            return None, None
    except Exception as e:
        print(f"Erro ao obter coordenadas: {e}")
        return None, None

# Função para obter o nome do logradouro usando o endereço
def obter_nome_do_cep(endereco):
    try:
        return endereco["logradouro"]
    except KeyError:
        print("Logradouro não encontrado no endereço.")
        return None

# Função para calcular a distância usando a API do GraphHopper
def calcular_distancia_graphhopper(lat1, long1, lat2, long2, api_key):
    # URL da API do GraphHopper, configurada para retornar a rota em português brasileiro
    url = f"https://graphhopper.com/api/1/route?point={lat1},{long1}&point={lat2},{long2}&vehicle=car&locale=pt-BR&calc_points=true&key={api_key}"

    # Requisição HTTP para obter os dados da rota entre os pontos A e B
    response = requests.get(url)

    # Verifica se a requisição foi bem-sucedida
    if response.status_code != 200:
        print(f"Erro ao consultar o GraphHopper. Código de status HTTP: {response.status_code} - {response.text}")
        return None, None

    try:
        dados = response.json()
        if "paths" not in dados or len(dados["paths"]) == 0:
            print("Erro: resposta da API não contém dados de caminho válidos.")
            return None, None

        caminho = dados["paths"][0]
        distancia_km = caminho["distance"] / 1000  # Conversão de metros para quilômetros
        duracao_min = caminho["time"] / 60000  # Conversão de milissegundos para minutos
        return distancia_km, duracao_min
    except (IndexError, KeyError, ValueError) as e:
        print(f"Erro ao processar a resposta da API do GraphHopper: {e}")
        return None, None

# Função para calcular a distância geodésica entre dois pontos usando geopy
def calcular_distancia_geodesica(coord1, coord2):
    return distance.distance(coord1, coord2).km

# Função principal para coordenar todo o processo
def main():
    # Definição do CEP de origem
    cep_origem = "49010-050"

    # Lista de CEPs de destino (corrigida com separadores adequados)
    ceps_destino = [
        "49025-020", "49055-110", "49047-040", "49097-670", "49025-040", "49039-712", "49039-100", "49095-786",
        "49089-249", "49092-125", "49025-750", "49001-231", "49000-626", "49050-100", "49044-000", "49043-472",
        "49043-847", "49039-000", "49040-970", "49060-200", "49090-550", "49048-520", "49027-190", "49035-170",
        "49036-170", "49035-110", "49097-563", "49069-135", "49025-530", "49004-021", "49043-484", "49080-130",
        "49080-135", "49096-020", "49095-780", "49072-730", "49003-250", "49092-490", "49097-310", "49000-593",
    ]

    # Busca o endereço completo do CEP de origem usando a API ViaCEP
    endereco_origem = buscar_endereco_por_cep(cep_origem)

    if endereco_origem is None:
        print(f"Não foi possível encontrar o endereço para o CEP de origem: {cep_origem}")
        return

    # Obtem as coordenadas (latitude e longitude) do endereço de origem
    lat_origem, long_origem = obter_coordenadas(endereco_origem)
    
    if lat_origem is None or long_origem is None:
        print(f"Não foi possível obter as coordenadas para o CEP de origem: {cep_origem}")
        return

    # Obtém o nome do logradouro do CEP de origem
    nome_origem = obter_nome_do_cep(endereco_origem)
    print(f"Nome do logradouro para o CEP de origem {cep_origem}: {nome_origem}")

    # Chave de API do GraphHopper (deve ser armazenada de maneira segura)
    api_key = "a330129f-1eee-43dd-8e18-a04a5f8e54bc"

    df = {"CEP Destino": [], "Logradouro": [], "Distância GrapHopper": [], "Distância GEO": [], "Duração": []}
    
    # Itera sobre cada CEP de destino para calcular a distância
    for cep_destino in ceps_destino:
        endereco_destino = buscar_endereco_por_cep(cep_destino)

        # Verifica se o endereço de destino foi encontrado
        if endereco_destino is None:
            print(f"Não foi possível encontrar o endereço para o CEP de destino: {cep_destino}")
            continue

        # Obtem as coordenadas (latitude e longitude) do endereço de destino
        lat_destino, long_destino = obter_coordenadas(endereco_destino)

        if lat_destino is None or long_destino is None:
            print(f"Não foi possível obter as coordenadas para o CEP de destino: {cep_destino}")
            continue

        # Obtém o nome do logradouro do CEP de destino
        nome_destino = obter_nome_do_cep(endereco_destino)
        print(f"Nome do logradouro para o CEP de destino {cep_destino}: {nome_destino}")

        # Calcula a distância usando a API do GraphHopper
        distancia_km, duracao_min = calcular_distancia_graphhopper(lat_origem, long_origem, lat_destino, long_destino, api_key)
        if distancia_km is not None:
            print(f"Distância real (GraphHopper) entre {cep_origem} e {cep_destino}: {distancia_km:.2f} km em {duracao_min:.0f} mins")
        else:
            print(f"Não foi possível calcular a distância real entre {cep_origem} e {cep_destino} usando o GraphHopper.")

        # Calcula a distância geodésica entre os pontos
        distancia_geo = calcular_distancia_geodesica((lat_origem, long_origem), (lat_destino, long_destino))


        print(f"Distância geodésica entre {cep_origem} e {cep_destino}: {distancia_geo:.2f} km")

# Executa o programa
if _name_ == "_main_":
    main()

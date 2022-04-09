# Especificação

## 1. Usuário

Usuário é toda pessoa física que interage com a plataforma. Estes podem ser anônimos ou registrados. Somente usuários registrados podem realizar solicitações de serviços e somente estes podem solicitar serviços. 

Atributos do modelo: 

- Nome 
- E-mail 
- Telefone
- Instituição
- Cargo


## 2. Serviço

Serviços são as opções de consumo que o usuário possui na plataforma.

Atributos do modelo: 

- Solicitante: Usuário que realizou a solicitação do serviço 
- Data da solicitação: Data em que a solicitação foi realizada 
- Data de conclusão: Data em que a solicitação foi concluída 
- Status: [ Aguardando pagamento ; Aguardando processamento ; Processando ; Concluído ]
- Tipo de serviço: [ Dosimetria clínica; Dosimetria pré-clínica ; Segmentação,  Radiosinoviorteses ; Modelagem Computacional ] 
- Preço: Valor cobrado pelo serviço
- Link para o relatório: URL para o relatório da solicitação
- Informações técnicas: Toda informação necessária para a geração do relatório. Específico ao tipo do serviço
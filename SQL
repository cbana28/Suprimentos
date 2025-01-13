CREATE DATABASE gestao_suprimentos;

USE gestao_suprimentos;

/*
Administrador: Cadastrar Usuários (Controlar quem pode acessar o sistema),
Definir níveis de acesso (Controlar o que cada usuário pode acessar)

Usuário Padrão: Cadastrar itens recebidos de modo padronizado (Material de Consumo/Controlar recebimento),
Cadastrar itens distribuídos de modo padronizado (Material de Consumo/Controlar entrega)

Gestor: Consultar estoque; Consultar custo por setor (Realizar a gestão do processo)
*/

-- Tabela de usuários
CREATE TABLE ac_usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100),
    nivel_acesso ENUM('Administrador', 'Usuário Padrão', 'Gestor'),
    login VARCHAR(50),
    senha VARCHAR(255),
    status ENUM('Ativo','Inativo'),
    limite_aprovacao FLOAT,
    centro_custo VARCHAR(50)
);

-- Tabela de itens
CREATE TABLE ac_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    descricao_item VARCHAR(255),
    valor_unitario FLOAT
/*
 DEMAIS CARACTERISTICAS DO ITEM/PRODUTO/SERVIÇO
 -unidade de medida
 -parametros
 -etc
*/

);

-- Tabela de controle de estoque
CREATE TABLE ac_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    local_estocado VARCHAR(60),
    quantidade_atual INT,
    FOREIGN KEY (item_id) REFERENCES ac_item(id)
);

-- Tabela de movimentações de estoque (controle de entradas e saídas)
CREATE TABLE ac_movimentacoes_estoque (
    id INT AUTO_INCREMENT PRIMARY KEY,
    item_id INT,
    usuario_id INT,
    tipo_movimentacao ENUM('entrada', 'saida'),
    quantidade INT,
    data_movimentacao DATE,
    local_estocado VARCHAR(60),
    valor_movimentacao FLOAT,
    FOREIGN KEY (item_id) REFERENCES ac_item(id),
    FOREIGN KEY (usuario_id) REFERENCES ac_usuarios(id)
);

/*
CREATE TABLE ac_local (....)
para definir melhor as informações dos centros de custos 
e suas localizações bem como o local onde esta estocado 

*/
# -*- coding: utf-8 -*-
# -------------------------------------------------------------------------
# This is a sample controller
# this file is released under public domain and you can use without limitations
# -------------------------------------------------------------------------

# ---- example index page ----
def index():
    """
    Redireciona para a página de login.
    """
    redirect(URL('default', 'login'))  # Redireciona para a página de login

def adm():
    return dict()

# ---- API (example) -----
@auth.requires_login()
def api_get_user_email():
    if not request.env.request_method == 'GET': raise HTTP(403)
    return response.json({'status':'success', 'email':auth.user.email})

# ---- Smart Grid (example) -----
@auth.requires_membership('admin') # can only be accessed by members of admin groupd
def grid():
    response.view = 'generic.html' # use a generic view
    tablename = request.args(0)
    if not tablename in db.tables: raise HTTP(403)
    grid = SQLFORM.smartgrid(db[tablename], args=[tablename], deletable=False, editable=False)
    return dict(grid=grid)

# ---- Embedded wiki (example) ----
def wiki():
    auth.wikimenu() # add the wiki to the menu
    return auth.wiki() 

# ---- Action for login/register/etc (required for auth) -----
def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())

# ---- action to server uploaded static content (required) ---
@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)

#################################
#################################
#################################
id_usuario = 0
def cadastro_usuario():
    """
    Função para cadastrar novos usuários no sistema.
    """
    form = SQLFORM(db.ac_usuarios)

    if form.process().accepted:
        response.flash = 'Usuário cadastrado com sucesso!'
    elif form.errors:
        response.flash = 'O formulário contém erros, por favor verifique.'

    # Renderiza a página com o formulário
    return dict(form=form)

################################
def cadastro_item():
    """
    Função para cadastrar novos itens no sistema.
    """
    form = SQLFORM(db.ac_item)

    if form.process().accepted:
        response.flash = 'Item cadastrado com sucesso!'
    elif form.errors:
        response.flash = 'O formulário contém erros, por favor verifique.'

    # Renderiza a página com o formulário
    return dict(form=form)

################################

def validar_movimentacao(form):
    item_id = form.vars.item_id  # ID do item movimentado
    quantidade = form.vars.quantidade  # Quantidade movimentada
    local_saida = form.vars.local_saida  # Local de onde o item está saindo

    # Se o local de saída não for "Nenhum (Compra)", verificar o estoque
    if local_saida != 'Nenhum (Compra)':
        estoque_saida = db((db.ac_estoque.item_id == item_id) & 
                           (db.ac_estoque.local_estocado == local_saida)).select().first()

        if not estoque_saida:
            form.errors.local_saida = 'Erro: item não encontrado no estoque de origem.'
        elif estoque_saida.quantidade_atual < quantidade:
            form.errors.quantidade = 'Erro: quantidade insuficiente no estoque de origem para essa saída.'


def cadastro_movimentacao():
    """
    Função para cadastrar movimentações de estoque e atualizar o estoque automaticamente.
    """

    # Define o validador para mostrar a descrição do item e o nome do usuário
    db.ac_movimentacoes_estoque.item_id.requires = IS_IN_DB(db, 'ac_item.id', '%(descricao_item)s', zero='Selecione um item')
    db.ac_movimentacoes_estoque.usuario_id.requires = IS_IN_DB(db, 'ac_usuarios.id', '%(nome)s', zero='Selecione um usuário')

    # Cria o formulário com as representações corretas
    form = SQLFORM(db.ac_movimentacoes_estoque)

    if form.process(onvalidation=validar_movimentacao).accepted:  # Use onvalidation para fazer validações antes de aceitar
        item_id = form.vars.item_id  # ID do item movimentado
        quantidade = form.vars.quantidade  # Quantidade movimentada
        local_saida = form.vars.local_saida  # Local de onde o item está saindo
        local_chegada = form.vars.local_chegada  # Local para onde o item está indo
        valor_movimentacao = form.vars.valor_movimentacao  # Valor total da movimentação

        # Atualiza o estoque do local de saída (subtrair)
        if local_saida != 'Nenhum (Compra)':  # Se for compra, não subtraímos de nenhum local
            estoque_saida = db((db.ac_estoque.item_id == item_id) & 
                               (db.ac_estoque.local_estocado == local_saida)).select().first()
            
            if estoque_saida:
                # Subtrai a quantidade do estoque de saída
                novo_estoque_saida = estoque_saida.quantidade_atual - quantidade
                # Subtrai o valor total da movimentação do estoque de saída
                novo_valor_total_saida = estoque_saida.valor_total - valor_movimentacao
                # Atualiza o registro do estoque
                estoque_saida.update_record(quantidade_atual=novo_estoque_saida, valor_total=novo_valor_total_saida)

        # Atualiza o estoque do local de chegada (adicionar)
        if local_chegada != 'Externo (Venda)':  # Se for venda externa, não adicionamos a nenhum local
            estoque_chegada = db((db.ac_estoque.item_id == item_id) & 
                                 (db.ac_estoque.local_estocado == local_chegada)).select().first()
            
            if estoque_chegada:
                # Adiciona a quantidade ao estoque de chegada
                novo_estoque_chegada = estoque_chegada.quantidade_atual + quantidade
                # Adiciona o valor total da movimentação ao estoque de chegada
                novo_valor_total_chegada = estoque_chegada.valor_total + valor_movimentacao
                # Atualiza o registro do estoque
                estoque_chegada.update_record(quantidade_atual=novo_estoque_chegada, valor_total=novo_valor_total_chegada)
            else:
                # Se o item não está no estoque de chegada, cria um novo registro
                db.ac_estoque.insert(item_id=item_id, 
                                     local_estocado=local_chegada, 
                                     quantidade_atual=quantidade,
                                     valor_total=valor_movimentacao)

        response.flash = 'Movimentação registrada e estoque atualizado com sucesso!'
    elif form.errors:
        response.flash = 'O formulário contém erros. Verifique os dados e tente novamente.'

    return dict(form=form)



################################
def lista_usuarios():
    """
    Função para listar os usuários cadastrados com links para editar.
    """
    # Seleciona todos os registros da tabela ac_usuarios
    usuarios = db(db.ac_usuarios).select()

    # Cria links de edição para cada usuário
    # O link de edição vai chamar a função 'editar_usuario' com o ID do usuário como argumento
    links_editar = [A('Editar', _href=URL('editar_usuario', args=[usuario.id])) for usuario in usuarios]

    # Retorna os dados dos usuários e os links de edição para serem renderizados na view
    return dict(usuarios=usuarios, links_editar=links_editar)

def editar_usuario():
    """
    Função para editar um usuário específico.
    """
    # O ID do usuário a ser editado é passado como argumento
    usuario_id = request.args(0) or redirect(URL('lista_usuarios'))

    # Busca o registro do usuário com o ID fornecido
    usuario = db.ac_usuarios(usuario_id) or redirect(URL('lista_usuarios'))

    # Cria o formulário de edição com base no registro do usuário
    form = SQLFORM(db.ac_usuarios, usuario, showid=False)

    if form.process().accepted:
        response.flash = 'Usuário atualizado com sucesso!'
        redirect(URL('lista_usuarios'))  # Redireciona de volta para a lista de usuários
    elif form.errors:
        response.flash = 'O formulário contém erros. Por favor, verifique.'

    return dict(form=form)


################################

def lista_itens():
    """
    Função para listar os itens cadastrados com links para editar.
    """
    # Seleciona todos os registros da tabela ac_item
    itens = db(db.ac_item).select()

    # Cria links de edição para cada item
    # O link de edição vai chamar a função 'editar_item' com o ID do item como argumento
    links_editar = [A('Editar', _href=URL('editar_item', args=[item.id])) for item in itens]

    # Retorna os dados dos itens e os links de edição para serem renderizados na view
    return dict(itens=itens, links_editar=links_editar)


def editar_item():
    """
    Função para editar um item específico.
    """
    # O ID do item a ser editado é passado como argumento
    item_id = request.args(0) or redirect(URL('listar_itens'))

    # Busca o registro do item com o ID fornecido (retorna o objeto de registro, não uma tupla)
    item = db.ac_item(item_id) or redirect(URL('listar_itens'))

    # Cria o formulário de edição com base no registro do item
    form = SQLFORM(db.ac_item, item, showid=False)

    if form.process().accepted:
        response.flash = 'Item atualizado com sucesso!'
        redirect(URL('lista_itens'))  # Redireciona de volta para a lista de itens
    elif form.errors:
        response.flash = 'O formulário contém erros. Por favor, verifique.'

    return dict(form=form)

###############################
######Estoque
import locale
locale.setlocale(locale.LC_ALL, '')  # Define a localidade para a formatação de números

def dashboard():
    """
    Função para exibir os valores do estoque na página do dashboard.
    """

    # Seleciona todos os registros da tabela ac_estoque
    # Inclui os dados do item (como descrição) da tabela ac_item através de uma junção
    estoque = db(db.ac_estoque).select(
        db.ac_estoque.ALL, 
        db.ac_item.descricao_item,  # Inclui a descrição do item
        join=db.ac_item.on(db.ac_estoque.item_id == db.ac_item.id)
    )

    # Passa os dados do estoque para a view
    return dict(estoque=estoque)

###############################
def listar_movimentacoes():
    """
    Função para listar as movimentações de estoque com links para editar.
    """
    # Seleciona todas as movimentações da tabela ac_movimentacoes_estoque
    movimentacoes = db(db.ac_movimentacoes_estoque).select()

    # Cria links de edição para cada movimentação
    links_editar = [A('Editar', _href=URL('editar_movimentacao', args=[mov.id])) for mov in movimentacoes]

    # Retorna os dados das movimentações e os links de edição
    return dict(movimentacoes=movimentacoes, links_editar=links_editar)

def editar_movimentacao():
    """
    Função para editar uma movimentação de estoque e atualizar o estoque automaticamente.
    """
    # O ID da movimentação a ser editada é passado como argumento
    movimentacao_id = request.args(0) or redirect(URL('listar_movimentacoes'))

    # Busca o registro da movimentação com o ID fornecido
    movimentacao = db.ac_movimentacoes_estoque(movimentacao_id) or redirect(URL('listar_movimentacoes'))

    # Cria o formulário de edição com base no registro da movimentação
    form = SQLFORM(db.ac_movimentacoes_estoque, movimentacao, showid=False)

    if form.process().accepted:
        # Pegando os valores antigos (antes da edição)
        quantidade_anterior = movimentacao.quantidade
        local_saida_anterior = movimentacao.local_saida
        local_chegada_anterior = movimentacao.local_chegada
        item_id_anterior = movimentacao.item_id
        valor_movimentacao_anterior = movimentacao.valor_movimentacao

        # Pegando os novos valores (depois da edição)
        item_id = form.vars.item_id  # ID do item movimentado
        quantidade = form.vars.quantidade  # Quantidade movimentada
        local_saida = form.vars.local_saida  # Local de onde o item está saindo
        local_chegada = form.vars.local_chegada  # Local para onde o item está indo
        valor_movimentacao = form.vars.valor_movimentacao  # Valor total da movimentação

        # Verificar se o item ou a quantidade mudou e ajustar o estoque
        if local_saida_anterior != 'Nenhum (Compra)':  # Subtrair a quantidade anterior do estoque de saída
            estoque_saida = db((db.ac_estoque.item_id == item_id_anterior) & 
                               (db.ac_estoque.local_estocado == local_saida_anterior)).select().first()
            if estoque_saida:
                # Devolver ao estoque a quantidade antiga e o valor da movimentação antiga
                estoque_saida.update_record(
                    quantidade_atual=estoque_saida.quantidade_atual + quantidade_anterior,
                    valor_total=estoque_saida.valor_total + valor_movimentacao_anterior
                )

        # Subtrair a nova quantidade do estoque do novo local de saída
        if local_saida != 'Nenhum (Compra)':
            estoque_saida = db((db.ac_estoque.item_id == item_id) & 
                               (db.ac_estoque.local_estocado == local_saida)).select().first()
            if estoque_saida:
                estoque_saida.update_record(
                    quantidade_atual=estoque_saida.quantidade_atual - quantidade,
                    valor_total=estoque_saida.valor_total - valor_movimentacao
                )

        # Atualizar o estoque do local de chegada antigo (reverter a quantidade anterior)
        if local_chegada_anterior != 'Externo (Venda)':  # Adicionar a quantidade anterior de volta ao estoque
            estoque_chegada = db((db.ac_estoque.item_id == item_id_anterior) & 
                                 (db.ac_estoque.local_estocado == local_chegada_anterior)).select().first()
            if estoque_chegada:
                estoque_chegada.update_record(
                    quantidade_atual=estoque_chegada.quantidade_atual - quantidade_anterior,
                    valor_total=estoque_chegada.valor_total - valor_movimentacao_anterior
                )

        # Atualizar o estoque com a nova quantidade e o novo local de chegada
        if local_chegada != 'Externo (Venda)':
            estoque_chegada = db((db.ac_estoque.item_id == item_id) & 
                                 (db.ac_estoque.local_estocado == local_chegada)).select().first()
            if estoque_chegada:
                estoque_chegada.update_record(
                    quantidade_atual=estoque_chegada.quantidade_atual + quantidade,
                    valor_total=estoque_chegada.valor_total + valor_movimentacao
                )
            else:
                # Se o item não está no estoque de chegada, cria um novo registro
                db.ac_estoque.insert(item_id=item_id, 
                                     local_estocado=local_chegada, 
                                     quantidade_atual=quantidade,
                                     valor_total=valor_movimentacao)

        response.flash = 'Movimentação atualizada e estoque corrigido com sucesso!'
        redirect(URL('listar_movimentacoes'))  # Redireciona para a lista de movimentações
    elif form.errors:
        response.flash = 'O formulário contém erros. Verifique os dados e tente novamente.'

    return dict(form=form)




################################
def login():
    form = SQLFORM.factory(
        Field('login', requires=IS_NOT_EMPTY()),
        Field('senha', 'password', requires=IS_NOT_EMPTY())
    )

    # Verifica se o formulário foi enviado
    if form.process().accepted:
        login_usuario = form.vars.login
        senha_entrada = form.vars.senha
        

        # Buscar usuário pelo login
        usuario = db(db.ac_usuarios.login == login_usuario).select().first()
        
        if usuario:
            # Criptografar a senha de entrada
            crypt = CRYPT()  # Instanciando o objeto CRYPT
            senha_criptografada_entrada = crypt(senha_entrada)[0]  # Criptografa a senha

            # Verificar se a senha criptografada da entrada é igual à senha armazenada no banco de dados
            if senha_criptografada_entrada == usuario.senha:
                # Verificar se o usuário está "Ativo"
                if usuario.status != 'Ativo':
                    response.flash = 'Usuário inativo. Entre em contato com o administrador.'
                else:
                    # Se o login for bem-sucedido, verificar o nível de acesso e redirecionar
                    if usuario.nivel_acesso == 'Administrador':
                        redirect(URL('default', 'adm'))
                    elif usuario.nivel_acesso == 'Usuário Padrão':
                        redirect(URL('default', 'cadastro_movimentacao'))
                    elif usuario.nivel_acesso == 'Gestor':
                        redirect(URL('default', 'dashboard'))
            else:
                response.flash = 'Senha incorreta.'
        else:
            response.flash = 'Usuário não encontrado.'

    return dict(form=form)


